# =============================================================================
# Import Required Libraries
# =============================================================================

import json
import pickle

from pathlib import Path

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
# =============================================================================
# Hybrid Retriever
# =============================================================================

class HybridRetriever:

    def __init__(self):

        # ChromaDB
        self.client = chromadb.PersistentClient(
            path="data/chroma_db"
        )

        self.collection = self.client.get_collection(
            "video_rag"
        )

        # BM25 Folder
        self.bm25_directory = Path(
            "data/bm25_index"
        )

        # Dense Embedding Model
        print("Loading SentenceTransformer...")

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("✓ Model Loaded")
# =============================================================================
# Generate Query Embedding
# =============================================================================

def generate_query_embedding(
    self,
    query
):

    embedding = self.embedding_model.encode(
        query,
        convert_to_numpy=True
    )

    return embedding.tolist()

HybridRetriever.generate_query_embedding = generate_query_embedding
# =============================================================================
# Dense Search
# =============================================================================

def dense_search(
    self,
    query,
    top_k=5
):

    print("\nPerforming Dense Search...")

    query_embedding = self.generate_query_embedding(
        query
    )

    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    dense_results = []

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(ids)):

        dense_results.append(
            {
                "chunk_id": ids[i],
                "text": documents[i],
                "video_id": metadatas[i]["video_id"],
                "type": metadatas[i]["type"],
                "timestamp": metadatas[i]["timestamp"],
                "score": distances[i]
            }
        )

    print(f"Retrieved {len(dense_results)} Dense Results")

    return dense_results

HybridRetriever.dense_search = dense_search
# =============================================================================
# Sparse Search
# =============================================================================

def sparse_search(
    self,
    query,
    top_k=5
):

    print("\nPerforming Sparse Search...")

    sparse_results = []

    query_tokens = query.lower().split()

    bm25_files = sorted(
        self.bm25_directory.glob("*_bm25.pkl")
    )

    for bm25_file in bm25_files:

        with open(bm25_file, "rb") as file:
            bm25 = pickle.load(file)

        metadata_file = bm25_file.with_name(
            bm25_file.name.replace(
                "_bm25.pkl",
                "_metadata.json"
            )
        )

        with open(metadata_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        scores = bm25.get_scores(query_tokens)

        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        for index in top_indices:

            sparse_results.append(
                {
                    "chunk_id": metadata[index]["chunk_id"],
                    "text": metadata[index]["text"],
                    "video_id": metadata[index]["video_id"],
                    "type": metadata[index]["type"],
                    "timestamp": metadata[index]["timestamp"],
                    "score": float(scores[index])
                }
            )

    sparse_results = sorted(
        sparse_results,
        key=lambda x: x["score"],
        reverse=True
    )

    print(f"Retrieved {len(sparse_results[:top_k])} Sparse Results")

    return sparse_results[:top_k]

HybridRetriever.sparse_search = sparse_search
# =============================================================================
# Hybrid Search
# =============================================================================

def hybrid_search(
    self,
    query,
    dense_k=5,
    sparse_k=5
):

    dense_results = self.dense_search(query, dense_k)

    sparse_results = self.sparse_search(query, sparse_k)

    hybrid_results = {}

    for result in dense_results:

        hybrid_results[result["chunk_id"]] = result
        hybrid_results[result["chunk_id"]]["retrieval"] = "Dense"

    for result in sparse_results:

        chunk_id = result["chunk_id"]

        if chunk_id in hybrid_results:
            hybrid_results[chunk_id]["retrieval"] = "Hybrid"
        else:
            hybrid_results[chunk_id] = result
            hybrid_results[chunk_id]["retrieval"] = "Sparse"

    final_results = list(hybrid_results.values())

    print(f"\nTotal Hybrid Results : {len(final_results)}")

    return final_results

HybridRetriever.hybrid_search = hybrid_search
# =============================================================================
# Process Query
# =============================================================================

def process_query(
    self,
    query
):

    print("\n========================================")
    print("Hybrid Retrieval Started")
    print("========================================")

    print(f"\nQuery : {query}")

    results = self.hybrid_search(query)

    print("\n========================================")
    print("Retrieved Chunks")
    print("========================================")

    for index, result in enumerate(results, start=1):

        print(f"\nRank : {index}")
        print(f"Chunk ID  : {result['chunk_id']}")
        print(f"Video ID  : {result['video_id']}")
        print(f"Type      : {result['type']}")
        print(f"Timestamp : {result['timestamp']}")
        print(f"Source    : {result['retrieval']}")
        print(f"Score     : {result['score']}")
        print(result["text"][:250])

    return results

HybridRetriever.process_query = process_query
# =============================================================================
# Main Execution
# =============================================================================

# Create Hybrid Retriever
retriever = HybridRetriever()

# Example Query
query = "when is milk added in caramel custard"

# Perform Hybrid Retrieval
results = retriever.process_query(
    query
)