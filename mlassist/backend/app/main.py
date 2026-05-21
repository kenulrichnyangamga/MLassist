# FastAPI zuerst importieren
from fastapi import FastAPI


app = FastAPI()

@app.get("/health")
def health():
    return {"status": "Ok"}