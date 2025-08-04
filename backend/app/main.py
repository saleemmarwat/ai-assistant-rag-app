from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os

from app import rag  # your rag.py with user-based vectorstore
from app.supabase_logger import insert_chat  # logging chat history

load_dotenv()
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Ingest Endpoint (file + user_id) ---
@app.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    print(f"📥 Received file: {file.filename} from user: {user_id}")

    file_path = Path(UPLOAD_DIR) / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    chunks = rag.add_docs_to_vectorstore([str(file_path)], user_id)
    print(f"✅ Ingested {chunks} chunks for user {user_id}")
    return {"message": f"{chunks} chunks ingested for user {user_id} from {file.filename}"}

# --- Query Endpoint (question + user_id) ---
class QueryRequest(BaseModel):
    query: str
    user_id: str

@app.post("/query")
async def query_question(req: QueryRequest):
    print(f"🤖 Received question from user_id: {req.user_id}")
    print(f"❓ Question: {req.query}")

    answer = rag.query_agent(req.query, req.user_id)
    print(f"💬 Answer: {answer}")

    # Prevent Supabase logging error from breaking response
    try:
        insert_chat(req.user_id, req.query, answer)
    except Exception as e:
        print(f"⚠️ Failed to log chat to Supabase: {e}")

    return {"answer": answer}
