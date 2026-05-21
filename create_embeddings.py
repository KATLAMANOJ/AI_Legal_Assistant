from loaders.data_loader import load_documents
from utils.text_splitter import split_documents
from embeddings.embedding_model import load_embedding_model
from vectordb.vector_store import create_vector_store
import os

def main():
    print("Checking data directory...")
    if not os.path.exists("data"):
        print("Data directory 'data' does not exist!")
        return

    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} pages/documents.")

    if not documents:
        print("No documents found in the 'data' directory.")
        return

    print("Splitting documents...")
    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print("Loading embedding model...")
    embedding_model = load_embedding_model()

    print("Creating vector database...")
    create_vector_store(chunks, embedding_model)
    print("Vector database created and saved successfully in 'vectorstore/faiss_index'!")

if __name__ == "__main__":
    main()
