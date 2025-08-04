import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_chat(user_id: str, question: str, answer: str):
    response = supabase.table("chat_history").insert({
        "user_id": user_id,
        "question": question,
        "answer": answer
    }).execute()

    if response.error:
        print("Error inserting chat:", response.error)
