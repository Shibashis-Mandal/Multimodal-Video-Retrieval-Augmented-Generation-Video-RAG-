
# Import Required Libraries


import json
from pathlib import Path

from ultralytics import YOLO



# Object Detector

class ObjectDetector:
    """
    Detect objects from representative frames using YOLOv8
    and update the Master JSON.
    """

    def __init__(self):

        
        # Master JSON folder
       

        self.json_directory = Path("data/json")

        
        # YOLO Model
        

        print("Loading YOLOv8 Model...")

        self.model = YOLO("yolov8n.pt")

        print("YOLO Model Loaded")

    
    # Get all JSON files
    

    def get_json_files(self):

        return sorted(

            self.json_directory.glob("*.json")

        )

    
    # Detect Objects from One Image
    
    def detect_objects(self, image_path):

        results = self.model(

            str(image_path),

            verbose=False

        )

        detected_objects = []

        for result in results:

            for box in result.boxes:

                class_id = int(

                    box.cls[0]

                )

                class_name = self.model.names[

                    class_id

                ]

                confidence = round(

                    float(box.conf[0]),

                    2

                )

                x1, y1, x2, y2 = [

                    round(float(value), 2)

                    for value in box.xyxy[0]

                ]

                detected_objects.append(

                    {

                        "class_name": class_name,

                        "confidence": confidence,

                        "bbox": [

                            x1,

                            y1,

                            x2,

                            y2

                        ]

                    }

                )

        return detected_objects
       
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

        if len(frame_information) == 0:

            print("No frame information found.")

            return

        print(

            f"Total Frames : {len(frame_information)}"

        )

        
        # Store Object Detection Results
       

        object_detection = []

        
        # Process Every Representative Frame
        

        for frame in frame_information:

            image_path = Path(

                frame["frame_path"]

            )

            if not image_path.exists():

                print(

                    f"Missing : {image_path}"

                )

                continue

            print(

                f"Detecting -> {image_path.name}"

            )

            detected_objects = self.detect_objects(

                image_path

            )

            object_detection.append(

                {

                    "frame_id": frame["frame_id"],

                    "shot_id": frame["shot_id"],

                    "detected_objects": detected_objects

                }

            )

            print(

                f" {len(detected_objects)} objects detected"

            )
                    
        # Update Master JSON
        

        master_json["object_detection"] = object_detection

       
        # Save Updated JSON
       

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
            
    # Process All Master JSON Files
    

    def process_all_json(self):

        json_files = self.get_json_files()

       
        print("Object Detection Started")
       

        print(f"\nFound {len(json_files)} JSON files.\n")

        for index, json_file in enumerate(json_files, start=1):

            print(

                f"[{index}/{len(json_files)}] "

                f"{json_file.name}"

            )

            self.process_json(

                json_file

            )

       
        print(" Object Detection Completed")
        

# Main


if __name__ == "__main__":

    detector = ObjectDetector()

    detector.process_all_json()