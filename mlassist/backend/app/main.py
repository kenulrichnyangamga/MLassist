# FastAPI zuerst importieren
from fastapi import FastAPI
from app.services.qdrant_service import new_collection_creation


app = FastAPI()

@app.get("/health")
def health():
    return {"status": "Ok"}