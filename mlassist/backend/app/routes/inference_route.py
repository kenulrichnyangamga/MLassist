from fastapi import APIRouter
from pydantic import BaseModel
from app.services.inference_service import search_relevant_chunks, generate_answer


router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/query")
async def query(request: QuestionRequest):
    results = search_relevant_chunks(request.question)
    answer = generate_answer(request.question, results)
    return {"answer": answer}