from sentence_transformers import SentenceTransformer
from app.services.qdrant_service import get_qdrant_client
from openai import OpenAI
import os
from dotenv import load_dotenv



load_dotenv()

def search_relevant_chunks(question):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = model.encode(question).tolist()

    client = get_qdrant_client()
    results = client.query_points(
        collection_name="documents",
        query=query_vector,
        limit=5
    ).points
    return results

def generate_answer(question, results):
    context = ""
    for result in results:
        context += result.payload["content"] + "\n\n"

    prompt = f"""Du bist ein hilfreicher Lernassistent für Studierende.
Beantworte die Frage NUR auf Basis des folgenden Kontexts.
Gib KEINE vollständige Lösung – nur Hinweise und Denkrichtungen.

Kontext:
{context}

Frage: {question}

Antwort:"""

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content