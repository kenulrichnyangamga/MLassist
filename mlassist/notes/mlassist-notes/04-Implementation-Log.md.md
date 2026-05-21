# MLAssist – Development Log

## Setup – Phase 1

### Was haben wir erreicht?
- Projektstruktur erstellt
- Virtuelle Umgebung aktiviert (venv)
- Pakete installiert (requirements.txt)
- Qdrant läuft lokal auf Port 6333
- FastAPI läuft auf Port 8000
- /health Endpunkt funktioniert

---

## Projektstruktur

mlassist/ ├── backend/ │ ├── app/ │ │ ├── **init**.py │ │ ├── main.py │ │ ├── routes/ │ │ │ └── **init**.py │ │ └── services/ │ │ └── **init**.py │ └── requirements.txt ├── frontend/ └── docker-compose.yml

---

## Befehle

### Virtuelle Umgebung
```bash
# Erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate
```

### Qdrant starten
```bash
docker run --name qdrant -p 6333:6333 qdrant/qdrant
```

### FastAPI starten
```bash
uvicorn app.main:app --reload
```

### Health Check
```bash
curl http://127.0.0.1:8000/health
# Erwartete Antwort: {"status": "ok"}
```

---

## Pakete (requirements.txt)

| Paket | Zweck |
|---|---|
| fastapi | Das Backend-Framework |
| uvicorn | Server der FastAPI ausführt |
| qdrant-client | Kommunikation mit Qdrant |
| sentence-transformers | Embedding-Modell |
| langchain | Orchestriert die RAG-Pipeline |
| pymupdf | Text aus PDFs extrahieren |
| python-pptx | Text aus Präsentationen extrahieren |
| python-docx | Text aus Word-Dokumenten extrahieren |
| python-multipart | Datei-Upload im Frontend |
| openai | OpenAI-kompatible API aufrufen |

---

## Wichtige URLs

| Dienst | URL |
|---|---|
| FastAPI | http://127.0.0.1:8000 |
| FastAPI Docs | http://127.0.0.1:8000/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## Konzepte

### Warum uvicorn?
FastAPI ist nur ein Framework — es kann keinen HTTP-Server selbst starten.
Uvicorn ist der asynchrone Server der FastAPI ausführt.
Asynchron = mehrere Anfragen gleichzeitig bearbeiten ohne zu blockieren.

### Warum virtuelle Umgebung?
Isolierter Ordner mit eigener Python-Installation.
Pakete die dort installiert werden beeinflussen den Rest des Systems nicht.
Jedes Projekt hat seine eigene Umgebung = keine Konflikte zwischen Projekten.

