from flask import Flask, request, jsonify
from config import Config
from models import AgenticRequest, AgenticResponse
from self_consistency import SelfConsistencyEngine
from cot_engine import ChainOfThoughtEngine
from pydantic import ValidationError
import traceback

app = Flask(__name__)

# Validate configuration on startup
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please set OPENAI_API_KEY in your .env file")
    exit(1)


def get_model_name(model_type: str) -> str:
    """Get the actual model name based on fast/slow selection"""
    if model_type == "slow":
        return Config.SLOW_MODEL
    else:
        return Config.FAST_MODEL


def calculate_cost(token_usage: dict, model_name: str) -> dict:
    """
    Calculate cost based on token usage and model

    Args:
        token_usage: Dictionary with prompt_tokens, completion_tokens, total_tokens
        model_name: Name of the model used

    Returns:
        Dictionary with cost breakdown
    """
    # Azure OpenAI pricing (per 1M tokens)
    if 'gpt-4o-mini' in model_name.lower():
        # GPT-4o-mini-0718 Global
        input_price = 0.20844
        output_price = 0.8338
        pricing_model = "GPT-4o-mini-0718 Global"
    elif 'gpt-4o' in model_name.lower():
        # GPT-4o-2024-1120 Regional
        input_price = 4.20339
        output_price = 16.8136
        pricing_model = "GPT-4o-2024-1120 Regional"
    else:
        # Default to gpt-4o-mini pricing
        input_price = 0.20844
        output_price = 0.8338
        pricing_model = "GPT-4o-mini-0718 Global (default)"

    prompt_tokens = token_usage.get('prompt_tokens', 0)
    completion_tokens = token_usage.get('completion_tokens', 0)

    input_cost = (prompt_tokens / 1_000_000) * input_price
    output_cost = (completion_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost

    return {
        "input_cost": round(input_cost, 8),
        "output_cost": round(output_cost, 8),
        "total_cost": round(total_cost, 8),
        "currency": "CAD",
        "pricing_model": pricing_model,
        "input_price_per_1m": input_price,
        "output_price_per_1m": output_price
    }


@app.route("/")
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Agentic AI with Self-Consistency and Chain-of-Thought",
        "version": "1.0.0"
    })


@app.route("/v1/completions", methods=["POST"])
def completions():
    """
    OpenAI-compatible endpoint for agentic completions with CoT and self-consistency

    Request body:
    {
        "prompt": "Your question here",
        "num_self_consistency": 5,  // Number of reasoning paths (1-15)
        "num_cot": 3,  // Number of CoT steps per path (1-10)
        "model": "fast",  // "fast" or "slow"
        "temperature": 0.7  // Optional, 0.0-2.0
    }
    """
    try:
        # Parse and validate request
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        try:
            req = AgenticRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Invalid request", "details": e.errors()}), 400

        # Get model name
        model_name = get_model_name(req.model)

        # Initialize self-consistency engine
        sc_engine = SelfConsistencyEngine(
            model_name=model_name,
            temperature=req.temperature
        )

        # Run self-consistency with chain-of-thought and reflection
        (samples, preliminary_answer, final_answer, reflection_reasoning,
         weighted_confidence, llm_confidence, agreement_confidence,
         reflection_confidence, summary, token_usage, timing) = sc_engine.run_self_consistency(
            prompt=req.prompt,
            num_samples=req.num_self_consistency,
            num_cot_steps=req.num_cot
        )

        # Get the primary chain-of-thought (from the first sample for consistency)
        primary_cot = samples[0].reasoning_path if samples else []

        # Calculate cost
        cost_analysis = calculate_cost(token_usage, model_name)

        # Build response
        response = AgenticResponse(
            prompt=req.prompt,
            model_used=model_name,
            chain_of_thought=primary_cot,
            self_consistency_samples=samples,
            preliminary_answer=preliminary_answer,
            final_answer=final_answer,
            confidence_score=reflection_confidence / 100.0,  # Use reflection confidence as primary (convert to 0-1 scale)
            llm_confidence=llm_confidence,
            agreement_confidence=agreement_confidence,
            reflection_reasoning=reflection_reasoning,
            reflection_confidence=reflection_confidence,
            reasoning_summary=summary,
            token_usage=token_usage,
            cost_analysis=cost_analysis,
            timing=timing
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print(f"Starting Agentic AI API on port {Config.FLASK_PORT}")
    print(f"Fast model: {Config.FAST_MODEL}")
    print(f"Slow model: {Config.SLOW_MODEL}")
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
