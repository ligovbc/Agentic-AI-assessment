# Agentic AI Assessment with BC Government Frontend

A professional full-stack application implementing advanced AI reasoning techniques with a BC Government-compliant frontend interface.

## Overview

**Stack:**
- **Frontend**: React + TypeScript + BC Government Design System
- **Backend**: Flask + Azure OpenAI + Self-Consistency + Chain-of-Thought
- **Visualization**: Recharts for interactive charts
- **Accessibility**: WCAG 2.1 AA compliant

**Key Features:**
- **Chain-of-Thought (CoT)** reasoning: Break down complex problems into logical steps
- **Self-Consistency**: Generate multiple reasoning paths and select the most consistent answer
- **PDF Support**: Upload and analyze PDF documents
- **Model Selection**: Choose between fast (GPT-4o-mini) and slow (GPT-4o) models
- **BC Government Design**: Official BC Sans font and color palette
- **Cost Tracking**: Real-time token usage and cost analysis
- **Confidence Scoring**: Based on answer agreement and LLM self-assessment

## Quick Start (3 Steps)

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- OpenAI or Azure OpenAI API key

### Step 1: Start the Backend

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Navigate to backend directory
cd backend

# Configure environment variables
cp .env.example .env
# Edit .env and add your API key

# Start Flask server
python app.py
```

Backend will run on **http://localhost:5000**

### Step 2: Start the Frontend

Open a **new terminal**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Configure environment variables
# Create frontend/.env with:
# VITE_API_URL=http://localhost:5000

# Start development server
npm run dev
```

Frontend will run on **http://localhost:5173**

### Step 3: Open in Browser

Navigate to: **http://localhost:5173**

---

## Installation Options

### Option 1: Docker (Recommended for Production)

```bash
# Clone repository
git clone <repository-url>
cd Agentic-AI-assessment

# Set up environment
cp .env.example backend/.env
# Edit backend/.env and add your API key

# Build and run
cd backend
docker-compose up -d
```

Backend API available at `http://localhost:5000`

To view logs:
```bash
docker-compose logs -f
```

To stop:
```bash
docker-compose down
```

### Option 2: Local Development

```bash
# Clone repository
git clone <repository-url>
cd Agentic-AI-assessment

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Configure backend
cp .env.example backend/.env
# Edit backend/.env with your API key

# Install frontend dependencies
cd frontend
npm install

# Create frontend/.env with:
# VITE_API_URL=http://localhost:5000
```

---

## Configuration

### Backend Environment Variables (backend/.env)

```env
# Provider Configuration (choose one)
OPENAI_PROVIDER=openai  # or "azure"

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Azure OpenAI Configuration (if using Azure)
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Model Configuration
FAST_MODEL=gpt-4o-mini
SLOW_MODEL=gpt-4o

# Flask Configuration
FLASK_PORT=5000
FLASK_DEBUG=False
```

### Frontend Environment Variables (frontend/.env)

```env
VITE_API_URL=http://localhost:5000
```

---

## Project Structure

```
Agentic-AI-assessment/
├── backend/                    # Backend directory
│   ├── app.py                  # Flask REST API with CORS
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models for validation
│   ├── self_consistency.py     # Self-consistency engine
│   ├── cot_engine.py          # Chain-of-thought engine
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── test_client.py         # Python test client
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Docker configuration
│   ├── docker-compose.yml     # Docker Compose config
│   └── .env                   # Backend environment variables
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── Header.tsx     # BC Gov header
│   │   ├── services/
│   │   │   └── api.ts         # API client (axios)
│   │   ├── App.tsx            # Main application
│   │   ├── App.css            # BC Gov styles
│   │   ├── index.css          # Global styles
│   │   └── types.ts           # TypeScript types
│   ├── .env                   # Frontend environment variables
│   ├── package.json
│   └── README.md
│
├── README.md                   # This file
└── .env.example               # Example environment variables
```

---

## Features

### BC Government Design System

✅ Official BC Sans font
✅ BC Gov color palette (BC Blue #003366, BC Gold #fcba19)
✅ Professional government styling
✅ Official branding and logos

### Accessibility (WCAG 2.1 AA)

✅ Keyboard navigation
✅ Screen reader support
✅ High contrast colors
✅ Focus indicators
✅ ARIA labels
✅ Skip to main content link
✅ Semantic HTML

### Visualizations

✅ Confidence bar charts
✅ Token usage pie charts
✅ Real-time cost tracking
✅ Chain-of-thought step display
✅ Self-consistency sample comparison

### PDF Support

✅ Upload PDF documents
✅ Automatic text extraction
✅ Combine with custom prompts
✅ Display PDF metadata

---

## API Documentation

### Endpoints

#### 1. Health Check
```
GET http://localhost:5000/
```

Returns API status and version.

#### 2. Completions (JSON)
```
POST http://localhost:5000/v1/completions
Content-Type: application/json
```

**Request:**
```json
{
  "prompt": "What is the capital of France?",
  "system_prompt": "You are a helpful assistant",
  "num_self_consistency": 3,
  "num_cot": 2,
  "model": "fast",
  "temperature": 0.7
}
```

**Parameters:**
- `prompt` (required): Your question or prompt
- `system_prompt` (optional): System instructions for the AI
- `num_self_consistency` (optional, default: 5): Number of reasoning paths (1-10)
- `num_cot` (optional, default: 3): Chain-of-thought steps per path (1-5)
- `model` (optional, default: "fast"): "fast" (GPT-4o-mini) or "slow" (GPT-4o)
- `temperature` (optional, default: 0.7): Response randomness (0.0-2.0)

**Response:**
```json
{
  "prompt": "What is the capital of France?",
  "model_used": "gpt-4o-mini",
  "final_answer": "Paris is the capital of France...",
  "reflection_reasoning": "The analysis confirms...",
  "reasoning_summary": "Generated 3 independent reasoning paths...",
  "llm_confidence": 95.0,
  "self_consistency_samples": [
    {
      "sample_number": 1,
      "reasoning_path": [
        {
          "step_number": 1,
          "reasoning": "First, identify the capital city..."
        }
      ],
      "final_answer": "Paris",
      "llm_confidence": 95.0
    }
  ],
  "token_usage": {
    "prompt_tokens": 150,
    "completion_tokens": 300,
    "total_tokens": 450
  },
  "cost_analysis": {
    "input_cost": 0.000075,
    "output_cost": 0.00045,
    "total_cost": 0.000525,
    "currency": "USD"
  },
  "timing": {
    "total_time": 2.5
  }
}
```

#### 3. Completions with PDF
```
POST http://localhost:5000/v1/completions
Content-Type: multipart/form-data
```

**Parameters:**
- `pdf_file`: PDF file (form data)
- `prompt`: Question about the PDF
- `num_self_consistency`: Number of samples
- `num_cot`: CoT steps
- `model`: "fast" or "slow"
- `temperature`: 0.0-2.0

**Additional Response Fields:**
```json
{
  "pdf_info": {
    "num_pages": 5,
    "error": null
  }
}
```

---

## Usage Examples

### Example 1: Simple Question

**Input:**
```
Prompt: "If a train travels 60 km in 1 hour, how far will it travel in 2.5 hours?"
Self-Consistency: 3
Chain-of-Thought: 2
Model: Fast
```

**Process:**
1. System generates 3 independent reasoning paths
2. Each path uses 2 chain-of-thought steps
3. Answers are compared for consistency
4. Most consistent answer is selected

**Output:**
- Final answer with confidence score
- All reasoning paths displayed
- Cost analysis and timing

### Example 2: PDF Analysis

**Input:**
```
PDF: research_paper.pdf
Prompt: "What are the main findings in this document?"
Self-Consistency: 5
Chain-of-Thought: 3
Model: Slow
```

**Process:**
1. PDF text is extracted automatically
2. Text is combined with your prompt
3. AI analyzes with enhanced reasoning
4. Multiple reasoning paths ensure accuracy

---

## Architecture

### System Flow

```
┌─────────────────┐         ┌─────────────────┐
│  React Frontend │ ◄─────► │  Flask Backend  │
│  (Port 5173)    │  HTTP   │  (Port 5000)    │
│  BC Design      │  CORS   │  Agentic AI     │
└─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Azure OpenAI /  │
                            │    OpenAI API   │
                            └─────────────────┘
```

### Backend Components

1. **app.py**: Flask REST API with CORS support
2. **config.py**: Environment configuration management
3. **models.py**: Pydantic models for request/response validation
4. **cot_engine.py**: Chain-of-thought reasoning using LangChain
5. **self_consistency.py**: Self-consistency mechanism with voting
6. **pdf_extractor.py**: PDF text extraction using pdfplumber

### Frontend Components

1. **Header.tsx**: BC Government branded header
2. **App.tsx**: Main application with form and results display
3. **api.ts**: Axios-based API client
4. **types.ts**: TypeScript interfaces

### How It Works

1. **Request Validation**: Pydantic validates incoming requests
2. **Model Selection**: Fast (GPT-4o-mini) or Slow (GPT-4o) model
3. **Self-Consistency Generation**:
   - Multiple independent reasoning paths created
   - Each uses chain-of-thought for step-by-step reasoning
4. **Answer Aggregation**:
   - Answers from all paths collected
   - Most consistent answer selected
   - Confidence calculated from agreement
5. **Reflection**: Final answer reviewed and refined
6. **Response**: Complete details returned with costs

---

## Testing

### Backend Testing

Run the Python test client:

```bash
cd backend
python test_client.py
```

The test client includes examples for:
- Simple math problems
- Complex reasoning
- Different parameter configurations

### Frontend Testing

```bash
cd frontend
npm run build  # Check for TypeScript errors
```

Test in browser:
1. Enter a prompt
2. Adjust parameters
3. Submit and view results
4. Try uploading a PDF

---

## Building for Production

### Frontend Build

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/`

Preview production build:
```bash
npm run preview
```

### Backend Docker Build

```bash
cd backend
docker build -t agentic-ai .
docker run -p 5000:5000 --env-file .env agentic-ai
```

---

## Troubleshooting

### Frontend can't connect to backend

**Solutions:**
1. Check backend is running: `cd backend && python app.py`
2. Verify `VITE_API_URL` in `frontend/.env`
3. Check browser console for CORS errors
4. Ensure `flask-cors` is installed: `pip install flask-cors`

### "Module not found" errors (Frontend)

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### "Module not found" errors (Backend)

```bash
cd backend
pip install -r requirements.txt
```

### Port already in use

**Backend:**
- Change `FLASK_PORT` in `backend/.env`

**Frontend:**
- Edit `frontend/vite.config.ts` and change port

### BC Sans font not loading

```bash
cd frontend
npm install @bcgov/bc-sans
```

### Docker build fails

1. Check Docker is running
2. Verify `backend/.env` exists
3. Check for pywin32 or Windows-specific dependencies in requirements.txt

### API returns 401 error

1. Check API key in `backend/.env`
2. Verify `OPENAI_PROVIDER` is set correctly ("openai" or "azure")
3. For Azure: Check endpoint URL and API version

---

## Performance Considerations

### Model Selection

- **Fast (GPT-4o-mini)**: Lower cost, faster responses, suitable for most tasks
- **Slow (GPT-4o)**: Higher cost, better reasoning, use for complex problems

### Parameter Tuning

- **Self-consistency samples**: More samples = higher confidence but slower and more expensive
- **CoT steps**: More steps = deeper reasoning but slower responses
- **Temperature**: Lower = more consistent, Higher = more creative

### Recommended Settings

**Simple questions:**
```
model: "fast"
num_self_consistency: 3
num_cot: 2
temperature: 0.5
```

**Complex reasoning:**
```
model: "slow"
num_self_consistency: 7
num_cot: 4
temperature: 0.7
```

### Limits

- Max chain-of-thought steps: 5
- Max self-consistency samples: 10
- Temperature range: 0.0 - 2.0
- PDF size: Keep under 10 pages for faster processing

---

## Security

### Development

- CORS enabled for all origins (OK for local dev)
- API keys in `.env` files (never commit!)
- File uploads validated (PDF only)

### Production Checklist

- [ ] Update CORS in `backend/app.py`:
  ```python
  CORS(app, origins=["https://your-domain.gov.bc.ca"])
  ```
- [ ] Use HTTPS with SSL certificates
- [ ] Implement rate limiting
- [ ] Validate all inputs on backend
- [ ] Use environment variables for all secrets
- [ ] Enable logging and monitoring
- [ ] Set `FLASK_DEBUG=False`
- [ ] Implement authentication/authorization
- [ ] Regular security audits

---

## BC Government Standards

This application follows:

- ✅ BC Web Accessibility Guidelines
- ✅ BC Government Digital Design System
- ✅ WCAG 2.1 Level AA compliance
- ✅ BC Privacy Guidelines
- ✅ BC Security Standards

---

## Error Handling

The API returns appropriate HTTP status codes:
- **200**: Success
- **400**: Invalid request (validation error)
- **500**: Internal server error

Error response format:
```json
{
  "error": "Invalid request",
  "message": "Detailed error message",
  "details": [...]
}
```

---

## Development Tips

- Use **Fast model** for development (cheaper, faster)
- Start with **1-2 samples** for quick testing
- Check **browser console** and **backend logs** for errors
- Use **network tab** in DevTools to debug API calls
- Test with small PDFs first (1-2 pages)
- Monitor costs in the response for budget tracking

---

## License

MIT

---

## Support

For issues:
1. Check logs (browser console + backend terminal)
2. Verify all dependencies installed
3. Ensure both servers running
4. Check environment variables configured
5. Review network tab in browser DevTools

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Enjoy your BC Government compliant Agentic AI Assessment tool!**
