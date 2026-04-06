import os
from dotenv import load_dotenv

from llama_index.llms.google_genai import GoogleGenAI

from src.config import (
    LLM_MODEL,
    LLM_MAX_NEW_TOKENS,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    LLM_REPETITION_PENALTY
)


# Load environment variables from the .env file
load_dotenv()


def initialise_llm() -> GoogleGenAI:
    """Initialises the GoogleGenAI LLM with core parameters from config."""

    api_key: str | None = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. Make sure it's set in your .env file."
        )

    return GoogleGenAI(
        api_key=api_key,
        model=LLM_MODEL,
        # The following parameters are optional
        # and will default to the model's defaults if not set
        # max_new_tokens=LLM_MAX_NEW_TOKENS,
        # temperature=LLM_TEMPERATURE,
        # top_p=LLM_TOP_P,
    )


from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_CACHE_PATH,
)

def get_embedding_model() -> HuggingFaceEmbedding:
    """Initialises and returns the HuggingFace embedding model"""
    # Create the cache directory if it doesn't exist
    EMBEDDING_CACHE_PATH.mkdir(parents=True, exist_ok=True)

    return HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL_NAME,
        cache_folder=EMBEDDING_CACHE_PATH.as_posix()
    )
