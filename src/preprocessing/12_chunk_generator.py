# =============================================================================
# Import Required Libraries
# =============================================================================

import json
from pathlib import Path


# =============================================================================
# Chunk Generator
# =============================================================================

class ChunkGenerator:

    def __init__(self):

        # ---------------------------------------------------------
        # Master JSON Folder
        # ---------------------------------------------------------

        self.json_directory = Path(

            "data/json"

        )

        # ---------------------------------------------------------
        # Output Chunk Folder
        # ---------------------------------------------------------

        self.chunk_directory = Path(

            "data/chunks"

        )

        # Create folder if it does not exist

        self.chunk_directory.mkdir(

            parents=True,

            exist_ok=True

        )

        print("\n========================================")
        print("Chunk Generator Initialized")
        print("========================================")


    # =========================================================================
    # Get All Master JSON Files
    # =========================================================================

    def get_json_files(self):

        return sorted(

            self.json_directory.glob(

                "*.json"

            )

        )
    # =========================================================================
    # Create Recipe Summary Chunk
    # =========================================================================

    def create_recipe_summary_chunk(

        self,

        video_id,

        recipe_information

    ):

        dish = recipe_information.get(

            "dish_type",

            ""

        )

        cuisine = recipe_information.get(

            "cuisine",

            ""

        )

        ingredients = ", ".join(

            recipe_information.get(

                "ingredients",

                []

            )

        )

        steps = " ".join(

            recipe_information.get(

                "estimated_steps",

                []

            )

        )

        text = (

            f"Dish: {dish}. "

            f"Cuisine: {cuisine}. "

            f"Ingredients: {ingredients}. "

            f"Steps: {steps}."

        )

        return {

            "chunk_id": f"{video_id}_summary",

            "video_id": video_id,

            "type": "recipe_summary",

            "timestamp": 0.0,

            "text": text

        }


    # =========================================================================
    # Create Frame Chunk
    # =========================================================================

    def create_frame_chunk(

        self,

        video_id,

        frame,

        visual_description,

        detected_objects

    ):

        frame_id = frame["frame_id"]

        shot_id = frame["shot_id"]

        timestamp = frame["timestamp"]

        ocr_text = frame.get(

            "ocr_text",

            ""

        )

        object_names = [

            obj["class_name"]

            for obj in detected_objects

        ]

        object_text = ", ".join(

            sorted(

                set(object_names)

            )

        )

        text = (

            f"At {timestamp:.2f}s. "

            f"Visual: {visual_description}. "

            f"OCR: {ocr_text}. "

            f"Objects: {object_text}."

        )

        return {

            "chunk_id":

                f"{video_id}_{shot_id}_{frame_id}",

            "video_id": video_id,

            "type": "frame_chunk",

            "timestamp": timestamp,

            "text": text

        }
    # =========================================================================
    # Process One Master JSON
    # =========================================================================

    def process_json(

        self,

        json_path

    ):

        print(f"\nProcessing {json_path.name}")

        # ---------------------------------------------------------
        # Load Master JSON
        # ---------------------------------------------------------

        with open(

            json_path,

            "r",

            encoding="utf-8"

        ) as file:

            master_json = json.load(

                file

            )

        # ---------------------------------------------------------
        # Read Required Sections
        # ---------------------------------------------------------

        video_info = master_json.get(

            "video_info",

            {}

        )

        recipe_information = master_json.get(

            "recipe_information",

            {}

        )

        frame_information = master_json.get(

            "frame_information",

            []

        )

        object_detection = master_json.get(

            "object_detection",

            []

        )

        visual_descriptions = master_json.get(

            "visual_descriptions",

            []

        )

        video_id = video_info.get(

            "video_id",

            "UNKNOWN_VIDEO"

        )

        # ---------------------------------------------------------
        # Create Lookup Dictionaries
        # ---------------------------------------------------------

        object_lookup = {

            item["frame_id"]: item["detected_objects"]

            for item in object_detection

        }

        visual_lookup = {

            item["frame_id"]: item["description"]

            for item in visual_descriptions

        }

        # ---------------------------------------------------------
        # Store All Chunks
        # ---------------------------------------------------------

        chunks = []

        # ---------------------------------------------------------
        # Recipe Summary Chunk
        # ---------------------------------------------------------

        recipe_chunk = self.create_recipe_summary_chunk(

            video_id,

            recipe_information

        )

        chunks.append(

            recipe_chunk

        )

        print(" Recipe Summary Chunk Created")
            # ---------------------------------------------------------
        # Generate Frame Chunks
        # ---------------------------------------------------------

        print(

            f"Generating Frame Chunks ({len(frame_information)} Frames)..."

        )

        for frame in frame_information:

            frame_id = frame["frame_id"]

            # ---------------------------------------------------------
            # Get Visual Description
            # ---------------------------------------------------------

            visual_description = visual_lookup.get(

                frame_id,

                ""

            )

            # ---------------------------------------------------------
            # Get Detected Objects
            # ---------------------------------------------------------

            detected_objects = object_lookup.get(

                frame_id,

                []

            )

            # ---------------------------------------------------------
            # Create Frame Chunk
            # ---------------------------------------------------------

            frame_chunk = self.create_frame_chunk(

                video_id,

                frame,

                visual_description,

                detected_objects

            )

            chunks.append(

                frame_chunk

            )

            print(

                f" Frame Chunk Created : {frame_id}"

            )
        # ---------------------------------------------------------
        # Save Chunk File
        # ---------------------------------------------------------

        chunk_file = self.chunk_directory / (

            f"{video_id}_chunks.json"

        )

        with open(

            chunk_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                chunks,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(

            f"\n Saved {len(chunks)} Chunks"

        )

        print(

            f"Chunk File : {chunk_file.name}"

        )


    # =========================================================================
    # Process All Master JSON Files
    # =========================================================================

    def process_all_json(

        self

    ):

        json_files = self.get_json_files()

        print("\n========================================")
        print("Chunk Generation Started")
        print("========================================")

        print(

            f"\nFound {len(json_files)} JSON files.\n"

        )

        for index, json_file in enumerate(

            json_files,

            start=1

        ):

            print(

                f"\n[{index}/{len(json_files)}] "

                f"Processing {json_file.name}"

            )

            self.process_json(

                json_file

            )

        print("\n========================================")
        print(" Chunk Generation Completed")
        print("========================================")
# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = ChunkGenerator()

    generator.process_all_json()