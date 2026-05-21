from langchain_community.document_loaders import PyPDFLoader
import os


def load_documents(data_path="data"):
    documents = []

    for file in os.listdir(data_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(data_path, file)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())

    return documents