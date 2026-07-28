
# Import Required Libraries

import json
from pathlib import Path

import ollama



# Visual Description Generator

class VisualDescriptionGenerator:

    def __init__(self):

        # Master JSON folder
        self.json_directory = Path("data/json")

        print("Loading Gemma 3...")

        # Text Model
        self.model_name = "gemma3:latest"

        print(f" Model Loaded : {self.model_name}")


   
    # Get all Master JSON files
    
    def get_json_files(self):

        return sorted(

            self.json_directory.glob("*.json")

        )
            
    # Generate Description using OCR + Objects + Transcript
    
    def generate_description(

        self,

        ocr_text,

        detected_objects,

        transcript

    ):

       
        # Convert detected objects into text
       
        object_names = []

        for obj in detected_objects:

            object_names.append(

                obj["class_name"]

            )

        object_text = ", ".join(

            sorted(

                set(object_names)

            )

        )

        if object_text == "":

            object_text = "None"

        if ocr_text.strip() == "":

            ocr_text = "None"

        if transcript.strip() == "":

            transcript = "None"

       
        # Prompt
        
        prompt = f"""
You are generating a visual description for a cooking video.

Use the following information:

OCR Text:
{ocr_text}

Detected Objects:
{object_text}

Recipe Transcript:
{transcript}

Generate ONLY one concise description (1-2 sentences).

Focus on:
- ingredients
- utensils
- cooking action
- food appearance

Do not mention OCR, transcript or object detection.
Do not invent information not supported by the provided inputs.
Return only the description.
"""

       
        # Call Gemma 3 (TEXT ONLY)
        
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

            return response["message"]["content"].strip()

        except Exception as e:

            print(e)

            return ""
        
    # Process One Master JSON
    
    def process_json(self, json_path):

        print(f"\nProcessing {json_path.name}")

        
        # Load Master JSON
        
        with open(

            json_path,

            "r",

            encoding="utf-8"

        ) as file:

            master_json = json.load(file)

        
        # Read Frame Information
        

        frame_information = master_json.get(

            "frame_information",

            []

        )

        
        # Read Object Detection
       
        object_detection = master_json.get(

            "object_detection",

            []

        )

        
        # Read Shot Information
       
        shot_information = master_json.get(

            "shot_information",

            []

        )

        if len(frame_information) == 0:

            print("No frame information found.")

            return

        print(

            f"Total Frames : {len(frame_information)}"

        )

        
        # Build Object Lookup
        

        object_lookup = {

            item["frame_id"]: item["detected_objects"]

            for item in object_detection

        }

       
        # Build Shot Lookup
       
        shot_lookup = {

            shot["shot_id"]: shot

            for shot in shot_information

        }

        
        # Existing Visual Descriptions
        

        visual_descriptions = master_json.get(

            "visual_descriptions",

            []

        )

        completed_frames = {

            item["frame_id"]

            for item in visual_descriptions

        }

        print(

            f"Already Completed : {len(completed_frames)}"

        )

        
        # Process Every Representative Frame
        

        for frame in frame_information:

            frame_id = frame["frame_id"]

            shot_id = frame["shot_id"]

           
            # Skip Already Processed Frames
            

            if frame_id in completed_frames:

                print(

                    f"Skipping {frame_id}"

                )

                continue

           
            # OCR
            
            ocr_text = frame.get(

                "ocr_text",

                ""

            )

            
            # Objects
            
            detected_objects = object_lookup.get(

                frame_id,

                []

            )

           
            # Transcript
            

            transcript = ""

            if shot_id in shot_lookup:

                transcript = shot_lookup[

                    shot_id

                ].get(

                    "audio_text_en",

                    ""

                )

            print(

                f"\nGenerating Description -> {frame_id}"

            )

            description = self.generate_description(

                ocr_text,

                detected_objects,

                transcript

            )
                 
            # Save Generated Description
            
            if description != "":

                visual_descriptions.append(

                    {
                        "frame_id": frame_id,

                        "shot_id": shot_id,

                        "timestamp": frame.get(
                            "timestamp",
                            0
                        ),

                        "description": description
                    }

                )


                completed_frames.add(frame_id)


               
                # Save Immediately (Checkpoint)
                

                master_json["visual_descriptions"] = visual_descriptions


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


                print(

                    f" Saved Description : {frame_id}"

                )


            else:

                print(

                    f" Failed Description : {frame_id}"

                )


        print(

            f"\nCompleted {json_path.name}"

        )

# Main Execution


if __name__ == "__main__":


    generator = VisualDescriptionGenerator()


    json_files = generator.get_json_files()


    print(
        f"\nTotal JSON Files Found : {len(json_files)}"
    )


    for json_file in json_files:

        generator.process_json(json_file)


    print(
        "\n================================="
    )

    print(
        "ALL VISUAL DESCRIPTIONS COMPLETED"
    )

    print(
        "================================="
    )