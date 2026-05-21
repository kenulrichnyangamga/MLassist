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

