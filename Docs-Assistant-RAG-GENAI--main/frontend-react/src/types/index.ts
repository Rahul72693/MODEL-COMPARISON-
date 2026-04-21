// Type definitions for the Model Comparison System

export interface ComparisonResponse {
    gemini: ModelResult;
    groq: ModelResult;
    comparison: ComparisonMetrics;
    sources: ContextSnippet[];
    run_id: number;
}

export interface ModelResult {
    answer: string;
    response_time: number;
    tokens: number;
    cost: number;
    quality: QualityMetrics;
}

export interface QualityMetrics {
    semantic_similarity: number;
    context_relevance: number;
    citation_quality: number;
    completeness_score: number;
}

export interface ComparisonMetrics {
    agreement_score: number;
    gemini_faster: boolean;
    speed_ratio: number;
    cost_ratio: number;
    gemini_quality_avg: number;
    groq_quality_avg: number;
}

export interface ContextSnippet {
    text: string;
    score: number;
    meta: {
        file_name?: string;
        page_number?: number;
        chunk_type?: string;
    };
}

export interface UploadResponse {
    file_name: string;
    extraction_status: string;
    vectorizer_status: {
        status: string;
        message: string;
    };
}

export interface MetricsSummary {
    session_id: string;
    total_queries: number;
    gemini: ProviderStats;
    groq: ProviderStats;
}

export interface ProviderStats {
    avg_response_time: number;
    total_tokens: number;
    total_cost: number;
    query_count: number;
}

export interface HistoricalData {
    run_id: number;
    session_id: string;
    query: string;
    timestamp: string;
    responses: ResponseData[];
}

export interface ResponseData {
    model_name: string;
    response_time: number;
    tokens: number;
    cost: number;
    quality?: QualityMetrics;
}

export interface HealthStatus {
    status: string;
    gemini_ready: boolean;
    groq_ready: boolean;
    comparison_ready: boolean;
}
