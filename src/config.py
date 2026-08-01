"""Project configuration defaults (non-secret)."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file at the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

# Ingestion settings
PACKAGE_NAME = os.getenv("PACKAGE_NAME", "com.zeptoconsumerapp")
APP_STORE_ID = int(os.getenv("APP_STORE_ID", "1575323645"))
LOOKBACK_WEEKS = int(os.getenv("LOOKBACK_WEEKS", "10"))
MIN_WORD_COUNT = int(os.getenv("MIN_WORD_COUNT", "6"))

# Embeddings configuration
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "local")
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GROQ_EMBEDDING_MODEL = os.getenv("GROQ_EMBEDDING_MODEL", "nomic-embed-text-v1.5")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "128"))
EMBED_BATCH_SLEEP_S = float(os.getenv("EMBED_BATCH_SLEEP_S", "1.0"))

# LLM Chat Model configuration
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
ANALYSIS_SAMPLE_CAP = int(os.getenv("ANALYSIS_SAMPLE_CAP", "450"))
UNMET_NEEDS_SAMPLE_CAP = int(os.getenv("UNMET_NEEDS_SAMPLE_CAP", "300"))
ANALYSIS_BATCH_SIZE = int(os.getenv("ANALYSIS_BATCH_SIZE", "20"))
GROQ_CALL_SLEEP_S = float(os.getenv("GROQ_CALL_SLEEP_S", "0.5"))

# Reddit configurations
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "macos:com.discoveryengine.scraper:v1.0.0 (by /u/prodkins)")

# RAG chatbot
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "8"))
RAG_FETCH_K = int(os.getenv("RAG_FETCH_K", "40"))
RAG_MMR_LAMBDA = float(os.getenv("RAG_MMR_LAMBDA", "0.7"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.30"))
RAG_MAX_ANSWER_TOKENS = int(os.getenv("RAG_MAX_ANSWER_TOKENS", "512"))
RAG_USE_GROQ = os.getenv("RAG_USE_GROQ", "true").lower() == "true"
RAG_FALLBACK = os.getenv("RAG_FALLBACK", "true").lower() == "true"
USE_GROQ_SEGMENTATION = os.getenv("USE_GROQ_SEGMENTATION", "false").lower() == "true"
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
