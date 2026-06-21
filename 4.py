import json
import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()
# ==================== CONFIGURATION ====================
API_KEY = os.getenv("RPM_API_KEY")

SOURCE_DIRECTORY = "/content/Movies"
RPM_FOLDER_ID = ""
IS_PUBLIC = 1  # 1 = Public, 0 = Private
# =======================================================

# Parse the Folder ID input
PARSED_FOLDER_ID = None
if RPM_FOLDER_ID and str(RPM_FOLDER_ID).strip().lower() != "none":
    try:
        PARSED_FOLDER_ID = int(RPM_FOLDER_ID)
    except ValueError:
        print(
            "⚠️ Warning: Provided Folder ID is not a valid number. Proceeding without a folder."
        )


def get_upload_server_url(api_key):
    """Requests a fresh upload server URL from the API."""
    url = f"https://rpmshare.com/api/upload/server?key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == 200:
            return data["result"]
        else:
            print(f"   ❌ API Error getting server: {data.get('msg')}")
            return None
    except Exception as e:
        print(f"   ❌ Connection Error: {str(e)}")
        return None


def upload_single_file(file_path, upload_url, current_idx, total_files):
    """Uploads a specific file to the provided server URL."""
    filename = os.path.basename(file_path)
    print(f"🔄 [{current_idx}/{total_files}] Uploading: {filename} ...")

    # Prepare payload
    payload = {
        "key": API_KEY,
        "file_title": filename,  # Uses filename as title
        "file_public": IS_PUBLIC,
    }

    if PARSED_FOLDER_ID is not None:
        payload["fld_id"] = PARSED_FOLDER_ID

    try:
        with open(file_path, "rb") as f:
            files = {"file": (filename, f)}
            response = requests.post(upload_url, data=payload, files=files)
            result = response.json()

            if result.get("status") == 200:
                # Success
                file_code = (
                    result["files"][0]["filecode"]
                    if "files" in result
                    else "Unknown"
                )
                print(f"   ✅ Success! Code: {file_code}")
                return True
            else:
                # API returned an error
                print(f"   ❌ Failed: {result.get('msg')}")
                return False

    except Exception as e:
        print(f"   ❌ Error uploading file: {str(e)}")
        return False


def batch_upload():
    # 1. Check Directory
    if not os.path.exists(SOURCE_DIRECTORY):
        print(f"❌ Directory not found: {SOURCE_DIRECTORY}")
        return

    # 2. Get list of files (filtering out directories and hidden files)
    all_items = os.listdir(SOURCE_DIRECTORY)
    file_list = [
        f
        for f in all_items
        if os.path.isfile(os.path.join(SOURCE_DIRECTORY, f))
        and not f.startswith(".")  # Skip .ipynb_checkpoints
    ]

    total_files = len(file_list)

    if total_files == 0:
        print("⚠️ No files found in directory to upload.")
        return

    print(f"📂 Found {total_files} files in {SOURCE_DIRECTORY}")
    print("🚀 Starting Batch Upload...")
    print("=========================================")

    # 3. Iterate and Upload
    success_count = 0

    for index, filename in enumerate(file_list, start=1):
        full_path = os.path.join(SOURCE_DIRECTORY, filename)

        # Step A: Get a fresh server URL for this specific file
        server_url = get_upload_server_url(API_KEY)

        if server_url:
            # Step B: Upload the file
            success = upload_single_file(
                full_path, server_url, index, total_files
            )
            if success:
                success_count += 1

        # Optional: Small delay to be polite to the API
        time.sleep(1)

    print("=========================================")
    print(
        f"🏁 Batch Complete. {success_count}/{total_files} files uploaded successfully."
    )


if __name__ == "__main__":
    batch_upload()

