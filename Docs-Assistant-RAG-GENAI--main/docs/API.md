# API Documentation - Model Comparison System

The Model Comparison System backend is built with FastAPI and provides endpoints for document extraction, model comparison, and metrics retrieval.

## Base URL
`http://localhost:8000`

## Endpoints

### 1. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Returns the status of the backend and configured LLM providers.
- **Response**:
    ```json
    {
      "status": "ok",
      "gemini_ready": true,
      "groq_ready": true,
      "comparison_ready": true
    }
    ```

### 2. Document Extraction
- **URL**: `/extract`
- **Method**: `POST`
- **Payload**: `file` (Multipart/form-data)
- **Description**: Upload a document (PDF, DOCX, PNG) to extract content and store it in the FAISS vector database.
- **Response**:
    ```json
    {
      "file_name": "report.pdf",
      "extraction_status": "done",
      "vectorizer_status": "ok"
    }
    ```

### 3. Model Comparison
- **URL**: `/compare`
- **Method**: `POST`
- **Payload**:
    ```json
    {
      "session_id": "string",
      "message": "string"
    }
    ```
- **Description**: Query both Gemini and Groq models concurrently using the same context.
- **Response**: Returns side-by-side answers, performance metrics, and quality scores.

### 4. Metrics Summary
- **URL**: `/metrics/summary`
- **Method**: `GET`
- **Params**: `session_id`
- **Description**: Get aggregated stats for all comparisons in a specific session.

### 5. Historical Data
- **URL**: `/metrics/history`
- **Method**: `GET`
- **Params**: `limit` (default 50)
- **Description**: Retrieve a list of recent comparison runs with all associated metrics.

### 6. Provider Specific Metrics
- **URL**: `/providers/metrics`
- **Method**: `GET`
- **Description**: Get aggregate performance metrics directly from the provider instances.
