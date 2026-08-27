from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.qdrant_service import new_collection_creation
from app.routes.ingestion_route import router as ingestion_router
from app.routes.inference_route import router as inference_router

app = FastAPI()

# CORS AVANT les routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(inference_router)

@app.get("/health")
def health():
    return {"status": "Ok"}

@app.on_event("startup")
async def startup():
    new_collection_creation()