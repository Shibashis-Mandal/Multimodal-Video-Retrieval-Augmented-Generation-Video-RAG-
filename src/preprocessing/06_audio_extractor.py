# Import required libraries

import subprocess                   # Run FFmpeg commands
from pathlib import Path            # Handle file and folder paths


class AudioExtractor:
    """Extracts audio from every video using FFmpeg."""

    def __init__(self, video_directory):

        # Folder containing videos
        self.video_directory = Path(video_directory)

        # Folder to save extracted audio
        self.audio_directory = Path("data/audio")

        # Create audio folder if it doesn't exist
        self.audio_directory.mkdir(parents=True, exist_ok=True)

    def get_video_list(self):

        # Return all MP4 videos
        return sorted(self.video_directory.glob("*.mp4"))

    def extract_audio(self, video_path):

        print(f"\nProcessing {video_path.name}")

        # Create output audio filename
        audio_file = self.audio_directory / f"{video_path.stem}.wav"

        # FFmpeg command
        command = [

            "ffmpeg",

            "-i", str(video_path),

            "-vn",

            "-acodec", "pcm_s16le",

            "-ar", "16000",

            "-ac", "1",

            "-y",

            str(audio_file)

        ]

        # Execute FFmpeg command
        subprocess.run(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

        print(f"✓ Audio saved -> {audio_file.name}")

    def process_all_videos(self):

        # Read all videos
        videos = self.get_video_list()

        print(f"\nFound {len(videos)} videos.\n")

        # Process every video
        for index, video in enumerate(videos, start=1):

            print(f"[{index}/{len(videos)}]")

            self.extract_audio(video)

        print("\nAudio extraction completed successfully.")


if __name__ == "__main__":

    # Create AudioExtractor object
    extractor = AudioExtractor("data/videos")

    # Process all videos
    extractor.process_all_videos()