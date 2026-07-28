
# Creates timestamps from Sarvam transcript using shot timings,
# aligns transcript to detected shots,
# and generates semantic shot information.

import json
from pathlib import Path

from src.preprocessing.translator import Translator



# Audio Shot Aligner

class AudioShotAligner:

    def __init__(self):

        # Master JSON folder
        self.json_directory = Path("data/json")

        # Bengali -> English translator
        self.translator = Translator()

   
    # Get all Master JSON files
   
    def get_json_files(self):

        return sorted(

            self.json_directory.glob("*.json")

        )

    
    # Merge consecutive semantic shots
    

    def merge_semantic_shots(self, shots):

        semantic_shots = []

        current = None

        step_id = 1

        for shot in shots:

            text_bn = shot.get(
                "audio_text_bn",
                ""
            ).strip()

            text_en = shot.get(
                "audio_text_en",
                ""
            ).strip()

            # Ignore silent shots
            if text_bn == "":
                continue

            # First semantic step
            if current is None:

                current = {

                    "step_id": step_id,

                    "start_time": shot["start_time"],

                    "end_time": shot["end_time"],

                    "duration": shot["duration"],

                    "representative_frame":
                        shot["representative_frame"],

                    "audio_text_bn": text_bn,

                    "audio_text_en": text_en

                }

                continue

            # Same instruction -> merge
            if current["audio_text_bn"] == text_bn:

                current["end_time"] = shot["end_time"]

                current["duration"] = round(

                    current["end_time"]
                    -
                    current["start_time"],

                    2

                )

            else:

                semantic_shots.append(current)

                step_id += 1

                current = {

                    "step_id": step_id,

                    "start_time": shot["start_time"],

                    "end_time": shot["end_time"],

                    "duration": shot["duration"],

                    "representative_frame":
                        shot["representative_frame"],

                    "audio_text_bn": text_bn,

                    "audio_text_en": text_en

                }

        if current is not None:

            semantic_shots.append(current)

        return semantic_shots
       
    # Process One Master JSON
   

    def process_json(self, json_path):

        print(f"\nProcessing : {json_path.name}")

        
        # Load Master JSON
        

        with open(

            json_path,

            "r",

            encoding="utf-8"

        ) as file:

            master_json = json.load(file)

       
        # Read Audio Information
        
        audio_information = master_json.get(

            "audio_information",

            {}

        )

        transcript_bn = audio_information.get(

            "transcript_bn",

            ""

        ).strip()

        transcript_en = audio_information.get(

            "transcript_en",

            ""

        ).strip()

        if transcript_bn == "":

            print(" No transcript found.")

            return

       
        # Read Shot Information
        
        shots = master_json.get(

            "shot_information",

            []

        )

        if len(shots) == 0:

            print(" No shot information found.")

            return

        print(f"Total Shots : {len(shots)}")

        
        # Split Bengali Transcript into Sentences
        
        sentences_bn = [

            sentence.strip()

            for sentence in transcript_bn.split("।")

            if sentence.strip()

        ]

        # If transcript has no Bengali punctuation,
        # keep the whole transcript as one sentence.

        if len(sentences_bn) == 0:

            sentences_bn = [

                transcript_bn

            ]

        print(f"Transcript Sentences : {len(sentences_bn)}")

        
        # Translate Each Sentence
        
        sentences_en = []

        for sentence in sentences_bn:

            try:

                translated = self.translator.translate(

                    sentence

                )

            except Exception:

                translated = ""

            sentences_en.append(

                translated

            )

        
        # Initialize Shot Fields
        

        for shot in shots:

            shot["audio_text"] = ""

            shot["audio_text_bn"] = ""

            shot["audio_text_en"] = ""
               
        # Generate Timestamp Segments from Shot Timings
        

        timestamps = []

        total_shots = len(shots)

        total_sentences = len(sentences_bn)

        # Number of shots assigned to each sentence
        shots_per_sentence = max(

            1,

            round(total_shots / total_sentences)

        )

        sentence_index = 0

        for shot_index, shot in enumerate(shots):

            # Move to next sentence after enough shots
            if (

                shot_index != 0

                and

                shot_index % shots_per_sentence == 0

                and

                sentence_index < total_sentences - 1

            ):

                sentence_index += 1

            start_time = shot["start_time"]

            end_time = shot["end_time"]

            text_bn = sentences_bn[sentence_index]

            text_en = sentences_en[sentence_index]

           
            # Store timestamp
            

            timestamps.append(

                {

                    "start": start_time,

                    "end": end_time,

                    "text": text_bn

                }

            )

           
            # Update Shot Information
           

            shot["audio_text"] = text_bn

            shot["audio_text_bn"] = text_bn

            shot["audio_text_en"] = text_en

        print(

            f" Generated {len(timestamps)} timestamp segments"

        )

        
        # Save timestamps back into audio_information
       
        audio_information["timestamps"] = timestamps

        master_json["audio_information"] = audio_information
                
        # Generate Semantic Shot Information
       
        print("\nGenerating Semantic Shot Information...")

        semantic_shots = self.merge_semantic_shots(

            shots

        )

        print(

            f" Generated {len(semantic_shots)} semantic steps"

        )

       
        # Update Master JSON
       
        master_json["audio_information"] = audio_information

        master_json["shot_information"] = shots

        master_json["semantic_shot_information"] = semantic_shots

        print(" Master JSON Updated")
               
        # Save Updated Master JSON
       
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

        print(f" Updated -> {json_path.name}")

   
    # Process All JSON Files
    
    def process_all_json(self):

        json_files = self.get_json_files()

       
        print("Audio Shot Alignment Started")
       

        print(f"\nFound {len(json_files)} JSON files.\n")

        for json_file in json_files:

            self.process_json(

                json_file

            )

       
        print(" Audio Shot Alignment Completed")
       



# Main

if __name__ == "__main__":

    aligner = AudioShotAligner()

    aligner.process_all_json()