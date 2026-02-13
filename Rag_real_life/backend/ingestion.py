import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import *

def load_pdfs(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return []
    
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            file_path = os.path.join(folder_path, file)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = file
            documents.extend(docs)
    return documents

def main():
    # Use absolute paths from config
    data_path = str(ROOT_DIR / "data")
    print(f"Reading PDFs from: {data_path}")
    
    docs = load_pdfs(data_path)
    if not docs:
        print("No documents found to process.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    split_docs = splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Persist to the absolute path defined in config
    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME
    )

    print(f"✅ Ingestion Complete. Total chunks stored in {CHROMA_PATH}: {len(split_docs)}")

if __name__ == "__main__":
    main()