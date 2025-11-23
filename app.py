from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import AgenticRequest, AgenticResponse
from self_consistency import SelfConsistencyEngine
from cot_engine import ChainOfThoughtEngine
from pydantic import ValidationError
from pdf_extractor import extract_text_from_pdf, get_pdf_info
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

    Supports two request formats:

    1. JSON (application/json):
    {
        "prompt": "Your question here",
        "system_prompt": "Optional system instructions and context" (optional),
        "num_self_consistency": 5,
        "num_cot": 3,
        "model": "fast",
        "temperature": 0.7
    }

    2. Form-data with optional PDF (multipart/form-data):
    - prompt: text (optional if PDF is provided)
    - system_prompt: text (optional system instructions and context)
    - pdf_file: file (optional PDF upload)
    - num_self_consistency: number (default: 5)
    - num_cot: number (default: 3)
    - model: text (default: "fast")
    - temperature: number (default: 0.7)
    """
    try:
        pdf_text = None
        pdf_info = None

        # Check if this is a multipart/form-data request (PDF upload)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle form-data with optional PDF
            pdf_file = request.files.get('pdf_file')

            # Extract text from PDF if provided
            if pdf_file and pdf_file.filename:
                try:
                    pdf_text = extract_text_from_pdf(pdf_file)
                    # Reset file pointer for metadata extraction
                    pdf_file.stream.seek(0)
                    pdf_info = get_pdf_info(pdf_file)
                except ValueError as e:
                    return jsonify({"error": f"PDF extraction failed: {str(e)}"}), 400

            # Get other form fields
            data = {
                "prompt": request.form.get('prompt', ''),
                "system_prompt": request.form.get('system_prompt'),  # Optional field
                "num_self_consistency": int(request.form.get('num_self_consistency', 5)),
                "num_cot": int(request.form.get('num_cot', 3)),
                "model": request.form.get('model', 'fast'),
                "temperature": float(request.form.get('temperature', 0.7))
            }

            # Combine PDF text with prompt if PDF was provided
            if pdf_text:
                original_prompt = data.get("prompt", "")
                if original_prompt:
                    data["prompt"] = f"PDF Content:\n{pdf_text}\n\nQuestion: {original_prompt}"
                else:
                    data["prompt"] = f"PDF Content:\n{pdf_text}\n\nQuestion: Please analyze this document."
        else:
            # Handle JSON request
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body must be JSON or form-data"}), 400

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
            num_cot_steps=req.num_cot,
            system_prompt=req.system_prompt
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

        # Convert to dict and add PDF info if present
        response_dict = response.model_dump()
        if pdf_info:
            response_dict['pdf_info'] = pdf_info

        return jsonify(response_dict), 200

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
