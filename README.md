# Agentic AI API with Self-Consistency and Chain-of-Thought

A Flask-based API that implements advanced reasoning techniques using LangChain, including:
- **Chain-of-Thought (CoT)** reasoning: Break down complex problems into logical steps
- **Self-Consistency**: Generate multiple reasoning paths and select the most consistent answer
- **Model Selection**: Choose between fast (GPT-3.5) and slow (GPT-4) models

## Features

- OpenAI-compatible API endpoints
- Configurable chain-of-thought reasoning steps
- Configurable self-consistency sample count
- Confidence scoring based on answer agreement
- Support for both fast and slow models
- Detailed reasoning paths in responses

## Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd Agentic-AI-assessment
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-api-key-here
FAST_MODEL=gpt-3.5-turbo
SLOW_MODEL=gpt-4-turbo-preview
FLASK_PORT=5000
FLASK_DEBUG=False
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:5000`

To view logs:
```bash
docker-compose logs -f
```

To stop the container:
```bash
docker-compose down
```

### Option 2: Local Python Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Agentic-AI-assessment
```

2. Create a virtual environment:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-api-key-here
FAST_MODEL=gpt-3.5-turbo
SLOW_MODEL=gpt-4-turbo-preview
FLASK_PORT=5000
FLASK_DEBUG=True
```

## Usage

### Starting the Server

**With Docker:**
```bash
docker-compose up -d
```

**Without Docker:**
```bash
python app.py
# Or use the startup script with environment checks:
python run.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### 1. `/v1/completions` (POST)

Main endpoint for agentic completions with CoT and self-consistency.

**Request:**
```json
{
  "prompt": "What is the capital of France and why is it historically important?",
  "num_self_consistency": 5,
  "num_cot": 3,
  "model": "fast",
  "temperature": 0.7
}
```

**Parameters:**
- `prompt` (required): Your question or prompt
- `num_self_consistency` (optional, default: 5): Number of independent reasoning paths (1-15)
- `num_cot` (optional, default: 3): Number of chain-of-thought steps per path (1-10)
- `model` (optional, default: "fast"): "fast" for GPT-4o-mini or "slow" for GPT-4
- `temperature` (optional, default: 0.7): Response randomness (0.0-2.0)

**Response:**
```json
{
  "prompt": "What is the capital of France...",
  "model_used": "gpt-4o-mini",
  "chain_of_thought": [
    {
      "step_number": 1,
      "reasoning": "First, we need to identify the capital city...",
      "intermediate_conclusion": "Paris is the capital of France"
    },
    ...
  ],
  "self_consistency_samples": [
    {
      "sample_number": 1,
      "reasoning_path": [...],
      "final_answer": "Paris is the capital..."
    },
    ...
  ],
  "final_answer": "Paris is the capital of France...",
  "confidence_score": 0.95,
  "reasoning_summary": "Generated 5 independent reasoning paths. Consistency score: 95%"
}
```

#### 2. `/v1/chat/completions` (POST)

Alternative chat-style endpoint compatible with OpenAI's chat format.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Explain quantum computing in simple terms"}
  ],
  "num_self_consistency": 5,
  "num_cot": 3,
  "model": "fast",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "id": "chatcmpl-agentic",
  "object": "chat.completion",
  "model": "gpt-4o-mini",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Quantum computing is..."
    },
    "finish_reason": "stop"
  }],
  "agentic_metadata": {
    "chain_of_thought": [...],
    "self_consistency_samples": [...],
    "confidence_score": 0.92,
    "reasoning_summary": "..."
  }
}
```

#### 3. `/` (GET)

Health check endpoint.

## Python Client Example

```python
import requests

url = "http://localhost:5000/v1/completions"

request_data = {
    "prompt": "If I have 5 apples and give away 2, then buy 3 more, how many do I have?",
    "num_self_consistency": 5,
    "num_cot": 3,
    "model": "fast",
    "temperature": 0.7
}

response = requests.post(url, json=request_data)
result = response.json()

print("Final Answer:", result["final_answer"])
print("Confidence:", result["confidence_score"])
print("\nReasoning Steps:")
for step in result["chain_of_thought"]:
    print(f"Step {step['step_number']}: {step['reasoning']}")
```

See `test_client.py` for a complete working example.

## Architecture

### Components

1. **app.py**: Flask application with API endpoints
2. **config.py**: Configuration management and environment variables
3. **models.py**: Pydantic models for request/response validation
4. **cot_engine.py**: Chain-of-thought reasoning implementation
5. **self_consistency.py**: Self-consistency mechanism with multiple reasoning paths

### How It Works

1. **Request Validation**: Incoming requests are validated using Pydantic models
2. **Model Selection**: Based on the "fast" or "slow" parameter, the appropriate LLM is selected
3. **Self-Consistency Generation**:
   - Multiple independent reasoning paths are generated
   - Each path uses chain-of-thought to break down the problem
4. **Chain-of-Thought**:
   - Each reasoning path is broken into N steps
   - Each step builds on previous steps
   - Steps include reasoning and intermediate conclusions
5. **Answer Aggregation**:
   - All reasoning paths produce final answers
   - The most consistent answer is selected
   - Confidence score is calculated based on agreement
6. **Response**: Detailed response includes all reasoning paths, final answer, and confidence

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FAST_MODEL`: Model for "fast" mode (default: gpt-4o-mini)
- `SLOW_MODEL`: Model for "slow" mode (default: gpt-4)
- `FLASK_PORT`: Port to run the server on (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: True)

### Limits

- Max chain-of-thought steps: 10
- Max self-consistency samples: 15
- Temperature range: 0.0 - 2.0

## Testing

Run the test client:

**Without Docker:**
```bash
python test_client.py
```

**With Docker:**
```bash
# Install requests in your local environment first
pip install requests

# Then run the test client against the containerized API
python test_client.py
```

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Invalid request (validation error)
- 500: Internal server error

Error responses include details:
```json
{
  "error": "Invalid request",
  "details": [...]
}
```

## Performance Considerations

- **Fast model (GPT-4o-mini)**: Lower cost, faster responses, suitable for most tasks
- **Slow model (GPT-4)**: Higher cost, better reasoning, use for complex problems
- **Self-consistency samples**: More samples = higher confidence but slower and more expensive
- **CoT steps**: More steps = deeper reasoning but slower responses

Recommended settings:
- Simple questions: `model="fast"`, `num_self_consistency=3`, `num_cot=2`
- Complex reasoning: `model="slow"`, `num_self_consistency=7`, `num_cot=5`

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
