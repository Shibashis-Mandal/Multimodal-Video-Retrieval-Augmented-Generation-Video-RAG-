
# Import Required Libraries


import cv2
import json
from pathlib import Path


# Frame Extractor


class FrameExtractor:
    """
    Extract one representative frame from every detected shot
    and update the Master JSON.
    """

    def __init__(self, video_directory):

        # Folder containing videos
        self.video_directory = Path(video_directory)

        # Folder containing Master JSON files
        self.json_directory = Path("data/json")

        # Folder to save extracted frames
        self.frame_directory = Path("data/frames")

        # Create folder if it doesn't exist
        self.frame_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    # Get Video List


    def get_video_list(self):

        return sorted(

            self.video_directory.glob("*.mp4")

        )

  
    # Extract Frames
    

    def extract_frames(self, video_path):

        print(f"\nProcessing {video_path.name}")

     
        # Open Master JSON
     

        json_file = self.json_directory / f"{video_path.stem}.json"

        with open(

            json_file,

            "r",

            encoding="utf-8"

        ) as file:

            master_json = json.load(file)

        # Read shot information
        shots = master_json.get(

            "shot_information",

            []

        )

        if len(shots) == 0:

            print("No shots found.")

            return

        
        # Open Video
       

        cap = cv2.VideoCapture(

            str(video_path)

        )

        fps = cap.get(

            cv2.CAP_PROP_FPS

        )

       
        # Folder for this video's frames
       

        video_frame_folder = self.frame_directory / video_path.stem

        video_frame_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        # Store frame metadata

        frame_information = []

      
        # Process Every Shot
     

        for shot in shots:

            start_time = shot["start_time"]

            end_time = shot["end_time"]

            middle_time = (start_time + end_time) / 2

            frame_number = int(

                middle_time * fps

            )

            cap.set(

                cv2.CAP_PROP_POS_FRAMES,

                frame_number

            )

            success, frame = cap.read()

            if not success:

                continue

            
            # Save Representative Frame
           

            image_name = f"{shot['shot_id']}.jpg"

            image_path = video_frame_folder / image_name

            cv2.imwrite(

                str(image_path),

                frame

            )
            # Update representative frame inside shot_information
            

            shot["representative_frame"] = str(image_path)

           
            # Store Frame Information
           

            frame_information.append({

                "frame_id": f"{video_path.stem}_{shot['shot_id']}_f1",

                "shot_id": shot["shot_id"],

                "timestamp": round(middle_time, 2),

                "frame_path": str(image_path),

                "ocr_text": ""

            })

            print(f" Saved {image_name}")

        
        # Update Master JSON
      

        master_json["shot_information"] = shots

        master_json["frame_information"] = frame_information

     
        # Save Updated JSON
    

        with open(

            json_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                master_json,

                file,

                indent=4,

                ensure_ascii=False

            )

        cap.release()

        print(f" Updated -> {json_file.name}")

    
    # Process All Videos


    def process_all_videos(self):

        videos = self.get_video_list()

        print(f"\nFound {len(videos)} videos.\n")

        for index, video in enumerate(videos, start=1):

            print(f"[{index}/{len(videos)}] Processing {video.name}")

            self.extract_frames(video)

        print("\n Frame Extraction Completed Successfully")



# Main


if __name__ == "__main__":

    extractor = FrameExtractor("data/videos")

    extractor.process_all_videos()