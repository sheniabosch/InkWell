from datasets import Dataset

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.query_engine import (
    BaseQueryEngine,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
import pandas as pd
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.llms.base import LlamaIndexLLMWrapper

from evaluation.evaluation_helper_functions import (
    # ... all the other imports
    evaluate_without_rate_limit,
    evaluate_with_rate_limit, # <-- Add this line
)

from evaluation.evaluation_helper_functions import (
    generate_qa_dataset,
    get_evaluation_data,
    get_or_build_index,
    save_results,
    evaluate_without_rate_limit,
    evaluate_with_rate_limit,
)

from evaluation.evaluation_model_loader import load_ragas_models
from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    SIMILARITY_TOP_K,
)
from src.model_loader import get_embedding_model, initialise_llm


from evaluation.evaluation_config import (
    CHUNKING_STRATEGY_CONFIGS,
)

# Add to existing llama-index.core imports
from llama_index.core.query_engine import RetrieverQueryEngine # <-- Add this line
from llama_index.core.postprocessor import SentenceTransformerRerank # <-- Add this line

# Add to existing llama-index.core imports
from llama_index.core.query_engine import TransformQueryEngine # <-- Add this line
from llama_index.core.indices.query.query_transform import HyDEQueryTransform # <-- Add this line

# Add the new configs to the import from evaluation.evaluation_config
from evaluation.evaluation_config import (
    # ... existing imports
    CHUNKING_STRATEGY_CONFIGS,
    RERANKER_MODEL_NAME, # <-- Add this line
    RERANKER_CONFIGS, # <-- Add this line
    BEST_RERANKER_STRATEGY, # <-- Add this line
#    BEST_CHUNKING_STRATEGY, # recently added
)


def evaluate_baseline() -> None:
    """
    Evaluates the RAG system using only the settings from config.py.
    """
    print("--- 🚀 Stage 1: Evaluating Baseline Configuration ---")

    llm_to_test: GoogleGenAI = initialise_llm()

    embed_model_to_test: HuggingFaceEmbedding = get_embedding_model()

    questions: list[str]
    ground_truths: list[str]
    questions, ground_truths = get_evaluation_data()

    index: VectorStoreIndex = get_or_build_index(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        embed_model=embed_model_to_test
    )

    query_engine: BaseQueryEngine = index.as_query_engine(
        similarity_top_k=SIMILARITY_TOP_K,
        llm=llm_to_test
    )

    qa_dataset: Dataset = generate_qa_dataset(
        query_engine,
        questions,
        ground_truths
    )

    print("--- Running Ragas evaluation for baseline... ---")

    ragas_llm: LlamaIndexLLMWrapper
    ragas_embeddings: HuggingFaceEmbeddings
    ragas_llm, ragas_embeddings = load_ragas_models()

    results_df: pd.DataFrame = evaluate_with_rate_limit(
        qa_dataset,
        ragas_llm,
        ragas_embeddings,
    )


def evaluate_chunking_strategies() -> None:
    """ Evaluates different chunk sizes and overlaps. """
    print("\n--- 🚀 Stage 2: Evaluating Chunking Strategies ---")

    llm_to_test: GoogleGenAI = initialise_llm()

    embed_model_to_test: HuggingFaceEmbedding = get_embedding_model()

    questions, ground_truths = get_evaluation_data()

    ragas_llm: LlamaIndexLLMWrapper
    ragas_embeddings: HuggingFaceEmbeddings
    ragas_llm, ragas_embeddings = load_ragas_models()

    all_results: list[pd.DataFrame] = []

    for config in CHUNKING_STRATEGY_CONFIGS:

        chunk_size, chunk_overlap = config['size'], config['overlap']

        print(f"--- Testing Chunk Config: size={chunk_size}, "
              f"overlap={chunk_overlap} ---")

        index: VectorStoreIndex = get_or_build_index(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embed_model=embed_model_to_test
        )

        query_engine: BaseQueryEngine = index.as_query_engine(
            similarity_top_k=SIMILARITY_TOP_K,
            llm=llm_to_test
        )

        qa_dataset: Dataset = generate_qa_dataset(
            query_engine,
            questions,
            ground_truths
        )

        print("--- Running Ragas evaluation for chunking... ---")

        # --- If you don't have a Rate per Minute limit on your API ---
        # results_df: pd.DataFrame = evaluate_without_rate_limit(
        #     qa_dataset,
        #     ragas_llm,
        #     ragas_embeddings,
        # )

        # --- If you do have a Rate per Minute API limit ---
        results_df: pd.DataFrame = evaluate_with_rate_limit(
            qa_dataset,
            ragas_llm,
            ragas_embeddings,
        )

        # Add Chunk Size and Chunk Overlap to DataFrame to help tracking
        results_df['chunk_size'] = chunk_size
        results_df['chunk_overlap'] = chunk_overlap

        all_results.append(results_df)

    final_df: pd.DataFrame = pd.concat(all_results, ignore_index=True)

    save_results(final_df, "chunking_evaluation")

    print("--- ✅ Chunking Strategy Evaluation Complete ---")


    # Add Chunk Size and Chunk Overlap to DataFrame to help tracking
    results_df['chunk_size'] = CHUNK_SIZE
    results_df['chunk_overlap'] = CHUNK_OVERLAP

    save_results(results_df, "baseline_evaluation")

    print("--- ✅ Baseline Evaluation Complete ---")


def evaluate_reranker_strategies() -> None:
    """
    Evaluates different reranker settings on top of the best chunking strategy.
    """
    print("\n--- 🚀 Stage 3: Evaluating Reranker Strategies ---")

    llm_to_test: GoogleGenAI = initialise_llm()

    embed_model_to_test: HuggingFaceEmbedding = get_embedding_model()

    questions, ground_truths = get_evaluation_data()

    ragas_llm: LlamaIndexLLMWrapper
    ragas_embeddings: HuggingFaceEmbeddings
    ragas_llm, ragas_embeddings = load_ragas_models()

    index: VectorStoreIndex = get_or_build_index(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        embed_model=embed_model_to_test
    )

    all_results: list[pd.DataFrame] = []

    for config in RERANKER_CONFIGS:

        retriever_k, reranker_n = config['retriever_k'], config['reranker_n']

        print(f"--- Testing Reranker Config: retrieve_k={retriever_k},"
              f" rerank_n={reranker_n} ---")

        retriever = index.as_retriever(similarity_top_k=retriever_k)

        reranker = SentenceTransformerRerank(
            top_n=reranker_n, model=RERANKER_MODEL_NAME
        )

        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[reranker],
            llm=llm_to_test
        )

        qa_dataset: Dataset = generate_qa_dataset(
            query_engine,
            questions,
            ground_truths
        )

        print("--- Running Ragas evaluation for reranker... ---")

        # --- If you don't have a Rate per Minute limit on your API ---
        # results_df: pd.DataFrame = evaluate_without_rate_limit(
        #     qa_dataset,
        #     ragas_llm,
        #     ragas_embeddings,
        # )

        # --- If you do have a Rate per Minute API limit ---
        results_df: pd.DataFrame = evaluate_with_rate_limit(
            qa_dataset,
            ragas_llm,
            ragas_embeddings,
        )

        results_df['chunk_size'] = CHUNK_SIZE
        results_df['chunk_overlap'] = CHUNK_OVERLAP
        results_df['retriever_k'] = retriever_k
        results_df['reranker_n'] = reranker_n

        all_results.append(results_df)

    final_df: pd.DataFrame = pd.concat(all_results, ignore_index=True)

    save_results(final_df, "reranker_evaluation")

    print("--- ✅ Reranker Strategy Evaluation Complete ---")



def evaluate_query_rewriting() -> None:
    """ Evaluates the impact of HyDE on top of the best RAG configuration. """
    print("\n--- 🚀 Stage 4: Evaluating Query Rewriting (HyDE) ---")

    llm_to_test: GoogleGenAI = initialise_llm()

    embed_model_to_test: HuggingFaceEmbedding = get_embedding_model()

    questions, ground_truths = get_evaluation_data()

    # Use the best configurations from the config file
    best_retriever_k: int = BEST_RERANKER_STRATEGY['retriever_k']
    best_reranker_n: int = BEST_RERANKER_STRATEGY['reranker_n']

    index: VectorStoreIndex = get_or_build_index(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        embed_model=embed_model_to_test
    )

    ragas_llm: LlamaIndexLLMWrapper
    ragas_embeddings: HuggingFaceEmbeddings
    ragas_llm, ragas_embeddings = load_ragas_models()

    all_results: list[pd.DataFrame] = []

    # Test with and without HyDE
    for use_hyde in [False, True]:
        print(f"\n--- Testing Query Rewrite Config: use_hyde={use_hyde} ---")

        # Build the base query engine with retriever and reranker
        retriever = index.as_retriever(
            similarity_top_k=best_retriever_k
        )

        reranker = SentenceTransformerRerank(
            top_n=best_reranker_n,
            model=RERANKER_MODEL_NAME
        )

        base_query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[reranker],
            llm=llm_to_test
        )

        if use_hyde:
            hyde_transform = HyDEQueryTransform(
                llm=llm_to_test,
                include_original=True
            )
            query_engine = TransformQueryEngine(
                base_query_engine,
                query_transform=hyde_transform
            )
        else:
            # When not using HyDE, the engine is just the base engine
            query_engine = base_query_engine

        qa_dataset: Dataset = generate_qa_dataset(
            query_engine,
            questions,
            ground_truths
        )

        print("--- Running Ragas evaluation for query rewriting... ---")

        # --- If you don't have a Rate per Minute limit on your API ---
        # results_df: pd.DataFrame = evaluate_without_rate_limit(
        #     qa_dataset,
        #     ragas_llm,
        #     ragas_embeddings,
        # )

        # --- If you do have a Rate per Minute API limit ---
        results_df: pd.DataFrame = evaluate_with_rate_limit(
            qa_dataset,
            ragas_llm,
            ragas_embeddings,
        )

        results_df['chunk_size'] = CHUNK_SIZE
        results_df['chunk_overlap'] = CHUNK_OVERLAP
        results_df['retriever_k'] = best_retriever_k
        results_df['reranker_n'] = best_reranker_n
        results_df['use_hyde'] = use_hyde
        all_results.append(results_df)

    final_df: pd.DataFrame = pd.concat(all_results, ignore_index=True)

    save_results(final_df, "query_rewrite_evaluation")

    print("--- ✅ Query Rewrite Evaluation Complete ---")