from fastapi import APIRouter, UploadFile, File
from app.services.ingestion_service import ingest_pdf


router = APIRouter()


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    contents = await file.read()
    with open(file.filename, "wb") as f:
        f.write(contents)
    ingest_pdf(file.filename, file.filename)
    return {"status": "ok", "filename": file.filename}