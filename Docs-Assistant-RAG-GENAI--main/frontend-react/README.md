# Model Comparison System - React Frontend

Modern React frontend for comparing Gemini and Groq LLM responses with comprehensive evaluation metrics.

## 🚀 Features

- **Document Upload**: Drag-and-drop interface for PDF, DOCX, and image files
- **Side-by-Side Comparison**: Real-time comparison of Gemini vs Groq responses
- **Quality Metrics**: Semantic similarity, context relevance, citation quality, and completeness scores
- **Analytics Dashboard**: Interactive charts showing performance, cost, and token usage
- **Modern Design**: Glassmorphism, gradients, smooth animations with Framer Motion

## 📋 Prerequisites

**Important**: This project requires Node.js >= 18.0.0

Current detected Node version: **16.14.2** (Too old for Vite 7)

### Upgrade Node.js:
- Download from: https://nodejs.org/ (LTS version recommended)
- Or use nvm: `nvm install 18 && nvm use 18`

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🎯 Usage

1. **Start Backend** (in project root):
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

2. **Start Frontend** (in frontend-react directory):
   ```bash
   npm run dev
   ```

3. **Open Browser**: Navigate to `http://localhost:5173`

## 📁 Project Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   └── layout/
│   │       ├── Header.tsx          # App header with branding
│   │       └── TabNavigation.tsx   # Animated tab navigation
│   ├── pages/
│   │   ├── DocumentInputPage.tsx   # Document upload interface
│   │   ├── ComparisonPage.tsx      # Side-by-side model comparison
│   │   └── MetricsPage.tsx         # Analytics dashboard
│   ├── services/
│   │   └── api.ts                  # API client for backend
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   ├── App.tsx                     # Main app component
│   ├── index.css                   # Tailwind + custom styles
│   └── main.tsx                    # App entry point
├── tailwind.config.js              # Tailwind configuration
├── vite.config.ts                  # Vite configuration
└── package.json
```

## 🎨 Design System

- **Colors**: Custom gradient palette with glassmorphism effects
- **Typography**: Inter (body) and JetBrains Mono (code)
- **Components**: Glass cards, animated buttons, custom scrollbars
- **Animations**: Framer Motion for smooth transitions

## 🔧 Tech Stack

- **Framework**: React 19 + Vite 7
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Router**: React Router v7
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **HTTP Client**: Axios

## 📡 API Endpoints

The frontend connects to these backend endpoints:

- `POST /extract` - Upload and process documents
- `POST /compare` - Compare both models
- `GET /metrics/summary` - Get session metrics
- `GET /metrics/history` - Get historical data
- `GET /health` - Backend health check

## ⚠️ Troubleshooting

### Vite won't start
- Ensure Node.js >= 18.0.0
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check if port 5173 is available

### Module not found errors
- Run `npm install` to ensure all dependencies are installed
- Restart your IDE/editor to refresh TypeScript

### Backend connection issues
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Update `VITE_API_URL` in `.env` if needed

## 📝 Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## 🚧 Development Notes

- Hot module replacement (HMR) is enabled
- TypeScript strict mode is on
- ESLint is configured for React best practices
- All components are functional components with hooks
