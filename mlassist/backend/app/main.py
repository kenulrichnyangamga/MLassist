# FastAPI zuerst importieren
from fastapi import FastAPI
from app.services.qdrant_service import new_collection_creation
from app.routes.ingestion_route import router as ingestion_router
from app.routes.inference_route import router as inference_router

app = FastAPI()
app.include_router(ingestion_router)
app.include_router(inference_router)

@app.get("/health")
def health():
    return {"status": "Ok"}

@app.on_event("startup")
async def startup():
    new_collection_creation()