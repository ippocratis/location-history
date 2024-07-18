import os
import shutil
import re
from datetime import datetime

def get_latest_file(files):
    dates = []
    for file in files:
        match = re.search(r'(\d{4}-\d{2})\.rec', file)
        if match:
            date_str = match.group(1)
            date_obj = datetime.strptime(date_str, "%Y-%m")
            dates.append((date_obj, file))
    if dates:
        latest_date, latest_file = max(dates)
        return latest_file
    return None

def merge_files(src_file, dest_file):
    with open(dest_file, 'a') as dest, open(src_file, 'r') as src:
        dest.write(src.read())

def scan_and_copy(source_folder, dest_folder, extension):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    print(f"Scanning {source_folder} for files with extension {extension}")

    for root, _, files in os.walk(source_folder):
        matching_files = [f for f in files if f.endswith(extension)]
        for file in matching_files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_folder, file)
            
            print(f"Found file: {src_file}")
            
            if os.path.exists(dest_file):
                base_name = os.path.splitext(file)[0]
                existing_files = [f for f in os.listdir(dest_folder) if f.startswith(base_name)]
                latest_file = get_latest_file(existing_files)
                
                if latest_file:
                    latest_dest_file = os.path.join(dest_folder, latest_file)
                    print(f"Merging {src_file} into {latest_dest_file}")
                    merge_files(src_file, latest_dest_file)
                else:
                    print(f"Copying {src_file} to {dest_file}")
                    shutil.copy2(src_file, dest_file)
            else:
                print(f"Copying {src_file} to {dest_file}")
                shutil.copy2(src_file, dest_file)

# Source and destination folder paths
source_folder = '../owntracks/store/rec/'  # External storage path
dest_folder = './'  # Project root folder
file_extension = '.rec'

scan_and_copy(source_folder, dest_folder, file_extension)
