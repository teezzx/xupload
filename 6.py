import glob
import os
import subprocess

# --- Configuration Settings ---
INPUT_DIR = "/content/Movies"
OUTPUT_DIR = "/content/Zipp"
WATERMARK = "v2.png"
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

        # FFmpeg command (NVIDIA GPU)
        cmd = [
            "ffmpeg", "-y",
            "-hwaccel", "cuda",
            "-i", video,
            "-i", WATERMARK,
            "-filter_complex",
            "[1]scale=iw*0.15:-1,format=rgba,colorchannelmixer=aa=1[logo];[0][logo]overlay=15:15",
            "-c:v", "h264_nvenc",
            "-preset", "p1",
            "-cq", "23",
            "-b:v", "0",
            "-c:a", "copy",
            output_file
        ]

        # CPU version (uncomment if needed)
        # cmd = [
        #     "ffmpeg", "-y",
        #     "-i", video,
        #     "-i", WATERMARK,
        #     "-filter_complex",
        #     "[1]scale=iw*0.15:-1,format=rgba,colorchannelmixer=aa=1[logo];[0][logo]overlay=15:15",
        #     "-c:v", "libx264",
        #     "-preset", "ultrafast",
        #     "-crf", "23",
        #     "-c:a", "copy",
        #     output_file
        # ]

        try:
            subprocess.run(cmd, check=True)

            # Verify output file exists and is not empty
            if (
                os.path.exists(output_file)
                and os.path.getsize(output_file) > 0
            ):
                os.remove(video)
                print(f"Finished processing: {filename}")
                print(f"Deleted original file: {filename}")
            else:
                print(f"Output file missing or empty: {output_file}")
                print("Original file kept.")

        except subprocess.CalledProcessError as e:
            print(f"Error processing '{filename}': {e}")
            print("Original file kept.")

        except FileNotFoundError:
            print("Error: 'ffmpeg' command was not found.")
            break

        except Exception as e:
            print(f"Unexpected error while processing '{filename}': {e}")
            print("Original file kept.")

    print("\nAll done!")
