import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Primary Model for Auditing
MODEL_NAME = "llama-3.3-70b-versatile" 
# Faster, cheaper model for the "Judge" evaluation logic
JUDGE_MODEL = "llama-3.1-8b-instant"

# Temperature mapping for benchmarking results
TEMP_MAP = {
    "Strict Auditor (Fact-Based)": 0.0,
    "Balanced Reviewer": 0.4,
    "Creative Strategist": 0.8
}

CHROMA_PATH = str(ROOT_DIR / "vector_db")
COLLECTION_NAME = "nike_policies"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
TOP_K = 4