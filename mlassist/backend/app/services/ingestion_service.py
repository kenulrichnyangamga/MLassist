from qdrant_client import QdrantClient
from qdrant_client import models
import fitz 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.services.qdrant_service import get_qdrant_client


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc :
        text+= page.get_text()
    return text    

def text_into_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    chunks = splitter.split_text(text)
    return chunks

def chunks_toembeddings(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    return embeddings

def save_to_qdrant(chunks, embeddings, source_title, source_type):
    client = get_qdrant_client()
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point = models.PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload= {
                "content": chunk,
                "source_title": source_title,
                "source_type": source_type,
            }
        )
        points.append(point)

    client.upsert(
        collection_name="documents",
        points=points
        )
    
def ingest_pdf(pdf_path, source_title):
    text = extract_text_from_pdf(pdf_path)
    chunks = text_into_chunks(text)
    embeddings = chunks_toembeddings(chunks)
    save_to_qdrant(chunks, embeddings, source_title, "pdf")
    print(f"{len(chunks)} Chunks gespeichert aus '{source_title}'")