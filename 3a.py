import subprocess
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

filename = datetime.now().strftime("org-%d%m%Y%H%M%S") + ".zip"

SOURCE = "/content/Zipp"
ZIP_NAME = f"/content/Zipp2/{filename}"
PASSWORD = os.getenv("PASSWORD")

# Use subprocess to run the 7z command in a standard Python environment
try:
    subprocess.run(
        [
            "7z",
            "a",
            "-tzip",
            ZIP_NAME,
            SOURCE,
            "-mx=0",
            f"-p{PASSWORD}",
            "-mem=AES256"
        ],
        check=True
    )
    print(f"Archive created successfully: {ZIP_NAME}")
except subprocess.CalledProcessError as e:
    print(f"An error occurred while creating the archive: {e}")
except FileNotFoundError:
    print("Error: '7z' utility is not installed or not found in the system PATH.")

