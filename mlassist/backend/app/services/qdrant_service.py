from qdrant_client import QdrantClient
from qdrant_client import models



def get_qdrant_client():
    return QdrantClient(host="localhost", port=6333)

def new_collection_creation():
    client = get_qdrant_client() # Einen Qdant client erstellen

    #Prüfen ob Collection bereits existiert

    existing = [c.name for c in client.get_collections().collections]

    if "documents" not in existing:
        client.create_collection(
            collection_name="documents",
            vectors_config=models.VectorParams(size=384,
            distance=models.Distance.COSINE
        )
     )
        print("Collection 'documents' wurde erstellt.")
    else:
        print("Collection 'documents' existiert bereits.")