from vectordb.vector_store import load_vector_store
from embeddings.embedding_model import load_embedding_model

embedding_model = load_embedding_model()
vector_db = None

def reload_vector_db():
    global vector_db
    vector_db = load_vector_store(embedding_model)

def search_documents(query, k=3):
    global vector_db
    if vector_db is None:
        reload_vector_db()

    if vector_db is None:
        return []

    docs = vector_db.similarity_search(query, k=k)
    return docs