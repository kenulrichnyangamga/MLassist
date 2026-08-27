from sentence_transformers import SentenceTransformer
from app.services.qdrant_service import get_qdrant_client
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def search_relevant_chunks(question):
    query_vector = embedding_model.encode(question).tolist()
    client = get_qdrant_client()
    results = client.query_points(
        collection_name="documents",
        query=query_vector,
        limit=5
    ).points
    return results


def _baue_prompt(question, context, mode="A", code_context=None):
    grundregeln = """Du bist ein hilfreicher Lernassistent für Studierende im Bereich Python-Programmierung und Machine Learning.

Dein Fachgebiet ist ausschließlich Python und Machine Learning (einschließlich Bibliotheken wie NumPy, pandas, scikit-learn und XGBoost). Liegt eine Frage klar außerhalb dieses Bereichs, weise höflich darauf hin, dass du nur bei Themen rund um Python und Machine Learning unterstützen kannst, und beantworte sie nicht.

Gib KEINE vollständige Lösung – nur Hinweise und Denkrichtungen, die den Studierenden zum eigenständigen Nachdenken anregen."""

    if mode == "B" and code_context:
        modus_anweisung = f"""Der Studierende hat folgenden Code eingereicht:

{code_context}

Deine Aufgabe ist es, ihm zu helfen, das Problem in seinem Code SELBST zu finden.
Analysiere dazu den eingereichten Code. Der zusätzlich bereitgestellte Kontext aus den Vorlesungsunterlagen dient nur als mögliche Ergänzung und muss nicht zwingend Informationen zum Problem enthalten.
Weise auf die relevante Stelle oder das zugrunde liegende Konzept hin, ohne den korrigierten Code direkt anzugeben."""
    else:
        modus_anweisung = """Beantworte fachlich passende Fragen NUR auf Basis des folgenden Kontexts.
Deine Aufgabe ist es, dem Studierenden mögliche Lösungsansätze und Denkrichtungen aufzuzeigen, ohne die fertige Lösung vorwegzunehmen."""

    return f"""{grundregeln}

{modus_anweisung}

Kontext:
{context}

Frage: {question}

Antwort:"""


def _frage_llm(prompt):
    response = llm_client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def _baue_quellen(results):
    """Aus den Qdrant-Ergebnissen eine Quellenliste für das Frontend bauen."""
    quellen = []
    for r in results:
        quellen.append({
            "title": r.payload.get("source_title", "Unbekannt"),
            "page": r.payload.get("page_number"),  # None bei DOCX
            "score": r.score,
        })
    return quellen


def generate_answer(question, results, mode="A", code_context=None):
    context = ""
    for result in results:
        context += result.payload["content"] + "\n\n"

    prompt = _baue_prompt(question, context, mode, code_context)
    answer = _frage_llm(prompt)
    quellen = _baue_quellen(results)
    return answer, quellen


def generate_answer_from_text(question, context, mode="A", code_context=None):
    prompt = _baue_prompt(question, context, mode, code_context)
    return _frage_llm(prompt)