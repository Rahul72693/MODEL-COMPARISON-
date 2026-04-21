# User Guide - Model Comparison System

Welcome to the Model Comparison System! This tool allows you to evaluate how different AI models (Gemini and Groq) perform when answering questions about your medical documents.

## Getting Started

### 1. Uploading Documents
- Navigate to the **Document Input** tab.
- Drag and drop your medical file (PDF, DOCX, or PNG) or click to select a file.
- The system will extract text, detect tables, and perform OCR.
- Once processing is complete, your document is stored and ready for queries.

### 2. Running Comparisons
- Navigate to the **Comparison** tab.
- Enter a question in the text area (e.g., "What are the treatment options for NAFLD?").
- Click **Compare Models**.
- Both Gemini and Groq will generate responses side-by-side.
- You can see the sources cited and compare the answers directly.

### 3. Analyzing Metrics
- Navigate to the **Metrics** tab to see real-time analytics.
- **Charts**: View response time comparisons, token usage, and cost distribution.
- **Detailed Stats**: See average performance scores for both models.
- **Export**: (Coming soon) Download your session data for offline research.

### 4. Historical Data
- View the **History** section to see past runs and how model performance has trended over time across different documents.

## Best Practices
- **Clear Questions**: Be as specific as possible to get the best grounded answers.
- **Document Quality**: High-resolution PDFs and clear images result in better OCR and more accurate retrieval.
- **Context Awareness**: Remember that the models only "know" what is in the document you uploaded for that specific session.
