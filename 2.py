import os
import re

# --- Configuration Settings ---
folder_path = "/content/Movies/"

# Pattern: [anything] - 
old_pattern_1 = r"^\[[^\]]+\] - "
new_text_1 = ""

# Second Pair
old_text_2 = " ⭐️ Free FULL Video!.mp4"
new_text_2 = ".mp4"
# ------------------------------

if os.path.exists(folder_path):
    rename_count = 0

    for filename in os.listdir(folder_path):
        new_filename = filename

        # Remove leading "[Anything] - "
        new_filename = re.sub(old_pattern_1, new_text_1, new_filename)

        # Second replacement
        if old_text_2 in new_filename:
            new_filename = new_filename.replace(old_text_2, new_text_2)

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
    print(f"Error: The folder path '{folder_path}' does not exist.")
