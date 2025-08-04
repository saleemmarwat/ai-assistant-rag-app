# 🧠 AI Assistant with RAG, Supabase & FastAPI

This project is a **Retrieval-Augmented Generation (RAG)** based AI assistant that lets users:

- ✅ Upload documents (PDF/text)
- ✅ Ask natural language questions
- ✅ Store chat history per user
- ✅ Authenticate with Supabase
- ✅ Use OpenAI or any LLM for answers

---

## 🛠️ Stack

- ⚡ FastAPI (backend API)
- 🧠 OpenAI / LLMs (answering questions)
- 📦 Supabase (auth + DB)
- 🌐 Next.js (frontend)

---

## 🚀 How to Run

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your real keys in the new .env
uvicorn app.main:app --reload
