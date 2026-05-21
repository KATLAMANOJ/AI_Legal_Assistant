from langchain_community.vectorstores import FAISS
import os


def create_vector_store(chunks, embedding_model):
    vector_db = FAISS.from_documents(chunks, embedding_model)

    vector_db.save_local("vectorstore/faiss_index")

    return vector_db


def load_vector_store(embedding_model):
    if os.path.exists("vectorstore/faiss_index"):
        vector_db = FAISS.load_local(
            "vectorstore/faiss_index",
            embedding_model,
            allow_dangerous_deserialization=True
        )

        return vector_db

    return None