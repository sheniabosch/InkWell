from datasets import Dataset
from datetime import datetime
from pathlib import Path
import time
from typing import Any

from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import pandas as pd
from ragas.dataset_schema import EvaluationResult
from ragas.executor import Executor
from ragas.embeddings import HuggingFaceEmbeddings
from ragas import evaluate
from ragas.llms.base import LlamaIndexLLMWrapper

from evaluation.evaluation_config import (
    EVALUATION_RESULTS_PATH,
    EXPERIMENTAL_VECTOR_STORES_PATH,
    SLEEP_PER_QUESTION,
    SLEEP_PER_EVALUATION,
    EVALUATION_METRICS,
)
from evaluation.evaluation_questions import EVALUATION_DATA
from src.config import DATA_PATH


def get_evaluation_data() -> tuple[list[str], list[str]]:
    """
    Extracts questions and ground truths from the EVALUATION_DATA constant.
    """
    return [item["question"] for item in EVALUATION_DATA], [
        item["ground_truth"] for item in EVALUATION_DATA
    ]


def get_or_build_index(
    chunk_size: int, chunk_overlap: int, embed_model: HuggingFaceEmbedding
) -> VectorStoreIndex:
    """
    Checks for a persisted vector store for this experiment.
    If it exists, it loads it. If not, it builds it, persists it,
    and returns it.
    """
    vector_store_id: str = f"vs_chunk_{chunk_size}_overlap_{chunk_overlap}"
    specific_vector_store_path: Path = (
        EXPERIMENTAL_VECTOR_STORES_PATH
        / vector_store_id
    )

    if specific_vector_store_path.exists():
        print(f"--- Loading existing index from: {vector_store_id} ---")
        storage_context: StorageContext = StorageContext.from_defaults(
            persist_dir=str(specific_vector_store_path)
        )
        index: VectorStoreIndex = load_index_from_storage(
            storage_context, embed_model=embed_model
        )
    else:
        print(f"--- Creating new index for: {vector_store_id} ---")
        documents: list[Document] = SimpleDirectoryReader(
            input_dir=DATA_PATH
        ).load_data()

        text_splitter: SentenceSplitter = SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        index: VectorStoreIndex = VectorStoreIndex.from_documents(
            documents, transformations=[text_splitter], embed_model=embed_model
        )

        index.storage_context.persist(
            persist_dir=str(specific_vector_store_path)
        )
        print(f"--- Saved new index to: {vector_store_id} ---")
    return index

def generate_qa_dataset(
    query_engine: BaseQueryEngine,
    questions: list[str],
    ground_truths: list[str]
) -> Dataset:
    """
    Generates answers and contexts for a given query engine
    and returns a HuggingFace Dataset.
    """
    responses: list[str] = []
    contexts: list[list[str]] = []
    for question_index, question in enumerate(questions):
        print(
            "Fetching context and synthesising response for question "
            f"{question_index + 1}/{len(questions)}: '{question[:30]}...'"
        )
        response_object = query_engine.query(question)
        responses.append(str(response_object))
        contexts.append(
            [node.get_content() for node in response_object.source_nodes]
        )

        # If you are hitting API rate limits
        # You can slow down the rate with time.sleep
        #
        if question_index + 1 < len(questions):
            print(
                f"Taking a {SLEEP_PER_QUESTION} second breather "
                "to keep the API happy 🐢"
                )
            time.sleep(SLEEP_PER_QUESTION)
        else:
            continue

    response_data: dict[str, list[Any]] = {
        "question": questions,
        "answer": responses,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }

    return Dataset.from_dict(response_data)


def evaluate_without_rate_limit(
    qa_dataset: Dataset,
    ragas_llm: LlamaIndexLLMWrapper,
    ragas_embeddings: HuggingFaceEmbeddings,
) -> pd.DataFrame:
    """
    Runs Ragas evaluation on the entire dataset at once.
    Ideal for local models or APIs without strict rate limits.
    """
    print("--- ⚡ Running evaluation without rate limiting... ---")

    # Use ragas evaluation on the dataset
    result: EvaluationResult | Executor = evaluate(
        dataset=qa_dataset,
        metrics=EVALUATION_METRICS,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        raise_exceptions=True,
    )

    # Convert the evaluation result to a pandas DataFrame
    results_df: pd.DataFrame = result.to_pandas()

    print("--- ✅ Evaluation complete! ---")

    return results_df


def save_results(results_df: pd.DataFrame, filename_prefix: str) -> None:
    """Saves the evaluation results and summary to CSV files."""
    results_dir: Path = EVALUATION_RESULTS_PATH
    results_dir.mkdir(exist_ok=True, parents=True)
    timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    detailed_path: Path = (
        results_dir
        / f"{filename_prefix}_detailed_{timestamp}.csv"
    )
    results_df.to_csv(detailed_path, index=False)
    print(f"--- 💾 Detailed results saved to {detailed_path} ---")

    summary_path: Path = (
        results_dir
        / f"{filename_prefix}_summary_{timestamp}.csv"
    )
    # In the save_results function:
    param_cols: list[str] = [
        col
        for col in [
            'chunk_size',
            'chunk_overlap',
            'retriever_k',
            'reranker_n',
            'use_hyde']
        if col in results_df.columns
    ]

    if param_cols:
        avg_scores: pd.DataFrame = results_df.groupby(param_cols).mean(
            numeric_only=True
        )
        avg_scores.to_csv(summary_path)
        print(f"--- 💾 Summary of average scores saved to {summary_path} ---")



def evaluate_with_rate_limit(
    qa_dataset: Dataset,
    ragas_llm: LlamaIndexLLMWrapper,
    ragas_embeddings: HuggingFaceEmbeddings,
) -> pd.DataFrame:
    """
    Runs Ragas evaluation row-by-row to accommodate API rate limits,
    pausing between each evaluation.
    """
    print("--- 🐢 Running evaluation with rate limiting... ---")
    number_of_questions: int = len(qa_dataset)

    partial_results_list: list[pd.DataFrame] = []
    row: dict[str, Any]
    for i, row in enumerate(qa_dataset):
        print(
            f"Evaluating response for question {i + 1}/{number_of_questions}: "
            f"'{row['question'][:50]}...'"
        )

        # Create a new dataset with only one row to pass to evaluate
        single_row_dataset: Dataset = Dataset.from_dict(
            {key: [value] for key, value in row.items()}
        )

        # Evaluate just the single row
        result: EvaluationResult | Executor = evaluate(
            dataset=single_row_dataset,
            metrics=EVALUATION_METRICS,
            llm=ragas_llm,
            embeddings=ragas_embeddings,
            raise_exceptions=True,
        )

        # Convert the result to pandas DataFrame
        # Append the DataFrame to partial_results_list
        partial_results_list.append(result.to_pandas())

        # Pause to respect API rate limits, but not after the last item
        if i + 1 < number_of_questions:
            print(
                f"Taking a {SLEEP_PER_EVALUATION} second breather "
                "to keep the API happy."
            )
            time.sleep(SLEEP_PER_EVALUATION)

    # Combine the results from each row back into a single DataFrame
    results_df: pd.DataFrame = pd.concat(
        partial_results_list,
        ignore_index=True
    )

    print("--- ✅ Evaluation complete! ---")

    return results_df