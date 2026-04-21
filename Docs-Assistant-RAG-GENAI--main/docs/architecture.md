# System Architecture

## Current System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI<br/>app.py]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Backend<br/>main.py]
        LLM[Gemini LLM<br/>gemini-1.0-pro]
    end
    
    subgraph "Processing Layer"
        EXT[Document Extractor<br/>extractor.py]
        VEC[Vectorizer<br/>vectorizer.py]
    end
    
    subgraph "Storage Layer"
        FAISS[(FAISS Index<br/>In-Memory)]
        SESS[(Session History<br/>In-Memory Dict)]
    end
    
    UI -->|HTTP POST /extract| API
    UI -->|HTTP POST /chat| API
    API --> EXT
    API --> LLM
    EXT -->|Text Chunks| VEC
    VEC -->|Embeddings| FAISS
    API -->|Search Query| VEC
    VEC -->|Retrieve Top-K| FAISS
    API -->|Store/Retrieve| SESS
    
    style UI fill:#667eea,stroke:#333,stroke-width:2px,color:#fff
    style API fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style FAISS fill:#EC4899,stroke:#333,stroke-width:2px,color:#fff
```

## Proposed Multi-Model Comparison Architecture

```mermaid
graph TB
    subgraph "Frontend Layer - React"
        RT[React TypeScript<br/>Vite + Tailwind]
        UP[Upload Component]
        CMP[Comparison View]
        MTR[Metrics Dashboard]
        
        RT --> UP
        RT --> CMP
        RT --> MTR
    end
    
    subgraph "API Layer - FastAPI"
        GATE[API Gateway]
        EXT_EP[/extract Endpoint]
        CMP_EP[/compare Endpoint]
        MTR_EP[/metrics Endpoint]
        
        GATE --> EXT_EP
        GATE --> CMP_EP
        GATE --> MTR_EP
    end
    
    subgraph "Processing Layer"
        EXT[Document Extractor]
        VEC[Vectorizer]
        SEARCH[Semantic Search]
    end
    
    subgraph "LLM Provider Layer"
        PROV_INT[LLM Provider Interface]
        GEMINI[Gemini Provider<br/>gemini-1.5-flash]
        GROQ[Groq Provider<br/>llama3-70b]
        
        PROV_INT --> GEMINI
        PROV_INT --> GROQ
    end
    
    subgraph "Comparison Engine"
        COMP[Comparison Orchestrator]
        EVAL[Evaluation Engine]
        METRICS[Metrics Collector]
        
        COMP -->|Query Both| GEMINI
        COMP -->|Query Both| GROQ
        COMP --> EVAL
        EVAL --> METRICS
    end
    
    subgraph "Storage Layer"
        FAISS[(FAISS Vector DB)]
        DB[(SQLite/PostgreSQL<br/>Metrics Storage)]
        CACHE[(Redis Cache<br/>Optional)]
    end
    
    RT <-->|HTTP/WebSocket| GATE
    EXT_EP --> EXT
    EXT --> VEC
    VEC --> FAISS
    
    CMP_EP --> SEARCH
    SEARCH --> FAISS
    CMP_EP --> COMP
    
    MTR_EP --> METRICS
    METRICS --> DB
    
    style RT fill:#667eea,stroke:#333,stroke-width:3px,color:#fff
    style GATE fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style COMP fill:#7C3AED,stroke:#333,stroke-width:2px,color:#fff
    style DB fill:#EC4899,stroke:#333,stroke-width:2px,color:#fff
```

## Data Flow - Comparison Query

```mermaid
sequenceDiagram
    participant User
    participant React
    participant API
    participant Search
    participant Gemini
    participant Groq
    participant Metrics
    participant DB
    
    User->>React: Enter Query
    React->>API: POST /compare {query, sessionId}
    
    API->>Search: Retrieve Context
    Search->>Search: Embed Query
    Search->>Search: FAISS Top-K Search
    Search-->>API: Top-5 Chunks
    
    par Query Both Models
        API->>Gemini: Generate Response
        Gemini-->>API: Response + Metadata
    and
        API->>Groq: Generate Response
        Groq-->>API: Response + Metadata
    end
    
    API->>Metrics: Compute Evaluation
    Metrics->>Metrics: Calculate Metrics
    Metrics->>DB: Store Results
    
    API-->>React: Comparison Result
    React-->>User: Display Side-by-Side
    
    Note over React,User: Show Response Time<br/>Quality Scores<br/>Token Usage
```

## Component Interaction - Evaluation Metrics

```mermaid
graph LR
    subgraph "Input"
        Q[Query]
        R1[Model 1 Response]
        R2[Model 2 Response]
        CTX[Context Chunks]
    end
    
    subgraph "Metrics Engine"
        PERF[Performance Metrics]
        QUAL[Quality Metrics]
        COMP[Comparison Metrics]
    end
    
    subgraph "Performance"
        LAT[Latency]
        TOK[Token Count]
        COST[Cost Estimate]
    end
    
    subgraph "Quality"
        SIM[Semantic Similarity]
        REL[Context Relevance]
        CIT[Citation Quality]
        COMP_SCORE[Completeness]
    end
    
    subgraph "Comparison"
        AGR[Agreement Score]
        CONF[Confidence Delta]
        RATIO[Performance Ratio]
    end
    
    R1 --> PERF
    R2 --> PERF
    PERF --> LAT
    PERF --> TOK
    PERF --> COST
    
    Q --> QUAL
    R1 --> QUAL
    R2 --> QUAL
    CTX --> QUAL
    QUAL --> SIM
    QUAL --> REL
    QUAL --> CIT
    QUAL --> COMP_SCORE
    
    R1 --> COMP
    R2 --> COMP
    COMP --> AGR
    COMP --> CONF
    COMP --> RATIO
    
    style PERF fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style QUAL fill:#7C3AED,stroke:#333,stroke-width:2px,color:#fff
    style COMP fill:#EC4899,stroke:#333,stroke-width:2px,color:#fff
```

## Technology Stack Layers

```mermaid
graph TB
    subgraph "Layer 1: Presentation"
        L1A[React 18 + TypeScript]
        L1B[Tailwind CSS]
        L1C[Recharts + Framer Motion]
    end
    
    subgraph "Layer 2: Application"
        L2A[FastAPI + Uvicorn]
        L2B[WebSocket Support]
        L2C[RESTful API]
    end
    
    subgraph "Layer 3: Business Logic"
        L3A[LLM Provider Abstraction]
        L3B[Comparison Engine]
        L3C[Evaluation Metrics]
    end
    
    subgraph "Layer 4: AI/ML Services"
        L4A[Google Gemini API]
        L4B[Groq API]
        L4C[Sentence Transformers]
    end
    
    subgraph "Layer 5: Data Storage"
        L5A[FAISS Vector DB]
        L5B[SQLite/PostgreSQL]
        L5C[Redis Cache]
    end
    
    L1A --> L2A
    L1B --> L2A
    L1C --> L2A
    L2A --> L3A
    L2B --> L3A
    L2C --> L3A
    L3A --> L4A
    L3B --> L4B
    L3C --> L4C
    L3A --> L5A
    L3B --> L5B
    L3C --> L5C
    
    style L1A fill:#667eea,stroke:#333,stroke-width:2px,color:#fff
    style L2A fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style L3A fill:#7C3AED,stroke:#333,stroke-width:2px,color:#fff
    style L4A fill:#EC4899,stroke:#333,stroke-width:2px,color:#fff
    style L5A fill:#F59E0B,stroke:#333,stroke-width:2px,color:#fff
```

## React Component Hierarchy

```mermaid
graph TB
    APP[App.tsx<br/>Main Router]
    
    subgraph "Pages"
        P1[DocumentInput Page]
        P2[Comparison Page]
        P3[Metrics Page]
        P4[History Page]
    end
    
    subgraph "Layout Components"
        HEADER[Header]
        SIDEBAR[Sidebar]
        TABS[TabNavigation]
    end
    
    subgraph "Feature Components"
        UPLOAD[DocumentUpload]
        QUERY[QueryInput]
        RESPONSE[ModelResponseCard]
        SIDE[SideBySideView]
        DASH[MetricsDashboard]
        CHART[PerformanceChart]
    end
    
    subgraph "Common Components"
        BTN[Button]
        CARD[Card]
        SPINNER[LoadingSpinner]
        TOAST[Toast]
    end
    
    APP --> HEADER
    APP --> SIDEBAR
    APP --> TABS
    APP --> P1
    APP --> P2
    APP --> P3
    APP --> P4
    
    P1 --> UPLOAD
    P2 --> QUERY
    P2 --> SIDE
    P3 --> DASH
    P3 --> CHART
    
    SIDE --> RESPONSE
    DASH --> CHART
    
    UPLOAD --> CARD
    QUERY --> BTN
    RESPONSE --> CARD
    CHART --> CARD
    
    style APP fill:#667eea,stroke:#333,stroke-width:3px,color:#fff
    style P1 fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style P2 fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style P3 fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
```

## Database Schema

```mermaid
erDiagram
    EVALUATION_RUNS ||--o{ MODEL_RESPONSES : contains
    MODEL_RESPONSES ||--|| QUALITY_METRICS : has
    EVALUATION_RUNS ||--o{ HISTORICAL_AGGREGATES : summarizes
    
    EVALUATION_RUNS {
        int id PK
        string session_id
        string query
        datetime timestamp
        string document_name
    }
    
    MODEL_RESPONSES {
        int id PK
        int run_id FK
        string model_name
        text response
        float response_time
        int token_count
        float cost_estimate
    }
    
    QUALITY_METRICS {
        int id PK
        int response_id FK
        float semantic_similarity
        float context_relevance
        float citation_quality
        float completeness_score
    }
    
    HISTORICAL_AGGREGATES {
        int id PK
        int run_id FK
        string model_name
        float avg_response_time
        float avg_quality_score
        int total_tokens
        datetime created_at
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Client Browser"
        BROWSER[React SPA<br/>Port 5173]
    end
    
    subgraph "Application Server"
        NGINX[Nginx<br/>Reverse Proxy]
        BACKEND[FastAPI<br/>Port 8000]
        FRONTEND[Vite Build<br/>Static Files]
    end
    
    subgraph "External Services"
        GEMINI_API[Google Gemini API]
        GROQ_API[Groq API]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Metrics)]
        FAISS_FILE[FAISS Index<br/>File Storage]
        REDIS[(Redis<br/>Cache)]
    end
    
    BROWSER -->|HTTPS| NGINX
    NGINX -->|/api/*| BACKEND
    NGINX -->|/| FRONTEND
    
    BACKEND --> GEMINI_API
    BACKEND --> GROQ_API
    BACKEND --> PG
    BACKEND --> FAISS_FILE
    BACKEND --> REDIS
    
    style BROWSER fill:#667eea,stroke:#333,stroke-width:2px,color:#fff
    style NGINX fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style BACKEND fill:#7C3AED,stroke:#333,stroke-width:2px,color:#fff
    style PG fill:#EC4899,stroke:#333,stroke-width:2px,color:#fff
```

---

## Key Design Decisions

### 1. Provider Abstraction Pattern
Using an abstract base class allows easy addition of new LLM providers without modifying core logic.

### 2. Concurrent Processing
Async/await pattern enables parallel model querying for faster comparisons.

### 3. Modular Metrics
Separate evaluation components for performance, quality, and comparison metrics enable independent testing and extension.

### 4. Component-Based UI
React components promote reusability and maintainability.

### 5. Real-time Updates
WebSocket support for streaming metrics as they're computed.

### 6. Persistent Metrics
SQLite for development, easy migration to PostgreSQL for production scale.
