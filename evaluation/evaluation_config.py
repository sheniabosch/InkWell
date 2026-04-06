from pathlib import Path

from ragas.metrics.base import Metric
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

# --- LLM Model Configuration ---
EVALUATION_LLM_MODEL: str = "gemini-2.5-flash-lite"

# --- Embedding Model Configuration ---+
EVALUATION_EMBEDDING_MODEL_NAME: str = "BAAI/bge-large-en-v1.5"

# --- Paths for Evaluation ---
EVALUATION_ROOT_PATH: Path = Path(__file__).parent
EVALUATION_RESULTS_PATH: Path = EVALUATION_ROOT_PATH / "evaluation_results/"
EXPERIMENTAL_VECTOR_STORES_PATH: Path = (
    Path(__file__).parent.parent
    / "local_storage"
    / "experimental_vector_stores/"
)

# --- Ragas Evaluation Metrics ---
EVALUATION_METRICS: list[Metric] = [
    Faithfulness(),
    ContextPrecision(),
    ContextRecall(),
]

# --- Sleep Timers for API Limits ---
SLEEP_PER_EVALUATION: int = 20
SLEEP_PER_QUESTION: int = 6


# --- Configuration for Chunking Strategy Evaluation ---
CHUNKING_STRATEGY_CONFIGS: list[dict[str, int]] = [
    {'size': 512, 'overlap': 50},
    {'size': 768, 'overlap': 115},
    {'size': 1024, 'overlap': 200},
]


# --- Cross-encoder Model for Reranking ---
RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# --- Configuration for Reranking Evaluation ---
RERANKER_CONFIGS: list[dict[str, int]] = [
    {'retriever_k': 10, 'reranker_n': 2},
    {'retriever_k': 10, 'reranker_n': 5},
    {'retriever_k': 20, 'reranker_n': 5},
]


# --- Query Rewrite Evaluation ---
# The 'best' reranker strategy found in the previous evaluation stage.
# IMPORTANT: You must update this with the values you found to be optimal.
BEST_RERANKER_STRATEGY: dict[str, int] = {'retriever_k': 10, 'reranker_n': 2}