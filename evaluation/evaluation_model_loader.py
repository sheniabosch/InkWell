import os
from dotenv import load_dotenv

from llama_index.llms.google_genai import GoogleGenAI
from evaluation.evaluation_config import EVALUATION_LLM_MODEL
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.llms.base import LlamaIndexLLMWrapper

from evaluation.evaluation_config import (
    EVALUATION_EMBEDDING_MODEL_NAME,
)
from src.config import EMBEDDING_CACHE_PATH


# Load environment variables from the .env file
load_dotenv()


def initialise_evaluation_llm() -> GoogleGenAI:
    """Initialises the GoogleGenAI LLM with core parameters from config."""

    api_key: str | None = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. "
            "Make sure it's set in your .env file."
        )

    return GoogleGenAI(
        api_key=api_key,
        model=EVALUATION_LLM_MODEL,
    )


def load_ragas_models(
) -> tuple[LlamaIndexLLMWrapper, HuggingFaceEmbeddings]:
    """
    Loads the LLM and embedding models
    required for Ragas evaluation.
    """
    print("--- 🧠 Loading Ragas LLM and Embeddings ---")

    llm_for_evaluation: GoogleGenAI = initialise_evaluation_llm()

    # Wrap the LlamaIndex LLM for compatibility with Ragas
    ragas_llm = LlamaIndexLLMWrapper(llm=llm_for_evaluation)

    # Initialise the embedding model Ragas will use for its metrics
    ragas_embeddings = HuggingFaceEmbeddings(
        model=EVALUATION_EMBEDDING_MODEL_NAME,
        cache_folder=EMBEDDING_CACHE_PATH.as_posix()
    )

    return ragas_llm, ragas_embeddings