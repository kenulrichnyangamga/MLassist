import json
import time
import csv

# --- Imports depuis ton projet (ajuste les chemins selon ton arborescence) ---
from app.services.inference_service import (
    search_relevant_chunks,
    generate_answer,
    llm_client,           # der OpenAI-Client aus deiner Datei
)
import os

# Fichiers d'entrée / sortie
EINGABE = "evaluationsdatensatz.json"
AUSGABE = "evaluationsergebnisse.csv"


def baseline_antwort(frage):
    """Antwort OHNE Retrieval: dieselbe Frage direkt an das LLM,
    ohne abgerufenen Kontext. Dient als Vergleichsbasis (Baseline)."""
    prompt = (
        "Du bist ein Lernassistent für Python und Machine Learning. "
        "Beantworte die folgende Frage.\n\n"
        f"Frage: {frage}\nAntwort:"
    )
    response = llm_client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def main():
    with open(EINGABE, encoding="utf-8") as f:
        fragen = json.load(f)

    zeilen = []
    antwortzeiten = []

    for eintrag in fragen:
        fid = eintrag["id"]
        frage = eintrag["frage"]
        print(f"Verarbeite {fid} ...")

        # --- RAG-Antwort mit Zeitmessung (R10 + RAGAS-Daten) ---
        start = time.time()
        results = search_relevant_chunks(frage)
        rag_antwort, quellen = generate_answer(frage, results, mode="A")
        dauer = time.time() - start
        antwortzeiten.append(dauer)

        # Abgerufener Kontext als Liste von Textabschnitten (für RAGAS)
        kontexte = [r.payload["content"] for r in results]

        # --- Baseline-Antwort ohne Retrieval (5.3) ---
        base_antwort = baseline_antwort(frage)

        zeilen.append({
            "id": fid,
            "thema": eintrag["thema"],
            "frage": frage,
            "referenzantwort": eintrag["referenz"],
            "rag_antwort": rag_antwort,
            "baseline_antwort": base_antwort,
            "abgerufene_kontexte": json.dumps(kontexte, ensure_ascii=False),
            "quellen": json.dumps(quellen, ensure_ascii=False),
            "antwortzeit_s": round(dauer, 2),
        })

    # --- Ergebnisse als CSV speichern ---
    with open(AUSGABE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(zeilen[0].keys()))
        writer.writeheader()
        writer.writerows(zeilen)

    # --- Zusammenfassung der Antwortzeiten (R10) ---
    schnitt = sum(antwortzeiten) / len(antwortzeiten)
    print("\n=== Antwortzeiten (R10) ===")
    print(f"Anzahl Fragen:      {len(antwortzeiten)}")
    print(f"Durchschnitt:       {schnitt:.2f} s")
    print(f"Minimum:            {min(antwortzeiten):.2f} s")
    print(f"Maximum:            {max(antwortzeiten):.2f} s")
    print(f"\nErgebnisse gespeichert in: {AUSGABE}")


if __name__ == "__main__":
    main()