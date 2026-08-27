from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from app.services.inference_service import (
    search_relevant_chunks,
    generate_answer,
    generate_answer_from_text,
)
from app.services.ingestion_service import extract_pdf, extract_pptx, extract_docx

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    code_context: Optional[str] = None
    mode: str = "A"


@router.post("/query")
async def query(request: QuestionRequest):
    results = search_relevant_chunks(request.question)
    answer, sources = generate_answer(request.question, results, request.mode, request.code_context)
    return {"answer": answer, "sources": sources}


@router.post("/test-query")
async def test_query(
    file: UploadFile = File(...),
    question: str = Form(...),
    mode: str = Form("A"),
    code_context: Optional[str] = Form(None),
):
    # Datei temporär speichern, um dieselben Extraktoren wie bei der Ingestion zu nutzen
    contents = await file.read()
    endung = os.path.splitext(file.filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=endung) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        if endung == ".pdf":
            seiten = extract_pdf(tmp_path)
        elif endung == ".pptx":
            seiten = extract_pptx(tmp_path)
        elif endung == ".docx":
            seiten = extract_docx(tmp_path)
        else:
            return {"answer": f"Nicht unterstütztes Format: {endung}"}

        # Seitentexte zu einem Kontext zusammenfügen (keine Speicherung in Qdrant)
        text = "\n".join(t for _, t in seiten if t and t.strip())
    finally:
        os.remove(tmp_path)  # temporäre Datei wieder löschen -> keine Persistenz

    answer = generate_answer_from_text(question, text, mode, code_context)
    return {"answer": answer}