from fastapi import APIRouter, UploadFile, File
from app.services.ingestion_service import ingest_document
from app.services.qdrant_service import get_qdrant_client
from qdrant_client import models

router = APIRouter()


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    contents = await file.read()
    with open(file.filename, "wb") as f:
        f.write(contents)
    ingest_document(file.filename, file.filename)
    return {"status": "ok", "filename": file.filename}


@router.get("/documents")
def list_documents():
    client = get_qdrant_client()
    points, _ = client.scroll(
        collection_name="documents",
        limit=10000,
        with_payload=True,
        with_vectors=False,
    )
    dokumente = {}
    for p in points:
        titel = p.payload.get("source_title", "Unbekannt")
        if titel not in dokumente:
            dokumente[titel] = {
                "id": titel,
                "title": titel,
                "type": p.payload.get("source_type", "?"),
                "chunk_count": 0,
            }
        dokumente[titel]["chunk_count"] += 1
    return list(dokumente.values())


@router.delete("/document/{doc_id}")
def delete_document(doc_id: str):
    client = get_qdrant_client()
    client.delete(
        collection_name="documents",
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_title",
                        match=models.MatchValue(value=doc_id),
                    )
                ]
            )
        ),
    )
    return {"status": "deleted", "document": doc_id}