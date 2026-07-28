# =============================================================================
# Import Required Libraries
# =============================================================================

import json
from pathlib import Path

import ollama


# =============================================================================
# Recipe Information Generator
# =============================================================================

class RecipeInformationGenerator:

    def __init__(self):

        # Master JSON Folder
        self.json_directory = Path("data/json")

        print("Loading Gemma 3 Model...")

        # Ollama Model
        self.model_name = "gemma3:latest"

        print(f" Model Loaded : {self.model_name}")


    # =========================================================================
    # Get All Master JSON Files
    # =========================================================================

    def get_json_files(self):

        return sorted(

            self.json_directory.glob("*.json")

        )
    # =========================================================================
    # Generate Recipe Information using Gemma 3
    # =========================================================================

    def generate_recipe_information(

        self,

        transcript

    ):

        prompt = f"""
You are an expert cooking assistant.

Read the following cooking transcript carefully.

Extract the recipe information.

Return ONLY valid JSON in the following format.

{{
    "dish_type": "Recipe",
    "ingredients": [],
    "estimated_steps": [],
    "cuisine": "",
    "tags": []
}}

Rules:

1. dish_type
- Always return "Recipe".

2. ingredients
- Include only ingredient names.
- Do not include quantities.
- Remove duplicates.

3. estimated_steps
- Write 5 to 10 cooking steps.
- Keep them in chronological order.
- Each step should be one sentence.

4. cuisine
- Predict the cuisine if possible.
- Otherwise return "Unknown".

5. tags
- Return 3 to 6 relevant tags.

Transcript:

{transcript}

Return ONLY JSON.
"""

        try:

            response = ollama.chat(

                model=self.model_name,

                messages=[

                    {

                        "role": "user",

                        "content": prompt

                    }

                ]

            )

            output = response["message"]["content"].strip()

            # Remove markdown if present

            output = output.replace(

                "```json",

                ""

            )

            output = output.replace(

                "```",

                ""

            ).strip()

            recipe_information = json.loads(

                output

            )

            return recipe_information

        except Exception as e:

            print("\nRecipe Information Generation Failed")

            print(e)

            return {

                "dish_type": "",

                "ingredients": [],

                "estimated_steps": [],

                "cuisine": "",

                "tags": []

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
        # Read Audio Information
        # ---------------------------------------------------------

        audio_information = master_json.get(

            "audio_information",

            {}

        )

        transcript = audio_information.get(

            "transcript_en",

            ""

        )

        if transcript.strip() == "":

            print("No English transcript found.")

            return

        # ---------------------------------------------------------
        # Generate Recipe Information
        # ---------------------------------------------------------

        print("Generating Recipe Information...")

        recipe_information = self.generate_recipe_information(

            transcript

        )

        # ---------------------------------------------------------
        # Update Recipe Information
        # ---------------------------------------------------------

        master_json["recipe_information"]["dish_type"] = recipe_information.get(

            "dish_type",

            ""

        )

        master_json["recipe_information"]["ingredients"] = recipe_information.get(

            "ingredients",

            []

        )

        master_json["recipe_information"]["estimated_steps"] = recipe_information.get(

            "estimated_steps",

            []

        )
        master_json["recipe_information"]["cuisine"] = recipe_information.get(

            "cuisine",

            ""

        )

        master_json["recipe_information"]["tags"] = recipe_information.get(

            "tags",

            []

        )
        print(f"Full Path : {json_path.resolve()}")
        print(master_json["recipe_information"])

        # ---------------------------------------------------------
        # Save Updated Master JSON
        # ---------------------------------------------------------

        with open(

            json_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                master_json,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(" Recipe Information Updated")

        print(

            f"Ingredients Found : "

            f"{len(master_json['recipe_information']['ingredients'])}"

        )

        print(

            f"Steps Generated : "

            f"{len(master_json['recipe_information']['estimated_steps'])}"

        )
        # =========================================================================
    # Process All Master JSON Files
    # =========================================================================

    def process_all_json(

        self

    ):

        json_files = self.get_json_files()

        print("\n========================================")
        print("Recipe Information Generation Started")
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
        print(" Recipe Information Generation Completed")
        print("========================================")
# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = RecipeInformationGenerator()

    generator.process_all_json()