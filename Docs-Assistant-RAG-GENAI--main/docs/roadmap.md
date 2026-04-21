# Research Thesis: Model Comparison System - Detailed Roadmap

## Project Overview

**Objective**: Build a comprehensive comparison framework to evaluate **Gemini** and **Groq** models for RAG-based document question-answering, featuring detailed evaluation metrics and a modern React-based UI.

**Current System**: RAG-based document assistant with:
- Document extraction (PDF, DOCX, PNG with OCR)
- FAISS vector database for semantic search
- Gemini LLM integration
- Streamlit frontend

**Target System**: Dual-model comparison platform with:
- Abstract LLM interface supporting multiple providers
- Comprehensive evaluation metrics framework
- Modern React UI with side-by-side comparisons
- Real-time performance analytics and visualizations

---

## Phase 1: Codebase Analysis & Architecture Planning

### Duration: 2-3 days

### Objectives
- Deep understanding of existing codebase
- Design extensible architecture for multi-model support
- Plan evaluation metrics framework
- Define data models and API contracts

### Deliverables

#### 1.1 System Architecture Document
- Current architecture diagram
- Proposed multi-model architecture
- Component interaction flows
- Database schema for metrics storage

#### 1.2 Technical Specifications
- API endpoint definitions
- Data models for evaluation metrics
- Model provider interface contract
- Frontend component hierarchy

### Key Technical Decisions

**Model Provider Abstraction**
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: List[str], history: List[Dict]) -> Response
    
    @abstractmethod
    def get_metrics(self) -> ModelMetrics
```

**Evaluation Metrics Structure**
```python
@dataclass
class EvaluationMetrics:
    response_time: float
    token_count: int
    cost_estimate: float
    semantic_similarity: float
    context_relevance: float
    citation_quality: float
    timestamp: datetime
```

---

## Phase 2: Backend Enhancement - Model Integration

### Duration: 5-7 days

### Objectives
- Implement abstract LLM provider interface
- Integrate Groq API alongside existing Gemini
- Build concurrent query execution system
- Create evaluation metrics computation engine

### Deliverables

#### 2.1 LLM Provider System
**Files to Create/Modify:**
- `backend/llm_providers/base.py` - Abstract provider interface
- `backend/llm_providers/gemini_provider.py` - Gemini implementation
- `backend/llm_providers/groq_provider.py` - Groq implementation
- `backend/llm_providers/__init__.py` - Provider factory

**Key Features:**
- Unified interface for model invocation
- Automatic retry logic and error handling
- Token counting and cost tracking
- Response time measurement

#### 2.2 Comparison Engine
**Files to Create:**
- `backend/comparison/engine.py` - Dual-model query executor
- `backend/comparison/metrics.py` - Metrics computation
- `backend/comparison/storage.py` - Results persistence

**Capabilities:**
- Concurrent model querying (asyncio)
- Real-time metric collection
- Side-by-side response storage

#### 2.3 Enhanced API Endpoints
**New Endpoints:**
```python
@app.post("/api/compare")
async def compare_models(query: QueryRequest) -> ComparisonResponse

@app.get("/api/metrics/summary")
async def get_metrics_summary(session_id: str) -> MetricsSummary

@app.get("/api/metrics/history")
async def get_metrics_history(limit: int = 50) -> List[HistoricalMetric]

@app.post("/api/evaluate")
async def evaluate_response(evaluation: EvaluationRequest) -> EvaluationResult
```

### Technical Implementation

**Environment Variables** (`.env` update):
```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
DATABASE_URL=sqlite:///./metrics.db  # For metrics storage
```

**Dependencies** (`requirements.txt` additions):
```
groq>=0.4.0
sqlalchemy>=2.0.0
sentence-transformers>=2.2.0  # For semantic similarity
scikit-learn>=1.3.0
asyncio
aiohttp
```

---

## Phase 3: Evaluation Metrics Framework

### Duration: 4-5 days

### Objectives
- Implement comprehensive evaluation metrics
- Build automated quality assessment
- Create metrics aggregation and analysis system
- Develop comparison scoring algorithm

### Deliverables

#### 3.1 Core Metrics Implementation

**Performance Metrics:**
- **Response Latency**: Time from query to response
- **Token Usage**: Input/output token counts
- **Cost Estimation**: Based on model pricing
- **Throughput**: Queries per second capability

**Quality Metrics:**
- **Semantic Similarity**: Compare answer relevance using embeddings
- **Context Relevance**: How well retrieved chunks match the query
- **Citation Quality**: Accuracy and completeness of source citations
- **Answer Completeness**: Coverage of question aspects

**Comparative Metrics:**
- **Agreement Score**: Semantic similarity between model responses
- **Confidence Delta**: Difference in response certainty
- **Performance Ratio**: Speed/quality tradeoff

#### 3.2 Automated Evaluation System

**Files to Create:**
- `backend/evaluation/quality_scorer.py` - Answer quality metrics
- `backend/evaluation/similarity.py` - Semantic similarity computation
- `backend/evaluation/citation_checker.py` - Citation validation
- `backend/evaluation/aggregator.py` - Metrics aggregation

**Implementation Details:**

```python
class QualityScorer:
    def compute_semantic_similarity(self, answer1: str, answer2: str) -> float:
        # Use sentence-transformers to compute cosine similarity
        
    def assess_context_relevance(self, query: str, context: List[str], answer: str) -> float:
        # Measure how well answer uses provided context
        
    def evaluate_citation_quality(self, answer: str, sources: List[Dict]) -> float:
        # Check citation accuracy and completeness
```

#### 3.3 Metrics Database Schema

```sql
CREATE TABLE evaluation_runs (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    query TEXT,
    timestamp DATETIME,
    document_name TEXT
);

CREATE TABLE model_responses (
    id INTEGER PRIMARY KEY,
    run_id INTEGER,
    model_name TEXT,
    response TEXT,
    response_time REAL,
    token_count INTEGER,
    cost_estimate REAL,
    FOREIGN KEY (run_id) REFERENCES evaluation_runs(id)
);

CREATE TABLE quality_metrics (
    id INTEGER PRIMARY KEY,
    response_id INTEGER,
    semantic_similarity REAL,
    context_relevance REAL,
    citation_quality REAL,
    completeness_score REAL,
    FOREIGN KEY (response_id) REFERENCES model_responses(id)
);
```

---

## Phase 4: Modern React Frontend Development

### Duration: 7-10 days

### Objectives
- Build beautiful, modern UI with premium aesthetics
- Implement document upload with drag-drop
- Create side-by-side model comparison view
- Develop interactive metrics dashboard
- Design responsive, animated components

### Deliverables

#### 4.1 Project Initialization

**Setup Commands:**
```bash
cd Docs-Assistant-RAG-GENAI--main
npx -y create-vite@latest frontend-react -- --template react-ts
cd frontend-react
npm install
```

**Dependencies:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "framer-motion": "^10.16.0",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18",
    "react-dropzone": "^14.2.3",
    "tailwindcss": "^3.3.5"
  }
}
```

#### 4.2 Design System

**Color Palette** (`src/styles/theme.css`):
```css
:root {
  /* Primary Gradient */
  --primary-start: #667eea;
  --primary-end: #764ba2;
  
  /* Accent Colors */
  --accent-blue: #4F46E5;
  --accent-purple: #7C3AED;
  --accent-pink: #EC4899;
  
  /* Backgrounds */
  --bg-primary: #0F172A;
  --bg-secondary: #1E293B;
  --bg-card: #334155;
  
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 1);
}
```

**Typography:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body {
  font-family: 'Inter', sans-serif;
}

code, .monospace {
  font-family: 'JetBrains Mono', monospace;
}
```

#### 4.3 Component Architecture

**Directory Structure:**
```
frontend-react/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── TabNavigation.tsx
│   │   ├── upload/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── TextInput.tsx
│   │   │   └── ProcessingStatus.tsx
│   │   ├── comparison/
│   │   │   ├── QueryInput.tsx
│   │   │   ├── ModelResponseCard.tsx
│   │   │   ├── SideBySideView.tsx
│   │   │   └── DiffViewer.tsx
│   │   ├── metrics/
│   │   │   ├── MetricsDashboard.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   ├── QualityRadar.tsx
│   │   │   ├── ComparisonTable.tsx
│   │   │   └── HistoricalTrends.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── Toast.tsx
│   ├── pages/
│   │   ├── DocumentInput.tsx
│   │   ├── Comparison.tsx
│   │   ├── Metrics.tsx
│   │   └── History.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── hooks/
│   │   ├── useComparison.ts
│   │   ├── useMetrics.ts
│   │   └── useWebSocket.ts
│   ├── types/
│   │   └── index.ts
│   └── App.tsx
```

#### 4.4 Key UI Components

**Document Upload Component** (with drag-drop):
```tsx
// Glassmorphism card with gradient border
// Animated file hover states
// Real-time upload progress
// Support for PDF, DOCX, PNG, and text input
```

**Side-by-Side Comparison View:**
```tsx
// Split-screen layout
// Synchronized scrolling
// Highlight differences
// Citation tooltips
// Response time badges
```

**Metrics Dashboard:**
```tsx
// Interactive charts (Recharts)
// Real-time metric updates
// Comparison radar chart (quality metrics)
// Performance line graphs
// Cost comparison bar charts
// Token usage visualization
```

**Design Principles:**
- **Glassmorphism**: Translucent cards with backdrop blur
- **Gradients**: Smooth color transitions on buttons and backgrounds
- **Micro-animations**: Framer Motion for smooth transitions
- **Dark Mode**: Primary theme with optional light mode
- **Responsive**: Mobile-first design, tablet and desktop optimized

---

## Phase 5: Integration & Real-time Features

### Duration: 3-4 days

### Objectives
- Connect React frontend with FastAPI backend
- Implement WebSocket for real-time updates
- Add loading states and error handling
- Optimize performance

### Deliverables

#### 5.1 API Integration Layer

**Files to Create:**
- `frontend-react/src/services/api.ts` - Axios-based API client
- `frontend-react/src/services/websocket.ts` - WebSocket client
- `frontend-react/src/hooks/useComparison.ts` - Comparison hook
- `frontend-react/src/hooks/useMetrics.ts` - Metrics hook

**API Client Implementation:**
```typescript
class APIClient {
  async compareModels(query: string, sessionId: string): Promise<ComparisonResult>
  async uploadDocument(file: File): Promise<UploadResponse>
  async getMetrics(sessionId: string): Promise<MetricsSummary>
  async getHistory(limit: number): Promise<HistoricalData[]>
}
```

#### 5.2 WebSocket Integration

**Backend WebSocket Endpoint:**
```python
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    # Stream real-time comparison progress
    # Send incremental metrics updates
    # Notify completion
```

**Frontend WebSocket Hook:**
```typescript
const useWebSocket = (sessionId: string) => {
  // Connect to backend WebSocket
  // Listen for metric updates
  // Handle reconnection
  // Return real-time data stream
}
```

#### 5.3 State Management

**Context Providers:**
- `ComparisonContext` - Manage comparison state
- `MetricsContext` - Track metrics data
- `SessionContext` - Handle user sessions

---

## Phase 6: Testing & Optimization

### Duration: 3-4 days

### Objectives
- End-to-end testing with real documents
- Performance optimization
- UI/UX refinement
- Bug fixes and edge case handling

### Deliverables

#### 6.1 Test Suite

**Backend Tests:**
- Unit tests for LLM providers
- Integration tests for comparison engine
- API endpoint tests
- Metrics computation validation

**Frontend Tests:**
- Component unit tests (Jest + React Testing Library)
- Integration tests
- E2E tests (Playwright)

#### 6.2 Performance Optimization

**Backend:**
- Implement response caching (Redis)
- Concurrent model querying with asyncio
- Database query optimization
- FAISS index optimization

**Frontend:**
- Code splitting and lazy loading
- Image optimization
- Bundle size reduction (Vite optimization)
- Memoization of expensive computations

#### 6.3 Example Test Documents

Use existing documents:
- `Research on Non-alcoholic Fatty Liver Disease.pdf`
- `J of Gastro and Hepatol - 2017 - Wong.docx`

Create test queries:
- Factual questions (e.g., "What are the risk factors for NAFLD?")
- Complex reasoning questions
- Multi-hop questions requiring multiple chunks

---

## Phase 7: Documentation & Deployment

### Duration: 2-3 days

### Deliverables

#### 7.1 Documentation

**Files to Create/Update:**
- Updated `README.md` with comparison feature
- `docs/API.md` - API documentation
- `docs/METRICS.md` - Evaluation metrics methodology
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/USER_GUIDE.md` - User manual

#### 7.2 Deployment Configuration

**Docker Setup:**
```dockerfile
# Backend Dockerfile
# Frontend Dockerfile  
# docker-compose.yml for full stack
```

**Environment Templates:**
- `.env.example` with all required variables
- Configuration for production deployment

---

## Technology Stack Summary

### Backend
- **Framework**: FastAPI (async support)
- **LLM Providers**: Google Gemini, Groq
- **Vector DB**: FAISS
- **Database**: SQLite (development), PostgreSQL (production)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Document Processing**: pdfplumber, python-docx, pytesseract

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Custom CSS
- **Charts**: Recharts
- **Animations**: Framer Motion
- **State**: React Context + Hooks
- **HTTP Client**: Axios
- **Real-time**: WebSocket

### DevOps
- **Version Control**: Git
- **Containerization**: Docker
- **Testing**: Jest, Playwright, pytest
- **CI/CD**: GitHub Actions (recommended)

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Analysis & Planning | 2-3 days | None |
| Phase 2: Backend Enhancement | 5-7 days | Phase 1 |
| Phase 3: Evaluation Metrics | 4-5 days | Phase 2 |
| Phase 4: React Frontend | 7-10 days | Phase 1 |
| Phase 5: Integration | 3-4 days | Phase 2, 4 |
| Phase 6: Testing | 3-4 days | Phase 5 |
| Phase 7: Documentation | 2-3 days | Phase 6 |

**Total Estimated Duration**: 26-36 days (4-6 weeks)

---

## Success Criteria

1. **Functional Requirements**
   - ✅ Both models respond to queries with retrieved context
   - ✅ Evaluation metrics computed for each response
   - ✅ Side-by-side comparison UI working
   - ✅ Metrics dashboard shows real-time data

2. **Performance Requirements**
   - ✅ Response time < 5 seconds for typical queries
   - ✅ UI loads in < 2 seconds
   - ✅ Support concurrent queries without blocking

3. **Quality Requirements**
   - ✅ Accurate metric calculations
   - ✅ Beautiful, modern UI design
   - ✅ Responsive across devices
   - ✅ Comprehensive error handling

4. **Research Requirements**
   - ✅ Statistical analysis of model performance
   - ✅ Exportable comparison data
   - ✅ Reproducible evaluation methodology
   - ✅ Clear documentation for thesis inclusion
