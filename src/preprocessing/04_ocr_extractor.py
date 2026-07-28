
# Import Required Libraries
import json
from pathlib import Path
import easyocr


#OCR Extractor
class OCRExtractor:
    """
    Reads all representative frames and extracts Bengali + English text
    using EasyOCR. Updates only the 'ocr_text' field inside
    frame_information.
    """

    def __init__(self):

        # Master JSON folder
        self.json_directory = Path("data/json")

        print("Loading EasyOCR...")

        # Bengali + English OCR
        self.reader = easyocr.Reader(
            ['bn', 'en'],
            gpu=False
        )

        print(" OCR Model Loaded")

    
    def get_json_files(self):

        return sorted(self.json_directory.glob("*.json"))

   
    def process_json(self, json_path):

        print(f"\nProcessing {json_path.name}")

        with open(json_path, "r", encoding="utf-8") as file:

            master_json = json.load(file)

        frame_information = master_json.get("frame_information", [])

        if len(frame_information) == 0:

            print("No frame information found.")
            return

       

        for index, frame in enumerate(frame_information, start=1):

            image_path = Path(frame["frame_path"])

            print(
                f"Frame {index}/{len(frame_information)} : {image_path.name}"
            )

            if not image_path.exists():

                print(f"Missing frame : {image_path}")

                frame["ocr_text"] = ""

                continue

            try:

                result = self.reader.readtext(
                    str(image_path),
                    detail=0,
                    paragraph=True
                )

                extracted_text = " ".join(result).strip()

                frame["ocr_text"] = extracted_text

            except Exception as e:

                print(e)

                frame["ocr_text"] = ""

       
        master_json["frame_information"] = frame_information

        with open(json_path, "w", encoding="utf-8") as file:

            json.dump(
                master_json,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f" Updated -> {json_path.name}")

    

    def process_all_json(self):

        json_files = self.get_json_files()

        print(f"\nFound {len(json_files)} JSON files.\n")

        for json_file in json_files:

            self.process_json(json_file)

        print("\n OCR Extraction Completed Successfully")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    extractor = OCRExtractor()

    extractor.process_all_json()