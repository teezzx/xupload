import os
import sys
import mimetypes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
# Your working credentials


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

FOLDER_ID = os.getenv("FOLDER_ID")        # The Admin's folder ID




LOCAL_FOLDER_PATH = '/content/Zipp2'    # Path to the local Colab folder containing the files

def upload_folder_files():
    # 1. Silently authenticate using the Refresh Token
    info = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    try:
        creds = Credentials.from_authorized_user_info(info)
        service = build('drive', 'v3', credentials=creds)

        # 2. Verify local folder exists
        if not os.path.exists(LOCAL_FOLDER_PATH):
            print(f"Error: Local folder '{LOCAL_FOLDER_PATH}' not found. Please verify the path.")
            return

        # 3. Get list of files in the directory (excluding subdirectories)
        all_items = os.listdir(LOCAL_FOLDER_PATH)
        files_to_upload = [
            item for item in all_items
            if os.path.isfile(os.path.join(LOCAL_FOLDER_PATH, item))
        ]

        if not files_to_upload:
            print(f"No files found in folder '{LOCAL_FOLDER_PATH}' to upload.")
            return

        print(f"Found {len(files_to_upload)} file(s) in folder '{LOCAL_FOLDER_PATH}' for upload.")

        # 4. Loop through and upload each file
        for idx, filename in enumerate(files_to_upload, 1):
            local_file_path = os.path.join(LOCAL_FOLDER_PATH, filename)

            # Automatically guess the file's MIME type (e.g., zip, mp4, png)
            mime_type, _ = mimetypes.guess_type(local_file_path)
            if not mime_type:
                mime_type = 'application/octet-stream' # Fallback for unknown types

            print(f"\n[{idx}/{len(files_to_upload)}] Uploading '{filename}' ({mime_type})...")

            file_metadata = {
                'name': filename,
                'parents': [FOLDER_ID]
            }

            # 256 MB chunks for stable upload of files of any size
            chunk_size = 256 * 1024 * 1024
            media = MediaFileUpload(
                local_file_path,
                mimetype=mime_type,
                resumable=True,
                chunksize=chunk_size
            )

            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            )

            # Resumable upload loop with progress indicator
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    sys.stdout.write(f"\rProgress: {progress}%")
                    sys.stdout.flush()

            print(f"\nSuccess! Drive File ID: {response.get('id')}")

        print("\nAll files from the folder have been successfully uploaded.")

    except HttpError as error:
        print(f"\nGoogle Drive API error occurred: {error}")
    except Exception as error:
        print(f"\nAn unexpected error occurred: {error}")

if __name__ == '__main__':
    # Optional: Create a test folder and a dummy file if they do not exist
    if not os.path.exists(LOCAL_FOLDER_PATH):
        os.makedirs(LOCAL_FOLDER_PATH)
        print(f"Created temporary folder '{LOCAL_FOLDER_PATH}' for testing.")
        with open(os.path.join(LOCAL_FOLDER_PATH, 'test_file_1.txt'), 'w') as f:
            f.write("Test file content 1")
        with open(os.path.join(LOCAL_FOLDER_PATH, 'test_file_2.txt'), 'w') as f:
            f.write("Test file content 2")

    upload_folder_files()

