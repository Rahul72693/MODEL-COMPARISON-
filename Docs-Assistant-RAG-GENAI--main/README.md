# Medical Document Assistant & Model Comparison System

An advanced AI-powered platform for medical document analysis and LLM performance evaluation. This system allows users to upload medical documents and compare the responses of **Google Gemini** and **Llama (via Groq)** models side-by-side using a comprehensive RAG pipeline.

## 🚀 Key Features
- 📂 **Multi-format Extraction**: PDF, DOCX, and PNG (with OCR + Table detection).
- 🧠 **Dual-Model Comparison**: Real-time side-by-side responses from Gemini 2.0 Flash and Llama 3.3 70B.
- 📊 **Advanced Metrics**: Evaluation of latency, cost, semantic similarity, context relevance, and citation quality.
- 🎨 **Modern React UI**: Premium glassmorphism design with interactive charts and real-time updates.
- 🛠️ **Research-Ready**: Historical tracking of performance trends for academic or technical thesis work.

## 📦 Documentation
For detailed information on specific components, please refer to the following guides:
- [🚀 Quick Start & Deployment](docs/DEPLOYMENT.md)
- [📖 User Guide](docs/USER_GUIDE.md)
- [🔌 API Reference](docs/API.md)
- [📈 Evaluation Metrics](docs/METRICS.md)
- [📝 Project Roadmap](docs/roadmap.md)

## 🏗️ Architecture
The system follows a modular architecture:
1. **Frontend**: React 18 + Vite + Tailwind CSS + Framer Motion.
2. **Backend**: FastAPI + SQLAlchemy + Groq/Gemini SDKs.
3. **Extraction**: pdfplumber + python-docx + Tesseract OCR.
4. **Vector DB**: FAISS (ephemeral in-memory storage).

## 🛠️ Installation & Setup

### API Keys
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
```

### Option 1: Local Development
```bash
# Backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
cd frontend-react
npm install
npm run dev
```

### Option 2: Docker
```bash
docker-compose up --build
```

## 📜 License
Internal Research Prototype

## 👥 Acknowledgments
Built for Advanced Agentic Coding research and medical document analysis.
