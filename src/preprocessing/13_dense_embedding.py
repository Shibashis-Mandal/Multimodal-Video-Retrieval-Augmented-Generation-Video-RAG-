# =============================================================================
# Import Required Libraries
# =============================================================================

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


# =============================================================================
# Dense Embedding Generator
# =============================================================================

class DenseEmbeddingGenerator:

    def __init__(self):

        # Chunk Folder
        self.chunk_directory = Path("data/chunks")

        # Output Folder
        self.embedding_directory = Path("data/embeddings")

        self.embedding_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        print("Loading Sentence Transformer...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Model Loaded")


    # -------------------------------------------------------------------------
    # Get Chunk Files
    # -------------------------------------------------------------------------

    def get_chunk_files(self):

        return sorted(

            self.chunk_directory.glob(
                "*_chunks.json"
            )

        )


    # -------------------------------------------------------------------------
    # Generate Embedding
    # -------------------------------------------------------------------------

    def generate_embedding(self, text):

        embedding = self.model.encode(

            text,

            convert_to_numpy=True

        )

        return embedding.tolist()


    # -------------------------------------------------------------------------
    # Process One Chunk File
    # -------------------------------------------------------------------------

    def process_chunk_file(self, chunk_file):

        print(f"\nProcessing {chunk_file.name}")

        with open(

            chunk_file,

            "r",

            encoding="utf-8"

        ) as file:

            chunks = json.load(file)

        embeddings = []

        for chunk in chunks:

            vector = self.generate_embedding(

                chunk["text"]

            )

            embeddings.append(

                {

                    "chunk_id": chunk["chunk_id"],

                    "video_id": chunk["video_id"],

                    "type": chunk["type"],

                    "timestamp": chunk["timestamp"],

                    "text": chunk["text"],

                    "embedding": vector

                }

            )

            print(

                f"Embedded -> {chunk['chunk_id']}"

            )

        output_file = (

            self.embedding_directory /

            chunk_file.name.replace(

                "_chunks",

                "_embeddings"

            )

        )

        with open(

            output_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                embeddings,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(f"Saved -> {output_file.name}")


    # -------------------------------------------------------------------------
    # Process All Chunk Files
    # -------------------------------------------------------------------------

    def process_all_chunks(self):

        chunk_files = self.get_chunk_files()

        print(f"\nFound {len(chunk_files)} chunk files.")

        for chunk_file in chunk_files:

            self.process_chunk_file(

                chunk_file

            )

        print("\nDense Embedding Generation Completed.")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = DenseEmbeddingGenerator()

    generator.process_all_chunks()