
# Import Required Libraries
from pathlib import Path
import json

from scenedetect import detect
from scenedetect.detectors import ContentDetector


# Shot Detector
class ShotDetector:
    """Detects shots and updates the Master JSON."""

    def __init__(self, video_directory):

        # Folder containing videos
        self.video_directory = Path(video_directory)

        # Folder containing Master JSON files
        self.json_directory = Path("data/json")

   
    # Get Video List
    def get_video_list(self):

        return sorted(self.video_directory.glob("*.mp4"))

    
    
    # Detect Shots
 

    def detect_shots(self, video_path):

        scene_list = detect(

            str(video_path),

            ContentDetector(threshold=27.0)

        )

        shots = []

        for shot_number, scene in enumerate(scene_list, start=1):

            start_time = round(scene[0].seconds, 2)

            end_time = round(scene[1].seconds, 2)

            shots.append({

                "shot_id": f"shot_{shot_number}",

                "start_time": start_time,

                "end_time": end_time,

                "duration": round(end_time - start_time, 2),

                "representative_frame": ""

            })

        return shots

    
    # Update Master JSON


    def update_master_json(self, video_name, shots):

        json_file = self.json_directory / f"{Path(video_name).stem}.json"

        if not json_file.exists():

            print(f"JSON not found: {json_file}")

            return

        with open(json_file, "r", encoding="utf-8") as file:

            master_json = json.load(file)

        master_json["shot_information"] = shots

        with open(json_file, "w", encoding="utf-8") as file:

            json.dump(

                master_json,

                file,

                indent=4,

                ensure_ascii=False

            )

        print(f" Updated -> {json_file.name}")

    # Process All Videos
   

    def process_all_videos(self):

        videos = self.get_video_list()

        print(f"\nFound {len(videos)} videos.\n")

        for index, video in enumerate(videos, start=1):

            print(f"[{index}/{len(videos)}] Processing {video.name}")

            shots = self.detect_shots(video)

            print(f"Detected {len(shots)} shots")

            self.update_master_json(video.name, shots)

        print("\n Shot Detection Completed")


# Main


if __name__ == "__main__":

    detector = ShotDetector("data/videos")

    detector.process_all_videos()