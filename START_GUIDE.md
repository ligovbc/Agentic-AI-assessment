# 🚀 Quick Start Guide - Agentic AI with BC Gov Frontend

## Overview

This project provides a professional React frontend with BC Government Design System for your Agentic AI backend.

**Stack:**
- **Frontend**: React + TypeScript + BC Design System
- **Backend**: Flask + OpenAI + Self-Consistency + Chain-of-Thought
- **Visualization**: Recharts for interactive charts
- **Accessibility**: WCAG 2.1 AA compliant

---

## 📋 Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 18+** with npm
3. **OpenAI API Key** (set in `.env`)

---

## ⚡ Quick Start (3 Steps)

### Step 1: Start the Backend

```bash
# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Start Flask server
python app.py
```

✅ Backend will run on **http://localhost:5000**

### Step 2: Start the Frontend

Open a **new terminal**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend will run on **http://localhost:5173**

### Step 3: Open in Browser

Navigate to: **http://localhost:5173**

---

## 🎨 What You'll See

### 1. **BC Government Header**
- Official BC Blue (#003366) and BC Gold (#fcba19) colors
- Connection status indicator
- BC Sans typography

### 2. **Input Configuration**
- Text prompt input
- PDF file upload (optional)
- Parameters:
  - Self-Consistency Samples (1-10)
  - Chain-of-Thought Steps (1-5)
  - Model selection (Fast/Slow)
  - Temperature slider (0-2)

### 3. **Results Visualization**
- **Overview**: Confidence scores and processing time
- **Charts**: Bar charts for confidence metrics
- **Final Answer**: Highlighted with reflection reasoning
- **Self-Consistency Analysis**: All reasoning paths displayed
- **Cost Analysis**: Token usage and cost breakdown with pie charts

---

## 🔍 Features

### BC Government Design System
✅ Official BC Sans font
✅ BC Gov color palette
✅ Accessible design
✅ Professional government styling

### Accessibility (WCAG 2.1 AA)
✅ Keyboard navigation
✅ Screen reader support
✅ High contrast colors
✅ Focus indicators
✅ ARIA labels
✅ Skip to main content link

### Visualizations
✅ Confidence bar charts
✅ Token usage pie charts
✅ Real-time cost tracking
✅ Chain-of-Thought step display
✅ Self-consistency sample comparison

### PDF Support
✅ Upload PDF documents
✅ Automatic text extraction
✅ Combine with custom prompts
✅ Display PDF metadata

---

## 📁 Project Structure

```
Agentic-AI-assessment/
├── app.py                      # Flask backend with CORS
├── requirements.txt            # Python dependencies (includes flask-cors)
├── config.py                   # Configuration
├── models.py                   # Pydantic models
├── self_consistency.py         # Self-consistency engine
├── cot_engine.py              # Chain-of-Thought engine
├── pdf_extractor.py           # PDF processing
├── .env                        # Backend environment variables
│
└── frontend/                   # React frontend
    ├── src/
    │   ├── components/
    │   │   └── Header.tsx     # BC Gov header
    │   ├── services/
    │   │   └── api.ts         # API client
    │   ├── App.tsx            # Main app
    │   ├── App.css            # BC Gov styles
    │   ├── index.css          # Global styles
    │   └── types.ts           # TypeScript types
    ├── .env                   # Frontend environment variables
    ├── package.json
    └── README.md
```

---

## 🧪 Testing the Application

### Example 1: Simple Math Question

1. Enter prompt: `If a train travels 60 km in 1 hour, how far will it travel in 2.5 hours?`
2. Set parameters:
   - Self-Consistency: 3
   - Chain-of-Thought: 2
   - Model: Fast
3. Click "Run Analysis"
4. View results with confidence scores and reasoning paths

### Example 2: PDF Analysis

1. Click "Upload PDF" and select a PDF file
2. Enter prompt: `What are the main topics in this document?`
3. Set parameters as desired
4. Click "Run Analysis"
5. View PDF-based analysis results

---

## 🔧 Configuration

### Backend (.env in root)

```env
OPENAI_API_KEY=your_key_here
OPENAI_ENDPOINT=your_azure_endpoint  # For Azure OpenAI
FAST_MODEL=gpt-4o-mini
SLOW_MODEL=gpt-4o
FLASK_PORT=5000
FLASK_DEBUG=False
```

### Frontend (frontend/.env)

```env
VITE_API_URL=http://localhost:5000
```

---

## 🏗️ Building for Production

### Frontend

```bash
cd frontend
npm run build
```

Output: `frontend/dist/`

### Preview Production Build

```bash
npm run preview
```

---

## 🐛 Troubleshooting

### Issue: Frontend can't connect to backend

**Solution:**
1. Check backend is running: `python app.py`
2. Verify URL in `frontend/.env`: `VITE_API_URL=http://localhost:5000`
3. Check browser console for CORS errors
4. Ensure `flask-cors` is installed: `pip install flask-cors==5.0.0`

### Issue: "Module not found" errors

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port already in use

**Backend:**
Change `FLASK_PORT` in `.env` or config

**Frontend:**
Edit `frontend/vite.config.ts` to change port

### Issue: BC Sans font not loading

**Solution:**
```bash
cd frontend
npm install @bcgov/bc-sans
```

---

## 📊 API Endpoints

### Health Check
```
GET http://localhost:5000/
```

### Submit Analysis (JSON)
```
POST http://localhost:5000/v1/completions
Content-Type: application/json

{
  "prompt": "Your question here",
  "num_self_consistency": 3,
  "num_cot": 2,
  "model": "fast",
  "temperature": 0.7
}
```

### Submit Analysis with PDF
```
POST http://localhost:5000/v1/completions
Content-Type: multipart/form-data

pdf_file: <file>
prompt: "Your question"
num_self_consistency: 3
num_cot: 2
model: "fast"
temperature: 0.7
```

---

## 🔒 Security Notes

### Development
- CORS is enabled for all origins (OK for local development)
- API keys stored in `.env` (never commit!)

### Production
- Update CORS in `app.py`:
  ```python
  CORS(app, origins=["https://your-domain.gov.bc.ca"])
  ```
- Use HTTPS
- Implement rate limiting
- Validate all inputs
- Use environment variables for secrets

---

## 📚 Documentation

- [Frontend Setup Guide](FRONTEND_SETUP.md) - Detailed frontend docs
- [Backend API](test_client.py) - Python client examples

---

## ✅ Checklist

Before deployment:

- [ ] Backend running successfully
- [ ] Frontend running successfully
- [ ] Can submit text prompts
- [ ] Can upload PDFs
- [ ] Charts displaying correctly
- [ ] Cost analysis showing
- [ ] Accessibility tested (keyboard nav)
- [ ] Environment variables configured
- [ ] CORS configured for production
- [ ] Build works: `npm run build`

---

## 🎯 Next Steps

1. **Customize Branding**: Update colors/logos for your specific BC Gov department
2. **Add Authentication**: Implement BC Gov SSO if needed
3. **Enhanced Analytics**: Add usage tracking/metrics
4. **Deploy**: Use BC Gov approved hosting (Azure, AWS, etc.)
5. **Testing**: Add unit tests and e2e tests
6. **Documentation**: Add user guide for end users

---

## 💡 Tips

- Use **Fast model** for development (cheaper, faster)
- Start with **1-2 samples** for quick testing
- **PDF files**: Keep under 10 pages for faster processing
- **Temperature**: 0.7 is good default, lower for more consistent results
- Check **browser console** for any errors

---

## 📞 Support

For issues:
1. Check logs (browser console + backend terminal)
2. Verify all dependencies installed
3. Ensure both servers running
4. Check network tab in DevTools

---

**Enjoy your BC Government compliant Agentic AI frontend! 🎉**
