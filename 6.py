import glob
import os
import subprocess

# --- Configuration Settings ---
INPUT_DIR = "/content/Movies"
OUTPUT_DIR = "/content/Zipp"
WATERMARK = "/content/v2.png"
# ------------------------------

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Find all .mp4 files in the input directory
video_files = glob.glob(os.path.join(INPUT_DIR, "*.mp4"))

if not video_files:
    print(f"No .mp4 files found in {INPUT_DIR}")
else:
    for video in video_files:
        filename = os.path.basename(video)
        output_file = os.path.join(OUTPUT_DIR, filename)

        print(f"\nProcessing: {filename}")

        # Execute the ffmpeg command as a list to run natively in Python
        cmd = [
            "ffmpeg", "-y",
            "-hwaccel", "cuda",
            "-i", video,
            "-i", WATERMARK,
            "-filter_complex", "[1]scale=iw*0.15:-1,format=rgba,colorchannelmixer=aa=1[logo];[0][logo]overlay=15:15",
            "-c:v", "h264_nvenc",
            "-preset", "p1",
            "-cq", "23",
            "-b:v", "0",
            "-c:a", "copy",
            output_file
        ]
        
        #cmd = [
         #   "ffmpeg", "-y",
        #    "-i", video,
        #    "-i", WATERMARK,
        #    "-filter_complex",
        #    "[1]scale=iw*0.15:-1,format=rgba,colorchannelmixer=aa=1[logo];[0][logo]overlay=15:15",
        #    "-c:v", "libx264",
        #    "-preset", "ultrafast",
        #    "-crf", "23",
        #    "-c:a", "copy",
        #    output_file
       # ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Finished processing: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing '{filename}': {e}")
        except FileNotFoundError:
            print("Error: 'ffmpeg' command was not found. Please ensure it is installed on your system.")
            break

    print("\nAll done!")

