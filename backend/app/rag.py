# app/rag.py 

from dotenv import load_dotenv
import os
from pathlib import Path
from typing import List
from langchain_community.vectorstores import Chroma  # ✅ updated import
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain.chains.retrieval_qa.base import RetrievalQA

# ✅ Fallback token estimator (replaces tiktoken)
def rough_token_len(text: str) -> int:
    return len(text) // 4  # approx. 1 token ≈ 4 characters

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing. Put it in backend/.env")

BASE_PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"

def _get_embeddings():
    return OpenAIEmbeddings(api_key=OPENAI_API_KEY)

def get_vectorstore(user_id: str) -> Chroma:
    user_dir = BASE_PERSIST_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name="default",
        persist_directory=str(user_dir),
        embedding_function=_get_embeddings(),
    )

def add_docs_to_vectorstore(file_paths: List[str], user_id: str) -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=rough_token_len  # ✅ use fallback
    )
    docs: List[Document] = []

    for fp in file_paths:
        fp = Path(fp)
        if not fp.exists():
            continue
        if fp.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(fp))
        else:
            loader = TextLoader(str(fp), encoding="utf-8")
        loaded = loader.load()
        docs.extend(loaded)

    if not docs:
        return 0

    chunks = splitter.split_documents(docs)
    vs = get_vectorstore(user_id)

    try:
        vs.add_documents(chunks)
        vs.persist()
        print(f"✅ Added {len(chunks)} chunks to vectorstore for user {user_id}")
    except Exception as e:
        print(f"❌ Error during vectorstore ingest: {str(e)}")
        return 0

    return len(chunks)

def query_agent(question: str, user_id: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)

    try:
        vs = get_vectorstore(user_id)
        retriever = vs.as_retriever(search_kwargs={"k": 4})
        chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        out = chain.invoke({"query": question})
        return out["result"]
    except Exception as e:
        print(f"⚠️ Error in retrieval, falling back to LLM only: {str(e)}")
        resp = llm.invoke(question)
        return resp.content
