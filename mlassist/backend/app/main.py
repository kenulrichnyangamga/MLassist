# FastAPI zuerst importieren
from fastapi import FastAPI
from app.services.qdrant_service import new_collection_creation
from app.routes.ingestion_route import router

app = FastAPI()
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "Ok"}

@app.on_event("startup")
async def startup():
    new_collection_creation()