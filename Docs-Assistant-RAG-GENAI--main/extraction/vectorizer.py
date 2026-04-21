# extraction/vectorizer.py
"""
Vectorizer module for generating embeddings and storing them in FAISS (ephemeral).
- Uses SentenceTransformer ("all-MiniLM-L6-v2")
- Stores normalized embeddings in FAISS IndexFlatIP (cosine similarity via dot product)
- Keeps per-vector metadata to enable citation and retrieval
- Provides vectorize_and_store() and search_top_k()
"""

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Any

# Load embedding model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIM = model.get_sentence_embedding_dimension()

# Cosine similarity via inner product on L2-normalized vectors
index = faiss.IndexFlatIP(EMBED_DIM)

# In-memory stores aligned by vector id (0..N-1)
doc_texts: List[str] = []   # raw text chunks
doc_meta:  List[Dict[str, Any]] = []  # {file_name, page_number, chunk_type, ...}

def _extract_texts_and_meta(extraction_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten page text + table rows into chunks with metadata."""
    file_name = extraction_json.get("file_name", "unknown")
    chunks: List[Dict[str, Any]] = []
    for page in extraction_json.get("pages", []):
        pno = page.get("page_number", None)

        # page text
        txt = (page.get("text") or "").strip()
        if txt:
            chunks.append({
                "text": txt,
                "file_name": file_name,
                "page_number": pno,
                "chunk_type": "text"
            })

        # table rows
        for table in page.get("tables", []):
            for row in table.get("rows", []):
                row_text = " | ".join([c.strip() for c in row])
                if row_text:
                    chunks.append({
                        "text": row_text,
                        "file_name": file_name,
                        "page_number": pno,
                        "chunk_type": "table_row"
                    })
    return chunks

def _normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / norms

def vectorize_and_store(extraction_json: Dict[str, Any]) -> Dict[str, Any]:
    """Embed chunks and add to FAISS (normalized for cosine/IP)."""
    global doc_texts, doc_meta, index

    chunks = _extract_texts_and_meta(extraction_json)
    if not chunks:
        return {"status": "empty", "message": "No text found to embed."}

    texts = [c["text"] for c in chunks]
    embs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False).astype("float32")
    embs = _normalize(embs)  # important for cosine via inner product
    index.add(embs)

    doc_texts.extend(texts)
    doc_meta.extend([{k: c[k] for k in c if k != "text"} for c in chunks])

    return {"status": "ok", "message": f"Stored {len(texts)} chunks in FAISS index."}

def search_top_k(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Embed query, search normalized IP index (cosine), return top-k chunks + scores."""
    if index.ntotal == 0:
        return []

    q = model.encode([query], convert_to_numpy=True, show_progress_bar=False).astype("float32")
    q = _normalize(q)
    scores, ids = index.search(q, k)   # inner product == cosine similarity (because normalized)
    ids = ids[0]
    scores = scores[0]

    results: List[Dict[str, Any]] = []
    for idx, sc in zip(ids, scores):
        if idx < 0:
            continue
        results.append({
            "text": doc_texts[idx],
            "score": float(sc),
            "meta": doc_meta[idx]
        })
    return results
