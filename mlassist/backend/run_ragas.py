import json
import pandas as pd
import os
from dotenv import load_dotenv

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_precision, context_recall, faithfulness
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

# --- LLM-Richter: läuft über die THM-ki6-API (VPN muss aktiv sein) ---
richter_llm = LangchainLLMWrapper(
    ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0,
        timeout=420,       # ki6 ist langsam -> großzügiges Timeout pro Aufruf
        max_retries=2,
    )
)

# --- Embeddings: lokal, dasselbe Modell wie im System ---
richter_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)

# --- Daten laden und zusammenführen ---
with open("evaluationsdatensatz.json", encoding="utf-8") as f:
    fragen = {e["id"]: e for e in json.load(f)}

df = pd.read_csv("evaluationsergebnisse.csv")

daten = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

for _, zeile in df.iterrows():
    fid = zeile["id"]
    if fid not in fragen:      # F19 (Photosynthese) überspringen
        continue
    kontexte = json.loads(zeile["abgerufene_kontexte"])
    daten["question"].append(zeile["frage"])
    daten["answer"].append(str(zeile["rag_antwort"]))
    daten["contexts"].append(kontexte)
    daten["ground_truth"].append(fragen[fid]["referenz"])

dataset = Dataset.from_dict(daten)

# --- Evaluation (sequenziell, damit ki6 nicht überlastet wird) ---
ergebnis = evaluate(
    dataset,
    metrics=[context_precision, context_recall],
    llm=richter_llm,
    embeddings=richter_embeddings,
    run_config=RunConfig(timeout=360, max_workers=1),
)

print("\n=== RAGAS-Ergebnisse ===")
print(ergebnis)

ergebnis.to_pandas().to_csv("ragas_ergebnisse.csv", index=False)
print("\nDetails gespeichert in: ragas_ergebnisse.csv")