from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from config import *
import numpy as np

# Initialize embeddings using the new partner package
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Initialize Chroma with the absolute path from config
vectordb = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME
)

def hybrid_search(query, k=TOP_K):
    # Fetch data from vector store for BM25
    all_data = vectordb.get()
    all_docs = all_data["documents"]
    all_metadatas = all_data["metadatas"]

    if not all_docs:
        return [], []

    # 1. Semantic search (Vector-based)
    semantic_results = vectordb.similarity_search(query, k=k)

    # 2. Keyword search (BM25-based)
    tokenized_docs = [doc.split() for doc in all_docs]
    bm25 = BM25Okapi(tokenized_docs)
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    
    # Get top k indices for keyword matches
    top_indices = np.argsort(scores)[-k:][::-1]

    keyword_results = []
    for idx in top_indices:
        keyword_results.append(Document(
            page_content=all_docs[idx],
            metadata=all_metadatas[idx]
        ))

    return semantic_results, keyword_results