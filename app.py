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

        # Run self-consistency with chain-of-thought
        samples, final_answer, weighted_confidence, llm_confidence, agreement_confidence, summary = sc_engine.run_self_consistency(
            prompt=req.prompt,
            num_samples=req.num_self_consistency,
            num_cot_steps=req.num_cot
        )

        # Get the primary chain-of-thought (from the first sample for consistency)
        primary_cot = samples[0].reasoning_path if samples else []

        # Build response
        response = AgenticResponse(
            prompt=req.prompt,
            model_used=model_name,
            chain_of_thought=primary_cot,
            self_consistency_samples=samples,
            final_answer=final_answer,
            confidence_score=weighted_confidence,
            llm_confidence=llm_confidence,
            agreement_confidence=agreement_confidence,
            reasoning_summary=summary
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """
    Alternative endpoint with chat-style interface

    Request body:
    {
        "messages": [{"role": "user", "content": "Your question"}],
        "num_self_consistency": 5,
        "num_cot": 3,
        "model": "fast",
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        # Extract prompt from messages
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"error": "messages field is required"}), 400

        # Get the last user message as the prompt
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            return jsonify({"error": "No user message found"}), 400

        prompt = user_messages[-1].get("content", "")

        # Create request with prompt from messages
        request_data = {
            "prompt": prompt,
            "num_self_consistency": data.get("num_self_consistency", 5),
            "num_cot": data.get("num_cot", 3),
            "model": data.get("model", "fast"),
            "temperature": data.get("temperature", 0.7)
        }

        try:
            req = AgenticRequest(**request_data)
        except ValidationError as e:
            return jsonify({"error": "Invalid request", "details": e.errors()}), 400

        # Get model name
        model_name = get_model_name(req.model)

        # Initialize and run self-consistency
        sc_engine = SelfConsistencyEngine(
            model_name=model_name,
            temperature=req.temperature
        )

        samples, final_answer, weighted_confidence, llm_confidence, agreement_confidence, summary = sc_engine.run_self_consistency(
            prompt=req.prompt,
            num_samples=req.num_self_consistency,
            num_cot_steps=req.num_cot
        )

        primary_cot = samples[0].reasoning_path if samples else []

        # Build response in chat format
        response = {
            "id": "chatcmpl-agentic",
            "object": "chat.completion",
            "created": 1234567890,
            "model": model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": final_answer
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(final_answer.split()),
                "total_tokens": len(prompt.split()) + len(final_answer.split())
            },
            "agentic_metadata": {
                "chain_of_thought": [step.model_dump() for step in primary_cot],
                "self_consistency_samples": [s.model_dump() for s in samples],
                "confidence_score": weighted_confidence,
                "llm_confidence": llm_confidence,
                "agreement_confidence": agreement_confidence,
                "reasoning_summary": summary
            }
        }

        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Error processing chat request: {str(e)}")
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
