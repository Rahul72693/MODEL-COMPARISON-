import axios from 'axios';
import type {
    ComparisonResponse,
    UploadResponse,
    MetricsSummary,
    HistoricalData,
    HealthStatus,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export class APIClient {
    /**
     * Check backend health status
     */
    static async checkHealth(): Promise<HealthStatus> {
        const { data } = await api.get<HealthStatus>('/health');
        return data;
    }

    /**
     * Upload and extract a document
     */
    static async uploadDocument(file: File): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const { data } = await api.post<UploadResponse>('/extract', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return data;
    }

    /**
     * Compare both models with a query
     */
    static async compareModels(
        sessionId: string,
        message: string
    ): Promise<ComparisonResponse> {
        const { data } = await api.post<ComparisonResponse>('/compare', {
            session_id: sessionId,
            message,
        });

        return data;
    }

    /**
     * Get single model response (Gemini only for backward compatibility)
     */
    static async chat(sessionId: string, message: string): Promise<any> {
        const { data } = await api.post('/chat', {
            session_id: sessionId,
            message,
        });

        return data;
    }

    /**
     * Get metrics summary for a session
     */
    static async getMetricsSummary(sessionId: string): Promise<MetricsSummary> {
        const { data } = await api.get<MetricsSummary>('/metrics/summary', {
            params: { session_id: sessionId },
        });

        return data;
    }

    /**
     * Get historical comparison data
     */
    static async getMetricsHistory(limit: number = 50): Promise<HistoricalData[]> {
        const { data } = await api.get<{ history: HistoricalData[] }>('/metrics/history', {
            params: { limit },
        });

        return data.history;
    }

    /**
     * Get provider aggregate metrics
     */
    static async getProviderMetrics(): Promise<{
        gemini: any;
        groq: any;
    }> {
        const { data } = await api.get('/providers/metrics');
        return data;
    }
}

export default api;
