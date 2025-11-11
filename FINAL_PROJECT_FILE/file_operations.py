import os
import shutil
from datetime import datetime

def scan_files(drive, file_type):
    deleted_files = []
    total_files = sum([len(files) for r, d, files in os.walk(drive)])
    file_count = 0

    for root, dirs, files in os.walk(drive):
        for file in files:
            file_count += 1
            if file.endswith(file_type):
                file_path = os.path.join(root, file)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                deleted_files.append({'path': file_path, 'modified_time': modified_time})
    deleted_files.sort(key=lambda x: x['modified_time'], reverse=True)
    return deleted_files


def recover_files(files, save_dir):
    recovered = []
    for file_info in files:
        file_path = file_info['path']
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            save_path = os.path.join(save_dir, file_name)
            shutil.copy(file_path, save_path)
            recovered.append(file_path)
    return recovered
