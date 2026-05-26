# Core Concepts - MLAssist RAG System

## 1. RAG (Retrivial-Augmented Generation)

A technique that combines a **retrieval system** with a *language model*. Instead of replying only on the LLM's training data, the system first fetches relevant documents from a knowledge base, then uses them to generate the answer. 

**why it matters:** Reduces hallucinations. The LLM is grounded in real sources. 

---
## 2. Chunks
Large documents cannot be fed entirely to an LLM (context limit). 
So we split them into small overlapping pieces called **chunks** . 

-`chunk_size =512`-> each chunkbis max 512 characters
-`chunk_overlap = 64`-> chunks overlap by by 64 characters to preserve context

**why overlap?** So that an idea split across two chunks is still captured.

---
## 3. Embedding
The process of converting text into a **vector of numbers**. 
example: "How to use StandardScaler ?" -> `[0.23, -0.87, 0.41, ...]`(384 numbers) 

This allows the systems to measure **semantic similarity** between texts, even if they don't share the same words.

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`

## 4. Vector Database (Qdrant)
A database optimized for storing and searching vectors. Instead of SQL queries, you search by **similarity** (cosine distance). **In our project:** - Each chunk → embedded → stored as a Qdrant **Point** - A Point has: an ID, a vector, and a payload (metadata) - At query time: the question is embedded → Qdrant returns the top-5 closest chunks 

--- 

## 5. Inference Pipeline (per request) 
1. User sends a question (+ optional code) 
2. Question is embedded into a vector 
3. Qdrant returns top-5 most similar chunks 
4. Chunks + question → assembled into a prompt 
5. LLM generates an answer grounded in those chunks 
6. Answer + sources → sent back to the frontend 
---


## 6. Ingestion Pipeline (offline) 
1. Document uploaded (PDF, PPTX, DOCX) 
2. Text extracted (PyMuPDF / python-pptx / python-docx) 
3. Text split into chunks (RecursiveCharacterTextSplitter) 
4. Each chunk embedded (sentence-transformers) 
5. Vectors + metadata stored in Qdrant 
--- 

## 7. Mode A vs Mode B 
| | Mode A | Mode B | 
|---|---|---| 
| Input | Task description only | Task + code + specific question | | Output | Thinking directions, no solution | Targeted hints on the specific problem | | Detection | Automatic (no code detected) | Automatic (code block detected) |

# RAG – Universelle Prinzipien

## Die 7 Schritte – immer gleich

Diese Pipeline ist universell – sie ändert sich nie, egal welches RAG-Projekt.

---

## Was sich ändert

| Komponente | Unser Projekt | Alternativen |
|---|---|---|
| Vector DB | Qdrant | ChromaDB, Pinecone, Weaviate |
| Embedding | MiniLM | OpenAI, Cohere, mpnet |
| Chunking | RecursiveCharacterTextSplitter | SemanticChunker, FixedSize |
| LLM | OpenAI-compatible | Mistral, Llama, Claude |
| Framework | LangChain | LlamaIndex, from scratch |

---

## Die 3 kritischen Entscheidungen

### 1. chunk_size und chunk_overlap
- Zu groß → zu viele irrelevante Informationen → schlechte Präzision
- Zu klein → Kontext geht verloren → schlechte Antwort
- Optimaler Wert hängt immer vom Dokumenttyp ab

### 2. Das Embedding-Modell
- Muss bei der Ingestion UND bei der Query **dasselbe** sein
- Modell wechseln → alles neu indexieren

### 3. top_k
- Zu wenig Chunks → fehlende Information
- Zu viele Chunks → LLM wird überflutet
- Standard : 5 Chunks pro Anfrage

---

## Code den du immer wiederverwenden wirst

### Chunking
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64
)
chunks = splitter.split_text(text)
```

### Embedding
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)
```

### Qdrant Point erstellen
```python
from qdrant_client import models

point = models.PointStruct(
    id=i,
    vector=embedding.tolist(),
    payload={
        "content": chunk,
        "source_title": source_title,
        "source_type": source_type,
    }
)
```

### In Qdrant speichern
```python
client.upsert(
    collection_name="documents",
    points=points
)
```

---

## Das wichtigste Prinzip

> RAG ist eine klare Trennung zwischen **Gedächtnis** (Qdrant) 
> und **Intelligenz** (LLM).
> Qdrant findet – das LLM erklärt.
> Ohne diese Trennung halluziniert das LLM.

---

## Warum .tolist() ?
sentence-transformers gibt NumPy Arrays zurück.
Qdrant erwartet Python Listen.
.tolist() konvertiert NumPy Array → Python Liste.

## Warum upsert statt insert ?
upsert = update + insert
- Point existiert bereits → aktualisieren
- Point existiert nicht → neu erstellen
Flexibler als ein einfaches insert.

## Warum zip() ?
Verbindet chunks und embeddings parallel.
Chunk 1 gehört zu Embedding 1, Chunk 2 zu Embedding 2 usw.
Ohne zip() wüssten wir nicht welcher Vektor zu welchem Chunk gehört.

## Warum enumerate() ?
Fügt einen Zähler i hinzu.
Dieser Zähler wird als eindeutige ID des Points in Qdrant benutzt.