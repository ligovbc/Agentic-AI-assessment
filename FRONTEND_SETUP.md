# Frontend Setup Guide

This guide will help you set up and run the React frontend with BC Government Design System.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  React Frontend │ ◄─────► │  Flask Backend  │
│  (Port 5173)    │  HTTP   │  (Port 5000)    │
│  BC Design      │  CORS   │  Agentic AI     │
└─────────────────┘         └─────────────────┘
```

## Quick Start

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
python app.py
```

The backend will run on [http://localhost:5000](http://localhost:5000)

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Start Frontend Development Server

```bash
npm run dev
```

The frontend will run on [http://localhost:5173](http://localhost:5173)

### 5. Open in Browser

Navigate to [http://localhost:5173](http://localhost:5173)

## Features

### BC Government Design System

- **Official BC Sans Font**: Professional, government-approved typography
- **BC Gov Color Palette**:
  - BC Blue (#003366): Primary brand color
  - BC Gold (#fcba19): Secondary accent color
  - Official government grays and whites

### Accessibility (WCAG 2.1 AA)

✅ Keyboard navigation
✅ Screen reader support
✅ High contrast colors
✅ Focus indicators
✅ ARIA labels
✅ Skip to main content
✅ Semantic HTML

### Visualizations

- **Confidence Charts**: Bar charts showing LLM, agreement, and reflection confidence
- **Token Usage**: Pie charts breaking down prompt vs completion tokens
- **Cost Analysis**: Real-time cost tracking in CAD
- **Chain-of-Thought Display**: Step-by-step reasoning visualization

### PDF Support

- Upload PDF documents
- Automatic text extraction
- Combine PDF content with custom prompts
- Display PDF metadata (pages, etc.)

## Development

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Header.tsx          # BC Gov header with health check
│   ├── services/
│   │   └── api.ts              # API client (axios)
│   ├── App.tsx                 # Main application
│   ├── App.css                 # BC Gov styles
│   ├── index.css               # Global BC Gov styles
│   └── types.ts                # TypeScript types
├── public/
├── .env                        # Environment variables
└── package.json
```

### Key Technologies

- **React 18**: Modern UI framework
- **TypeScript**: Type safety
- **Vite**: Fast build tool and dev server
- **Recharts**: Data visualization library
- **Axios**: HTTP client
- **BC Sans**: Official BC Government typeface

### Environment Variables

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:5000
```

## Building for Production

### Frontend Build

```bash
cd frontend
npm run build
```

The build output will be in `frontend/dist/`

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend communicates with the backend via REST API:

### Endpoints Used

- `GET /` - Health check
- `POST /v1/completions` - Submit analysis (JSON or multipart/form-data with PDF)

### Request Format

```typescript
{
  prompt: string;
  num_self_consistency: number;  // 1-10
  num_cot: number;               // 1-5
  model: 'fast' | 'slow';
  temperature: number;            // 0-2
}
```

### Response Format

```typescript
{
  final_answer: string;
  confidence_score: number;
  llm_confidence: number;
  agreement_confidence: number;
  reflection_confidence: number;
  self_consistency_samples: Array<{
    sample_number: number;
    reasoning_path: Array<{
      step_number: number;
      reasoning: string;
    }>;
    final_answer: string;
    llm_confidence: number;
  }>;
  token_usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  cost_analysis: {
    total_cost: number;
    currency: string;
    // ...
  };
  // ...
}
```

## Troubleshooting

### Frontend can't connect to backend

1. Verify backend is running: `python app.py`
2. Check backend URL in `frontend/.env`
3. Verify CORS is enabled (flask-cors installed)
4. Check browser console for CORS errors

### BC Sans font not loading

The font is loaded via npm package `@bcgov/bc-sans`. Make sure:
```bash
cd frontend
npm install
```

### TypeScript errors

```bash
cd frontend
npm run build
```

Check console for specific errors.

### Port 5173 already in use

Change the port in `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    port: 3000  // or any other port
  }
})
```

## Security Considerations

### For Production

1. **Environment Variables**: Never commit `.env` files
2. **CORS**: Configure specific origins (not `*`)
3. **API Keys**: Backend should validate API keys
4. **Rate Limiting**: Implement on backend
5. **Input Validation**: Both frontend and backend
6. **HTTPS**: Use SSL certificates in production

### Update CORS for Production

In `app.py`:

```python
CORS(app, origins=["https://your-production-domain.gov.bc.ca"])
```

## BC Government Standards

This application follows:

- ✅ BC Web Accessibility Guidelines
- ✅ BC Government Digital Design System
- ✅ WCAG 2.1 Level AA
- ✅ BC Privacy Guidelines
- ✅ BC Security Standards

## Support

For issues or questions:

1. Check the logs (browser console + backend terminal)
2. Verify all dependencies are installed
3. Ensure both frontend and backend are running
4. Check network requests in browser DevTools

## License

BC Government Project - Follow BC Gov licensing requirements.
