# =============================================================================
# Import Required Libraries
# =============================================================================

import json
import pickle

from pathlib import Path

from rank_bm25 import BM25Okapi


# =============================================================================
# BM25 Index Generator
# =============================================================================

class BM25IndexGenerator:

    def __init__(self):

        # ---------------------------------------------------------
        # Chunk Folder
        # ---------------------------------------------------------

        self.chunk_directory = Path(

            "data/chunks"

        )

        # ---------------------------------------------------------
        # Output Folder
        # ---------------------------------------------------------

        self.output_directory = Path(

            "data/bm25_index"

        )

        self.output_directory.mkdir(

            parents=True,

            exist_ok=True

        )

        print("\nLoading BM25 Index Generator...")

        print("✓ Ready")


    # =========================================================================
    # Get All Chunk Files
    # =========================================================================

    def get_chunk_files(self):

        return sorted(

            self.chunk_directory.glob(

                "*_chunks.json"

            )

        )
        # =========================================================================
    # Process One Chunk File
    # =========================================================================

    def process_chunk_file(

        self,

        chunk_file

    ):

        print(f"\nProcessing {chunk_file.name}")

        # ---------------------------------------------------------
        # Load Chunk File
        # ---------------------------------------------------------

        with open(

            chunk_file,

            "r",

            encoding="utf-8"

        ) as file:

            chunks = json.load(

                file

            )

        corpus = []

        chunk_metadata = []

        # ---------------------------------------------------------
        # Prepare Corpus
        # ---------------------------------------------------------

        for chunk in chunks:

            text = chunk["text"]

            # Simple tokenization
            tokens = text.lower().split()

            corpus.append(

                tokens

            )

            chunk_metadata.append(

                {

                    "chunk_id": chunk["chunk_id"],

                    "video_id": chunk["video_id"],

                    "type": chunk["type"],

                    "timestamp": chunk["timestamp"],

                    "text": chunk["text"]

                }

            )

        print(

            f"Prepared {len(corpus)} Chunks"

        )

        # ---------------------------------------------------------
        # Build BM25 Index
        # ---------------------------------------------------------

        bm25 = BM25Okapi(

            corpus

        )
            # ---------------------------------------------------------
    # Save BM25 Index
    # ---------------------------------------------------------

        index_file = self.output_directory / (

            chunk_file.name.replace(

                "_chunks.json",

                "_bm25.pkl"

            )

        )

        with open(

            index_file,

            "wb"

        ) as file:

            pickle.dump(

                bm25,

                file

            )

        # ---------------------------------------------------------
        # Save Chunk Metadata
        # ---------------------------------------------------------

        metadata_file = self.output_directory / (

            chunk_file.name.replace(

                "_chunks.json",

                "_metadata.json"

            )

        )

        with open(

            metadata_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                chunk_metadata,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(

            f"✓ BM25 Index Saved : {index_file.name}"

        )

        print(

            f"✓ Metadata Saved : {metadata_file.name}"

        )
        # =========================================================================
    # Process All Chunk Files
    # =========================================================================

    def process_all_chunk_files(

        self

    ):

        chunk_files = self.get_chunk_files()

        print("\n========================================")
        print("BM25 Index Generation Started")
        print("========================================")

        print(

            f"\nFound {len(chunk_files)} Chunk Files.\n"

        )

        for index, chunk_file in enumerate(

            chunk_files,

            start=1

        ):

            print(

                f"\n[{index}/{len(chunk_files)}] "

                f"Processing {chunk_file.name}"

            )

            self.process_chunk_file(

                chunk_file

            )

        print("\n========================================")
        print("✓ BM25 Index Generation Completed")
        print("========================================")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = BM25IndexGenerator()

    generator.process_all_chunk_files()