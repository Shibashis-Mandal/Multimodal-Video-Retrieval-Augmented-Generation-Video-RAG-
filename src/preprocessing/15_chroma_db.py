# =============================================================================
# Import Required Libraries
# =============================================================================

import json

from pathlib import Path

import chromadb


# =============================================================================
# ChromaDB Generator
# =============================================================================

class ChromaDBGenerator:

    def __init__(self):

        # ---------------------------------------------------------
        # Dense Embedding Folder
        # ---------------------------------------------------------

        self.embedding_directory = Path(

            "data/dense_embeddings"

        )

        # ---------------------------------------------------------
        # Chroma Database Folder
        # ---------------------------------------------------------

        self.database_directory = "data/chroma_db"

        # ---------------------------------------------------------
        # Create Persistent Client
        # ---------------------------------------------------------

        self.client = chromadb.PersistentClient(

            path=self.database_directory

        )

        # ---------------------------------------------------------
        # Create Collection
        # ---------------------------------------------------------

        self.collection = self.client.get_or_create_collection(

            name="video_rag"

        )

        print("\n========================================")
        print("ChromaDB Initialized")
        print("========================================")


    # =========================================================================
    # Get Dense Embedding Files
    # =========================================================================

    def get_dense_files(self):

        return sorted(

            self.embedding_directory.glob(

                "*_dense.json"

            )

        )
        # =========================================================================
    # Process One Dense Embedding File
    # =========================================================================

    def process_dense_file(

        self,

        dense_file

    ):

        print(f"\nProcessing {dense_file.name}")

        # ---------------------------------------------------------
        # Load Dense Embeddings
        # ---------------------------------------------------------

        with open(

            dense_file,

            "r",

            encoding="utf-8"

        ) as file:

            embedded_chunks = json.load(

                file

            )

        # ---------------------------------------------------------
        # Insert Each Chunk into ChromaDB
        # ---------------------------------------------------------

        for index, chunk in enumerate(

            embedded_chunks,

            start=1

        ):

            print(

                f"Inserting Chunk {index}/{len(embedded_chunks)}"

            )

            self.collection.add(

                ids=[

                    chunk["chunk_id"]

                ],

                embeddings=[

                    chunk["embedding"]

                ],

                documents=[

                    chunk["text"]

                ],

                metadatas=[

                    {

                        "video_id": chunk["video_id"],

                        "type": chunk["type"],

                        "timestamp": chunk["timestamp"]

                    }

                ]

            )

        print(

            f"✓ Inserted {len(embedded_chunks)} Chunks"

        )
        # =========================================================================
    # Process All Dense Embedding Files
    # =========================================================================

    def process_all_dense_files(

        self

    ):

        dense_files = self.get_dense_files()

        print("\n========================================")
        print("ChromaDB Population Started")
        print("========================================")

        print(

            f"\nFound {len(dense_files)} Dense Embedding Files.\n"

        )

        for index, dense_file in enumerate(

            dense_files,

            start=1

        ):

            print(

                f"\n[{index}/{len(dense_files)}] "

                f"Processing {dense_file.name}"

            )

            self.process_dense_file(

                dense_file

            )

        print("\n========================================")
        print("✓ ChromaDB Population Completed")
        print("========================================")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = ChromaDBGenerator()

    generator.process_all_dense_files()