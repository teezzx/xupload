import os

# --- Configuration Settings ---
folder_path = "/content/Movies/"

# First Pair
old_text_1 = "[Pure Taboo] - "
new_text_1 = ""

# Second Pair
old_text_2 = " ⭐️ Free FULL Video!.mp4"
new_text_2 = ".mp4"
# ------------------------------

# Check if the directory exists before proceeding
if os.path.exists(folder_path):
    rename_count = 0

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Start with the original filename
        new_filename = filename

        # Apply the first replacement if the old text is present
        if old_text_1 and (old_text_1 in new_filename):
            new_filename = new_filename.replace(old_text_1, new_text_1)

        # Apply the second replacement if the old text is present
        if old_text_2 and (old_text_2 in new_filename):
            new_filename = new_filename.replace(old_text_2, new_text_2)

        # If the filename was changed by either replacement rule, rename the file
        if new_filename != filename:
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)

            try:
                os.rename(old_file, new_file)
                print(f"Renamed: '{filename}' -> '{new_filename}'")
                rename_count += 1
            except Exception as e:
                print(f"Error renaming '{filename}': {e}")

    print(f"Processing completed. Total files renamed: {rename_count}")
else:
    print(
        f"Error: The folder path '{folder_path}' does not exist. Please verify the path."
    )

