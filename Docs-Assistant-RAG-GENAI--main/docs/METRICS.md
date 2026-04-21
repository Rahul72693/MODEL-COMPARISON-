# Evaluation Metrics Framework

The Model Comparison System uses a multi-dimensional evaluation framework to compare the performance and quality of Gemini and Groq models in a RAG context.

## 1. Performance Metrics

### Response Time (Latency)
- **Measure**: Total time from sending the query to receiving the complete response.
- **Unit**: Seconds.
- **Significance**: Critical for user experience in real-time applications.

### Token Usage & Cost
- **Measure**: Number of input and output tokens processed.
- **Cost Calculation**: Based on current pricing for `gemini-2.0-flash` and `llama-3.3-70b-versatile`.
- **Significance**: Economical evaluation for production scaling.

## 2. Quality Metrics

### Semantic Similarity
- **Measure**: Cosine similarity between the query embedding and the response embedding.
- **Model**: `all-MiniLM-L6-v2`.
- **Range**: 0 (no similarity) to 1 (identical).
- **Significance**: Indicates how well the answer relates to the original question.

### Context Relevance
- **Measure**: Semantic similarity between the response and the retrieved context snippets.
- **Significance**: Measures "grounding" - how well the model stays within the provided document data and avoids hallucinations.

### Citation Quality
- **Measure**: Heuristic check for the presence and validity of source citations (e.g., [1], [2]).
- **Significance**: Evaluates the model's ability to provide verifiable evidence from the source document.

### Completeness Score
- **Measure**: Derived from answer length and keyword coverage (simple heuristic).
- **Significance**: Penalizes overly brief or "I don't know" answers when context is available.

## 3. Comparative Metrics

### Agreement Score
- **Measure**: Semantic similarity between the Gemini response and the Groq response.
- **Significance**: High agreement suggests strong confidence in the answer's factual accuracy.

### Speed & Cost Ratios
- **Measure**: Comparisons between models (e.g., "Groq is 2.5x faster than Gemini").
- **Significance**: Direct head-to-head comparison for trade-off analysis.
