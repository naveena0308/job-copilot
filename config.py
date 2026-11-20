"""
Configuration module for LinkedIn Job Copilot.
Manages file paths, email settings, skills ontology, and matching weights.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# File paths
PROFILE_PATH = BASE_DIR / "profile.json"
DEFAULT_RESUME_PATH = BASE_DIR / "Naveena_s_Resume___27_10_2026.pdf"
TRACKER_PATH = BASE_DIR / "tracker.json"
RESUMES_DIR = BASE_DIR / "generated_resumes"
RESUMES_DIR.mkdir(parents=True, exist_ok=True)

# Email Settings (Gmail SMTP)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "navirajan2003@gmail.com")
SENDER_NAME = os.getenv("SENDER_NAME", "Naveena N")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# Default target search keywords
DEFAULT_TARGET_ROLES = [
    "AI/ML Engineer",
    "Generative AI Engineer",
    "LLM Engineer",
    "Agentic AI Engineer",
    "Data Scientist",
    "MLOps Engineer",
]

DEFAULT_LOCATIONS = [
    "Bangalore",
    "Bengaluru",
    "Remote",
    "India",
    "Hybrid",
]

# Skills Taxonomy for Keyword Extraction and Categorization
TECH_SKILLS_TAXONOMY = {
    "Generative AI & LLMs": [
        "langgraph", "langchain", "llamaindex", "autogen", "crewai", "rag",
        "mcp", "model context protocol", "react", "prompt engineering",
        "embeddings", "vector database", "fine-tuning", "lora", "qlora",
        "gemini", "gpt-4", "claude", "vertex ai", "ollama", "hugging face",
        "transformers", "reranking", "agentic", "agents", "multi-agent"
    ],
    "Machine Learning & Deep Learning": [
        "python", "pytorch", "tensorflow", "keras", "scikit-learn",
        "numpy", "pandas", "scipy", "xgboost", "lightgbm", "catboost",
        "machine learning", "deep learning", "neural networks", "nlp",
        "computer vision", "yolo", "opencv", "efficientnet", "classification",
        "regression", "clustering", "hyperparameter tuning"
    ],
    "MLOps & Cloud Infrastructure": [
        "mlflow", "docker", "kubernetes", "k8s", "ci/cd", "git", "github actions",
        "aws", "s3", "ec2", "lambda", "gcp", "azure", "model monitoring",
        "experiment tracking", "batch inference", "model deployment"
    ],
    "Databases & Data Engineering": [
        "sql", "postgresql", "postgres", "pgvector", "chromadb", "pinecone",
        "weaviate", "qdrant", "snowflake", "bigquery", "etl", "data pipeline",
        "pymupdf", "data processing", "redis"
    ],
    "Backend & APIs": [
        "fastapi", "flask", "django", "next.js", "rest api", "graphql",
        "microservices", "asyncio", "httpx", "pydantic"
    ]
}

# Scoring Weights
SCORING_WEIGHTS = {
    "required_skills": 0.50,
    "role_relevance": 0.20,
    "experience_fit": 0.15,
    "preferred_skills": 0.15,
}

