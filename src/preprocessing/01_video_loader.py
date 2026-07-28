# Import required libraries

import cv2                          # Read video properties
import json                         # Create JSON files
from pathlib import Path            # Handle file and folder paths


class VideoLoader:
    """Loads videos and creates one Master JSON for each video."""

    def __init__(self, video_directory):

        # Folder containing input videos
        self.video_directory = Path(video_directory)

        # Folder where Master JSON files will be stored
        self.json_directory = Path("data/json")

        # Create folder if it doesn't exist
        self.json_directory.mkdir(parents=True, exist_ok=True)

    def get_video_list(self):

        # Return all MP4 videos
        return sorted(self.video_directory.glob("*.mp4"))

    def load_video(self, video_path):

        # Open the video
        cap = cv2.VideoCapture(str(video_path))

        # Stop if video cannot be opened
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open {video_path}")

        return cap

    def get_video_metadata(self, cap, video_path):

        # Read video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate duration
        duration = round(total_frames / fps, 2) if fps else 0

        # Calculate file size
        file_size = round(video_path.stat().st_size / (1024 * 1024), 2)

        # Store video metadata
        video_info = {

            "video_id": video_path.stem,

            "video_name": video_path.name,

            "title": video_path.stem.replace("_", " ").title(),

            "category": "Cooking",

            "language": "Bengali",

            "creator": "Debisha",

            "duration": duration,

            "fps": fps,

            "width": width,

            "height": height,

            "total_frames": total_frames,

            "file_size": f"{file_size} MB",

            "video_path": str(video_path)

        }

        return video_info

    def create_master_json(self, video_info):

        # Create the Master JSON structure
        master_json = {

            "video_info": video_info,

            "recipe_information": {

                "dish_type": "",

                "ingredients": [],

                "estimated_steps": [],

                "cuisine": "",

                "tags": []

            },

            "audio_information": {

                "transcript_bn": "",

                "transcript_en": "",

                "timestamps": []

            },

            "shot_information": [],

            "frame_information": [],

            "object_detection": [],

            "visual_descriptions": []

        }

        # JSON filename
        output_file = self.json_directory / f"{video_info['video_id']}.json"

        # Save Master JSON
        with open(output_file, "w", encoding="utf-8") as file:

            json.dump(master_json, file, indent=4, ensure_ascii=False)

        print(f" Master JSON created -> {output_file.name}")

    def process_all_videos(self):

        # Read all videos
        videos = self.get_video_list()

        print(f"\nFound {len(videos)} videos.\n")

        # Process each video
        for index, video in enumerate(videos, start=1):

            print(f"[{index}/{len(videos)}] Processing {video.name}")

            # Open video
            cap = self.load_video(video)

            # Extract metadata
            video_info = self.get_video_metadata(cap, video)

            # Create Master JSON
            self.create_master_json(video_info)

            # Release memory
            cap.release()

        print("\nMaster JSON creation completed successfully.")


if __name__ == "__main__":

    # Create VideoLoader object
    loader = VideoLoader("data/videos")

    # Process all videos
    loader.process_all_videos()