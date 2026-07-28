
# Import Required Libraries


import os
import json
from pathlib import Path

from dotenv import load_dotenv
from sarvamai import SarvamAI

from src.preprocessing.translator import Translator


# Audio Transcriber


class AudioTranscriber:
    """
    Transcribes every extracted audio file using Sarvam AI
    and updates the Master JSON.
    """

    def __init__(self, audio_directory):

      
        # Load Environment Variables
       

        load_dotenv()

        api_key = os.getenv("SARVAM_API_KEY")

        if not api_key:

            raise ValueError(
                " SARVAM_API_KEY not found in .env"
            )

        # Sarvam Client
      
        self.client = SarvamAI(

            api_subscription_key=api_key

        )

      
        # Translator
        

        self.translator = Translator()

        
        # Directories
        

        self.audio_directory = Path(audio_directory)

        self.json_directory = Path("data/json")

        self.output_directory = Path("data/transcripts")

        self.output_directory.mkdir(

            parents=True,

            exist_ok=True

        )

    
    # Get Audio Files
    
    def get_audio_files(self):

        return sorted(

            self.audio_directory.glob("*.wav")

        )

    
    # Process One Audio File
    
    def process_audio(self, audio_file):

        print(f"\nProcessing {audio_file.name}")

        
        # Find Corresponding Master JSON
        
        master_json_path = (

            self.json_directory /

            f"{audio_file.stem}.json"

        )

        if not master_json_path.exists():

            print(

                f" Master JSON not found for {audio_file.stem}"

            )

            return

        
        # Load Master JSON
        

        with open(

            master_json_path,

            "r",

            encoding="utf-8"

        ) as file:

            master_json = json.load(file)
               
        # Create Speech-to-Text Job
        
        print("Creating Sarvam Job...")

        try:

            job = self.client.speech_to_text_job.create_job(

                model="saaras:v3",

                mode="transcribe",

                language_code="bn-IN",

                with_diarization=False

            )

            print(" Job Created")

        except Exception as e:

            print(f" Failed to create job:\n{e}")

            return

       
        # Upload Audio File
        
        print("Uploading Audio...")

        try:

            job.upload_files(

                file_paths=[

                    str(audio_file)

                ]

            )

            print(" Audio Uploaded")

        except Exception as e:

            print(f" Upload Failed:\n{e}")

            return

        
        # Start Job
       
        print("Starting Transcription...")

        try:

            job.start()

            print(" Job Started")

        except Exception as e:

            print(f" Failed to start job:\n{e}")

            return

        
        # Wait Until Completed
        
        print("Waiting for Sarvam AI...")

        try:

            job.wait_until_complete()

            print(" Transcription Completed")

        except Exception as e:

            print(f" Job Failed:\n{e}")

            return

        
        # Download Output Files
       
        print("Downloading Transcript...")

        try:

            job.download_outputs(

                output_dir=str(

                    self.output_directory

                )

            )

            print(" Transcript Downloaded")

        except Exception as e:

            print(f" Download Failed:\n{e}")

            return

       
        # Locate Downloaded JSON
       
        json_files = sorted(

            self.output_directory.glob("*.json"),

            key=lambda file: file.stat().st_mtime,

            reverse=True

        )

        if len(json_files) == 0:

            print(" No transcript JSON found.")

            return

        transcript_json = json_files[0]

        print(f"Using Transcript: {transcript_json.name}")

       
        # Load Transcript JSON
        

        with open(

            transcript_json,

            "r",

            encoding="utf-8"

        ) as file:

            result = json.load(file)
               
        # Bengali Transcript
       
        transcript_bn = result.get("transcript", "").strip()

        if transcript_bn == "":

            print(" Empty transcript received.")

            return

        print(" Bengali Transcript Loaded")

       
        # English Translation
       
        print("Translating to English...")

        try:

            transcript_en = self.translator.translate(

                transcript_bn

            )

            print(" English Translation Completed")

        except Exception as e:

            print(f"Translation Failed: {e}")

            transcript_en = ""

       
        # Extract Timestamps
        
        timestamps = []

        try:

            timestamp_data = result.get("timestamps", {})

            chunks = timestamp_data.get("chunks", [])

            starts = timestamp_data.get("start_time_seconds", [])

            ends = timestamp_data.get("end_time_seconds", [])

            if len(chunks) == len(starts) == len(ends):

                for text, start, end in zip(

                    chunks,

                    starts,

                    ends

                ):

                    timestamps.append({

                        "start": round(float(start), 2),

                        "end": round(float(end), 2),

                        "text": text.strip()

                    })

                print(f" {len(timestamps)} timestamps extracted")

            else:

                print(" Timestamp lengths do not match.")

        except Exception as e:

            print(f" Timestamp Extraction Failed: {e}")

            timestamps = []

        
        # Update Master JSON
       
        master_json["audio_information"] = {

            "transcript_bn": transcript_bn,

            "transcript_en": transcript_en,

            "timestamps": timestamps

        }

       
        # Save Master JSON
       
        with open(

            master_json_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                master_json,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(f" Updated -> {master_json_path.name}")
           
    # Process All Audio Files
    

    def process_all_audio(self):

        audio_files = self.get_audio_files()

        print(f"\nFound {len(audio_files)} audio files.\n")

        if len(audio_files) == 0:

            print(" No audio files found.")

            return

        for index, audio_file in enumerate(audio_files, start=1):

            print("=" * 70)

            print(f"[{index}/{len(audio_files)}] {audio_file.name}")

            print("=" * 70)

            try:

                self.process_audio(audio_file)

            except Exception as e:

                print(f" Error processing {audio_file.name}")

                print(e)

        print("\n" + "=" * 70)

        print(" Audio Transcription Completed Successfully")

        print("=" * 70)



# Main

if __name__ == "__main__":

    transcriber = AudioTranscriber(

        "data/audio"

    )

    transcriber.process_all_audio()