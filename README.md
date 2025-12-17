# PDF Insight Assistant Pro

A production style PDF upload and chat system using FastAPI, Streamlit, LangChain, Groq, FAISS, and local embeddings.

Key features
1. PDF upload with validation, stored on disk
2. Per document vector index using FAISS
3. Chat with retrieval augmented generation, answers in Bengali, sources returned with page numbers
4. Session based memory per document
5. Prompt versioning and typed config
6. Logging, health endpoint, simple tests
7. Docker ready

## Prerequisites
1. Python 3.10 or newer
2. A Groq API key

## Setup
Create a `.env` file in the project root
```
GROQ_API_KEY=your_key_here
```

Install dependencies
```
pip install -r requirements.txt
```

## Run backend
```
uvicorn app.main:app --reload
```

Backend will start at `http://127.0.0.1:8000`.

## Run UI
In a new terminal
```
streamlit run ui/streamlit_app.py
```

## API quick test
Upload a PDF
```
curl -F "file=@your.pdf" http://127.0.0.1:8000/upload
```

Ask a question
```
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"doc_id":"<doc_id_from_upload>","session_id":"s1","question":"এই ডকুমেন্টে প্রধান ফলাফল কী","top_k":5}'
```

## Notes for real production
For real multi user production
1. Use object storage for PDFs
2. Use a database for document metadata
3. Use Redis for chat history
4. Use a managed vector database if you need scale
