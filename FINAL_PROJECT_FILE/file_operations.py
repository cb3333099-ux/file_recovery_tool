import os
import shutil
import time
from datetime import datetime

def scan_files(drive, file_type=None, min_size=None, max_size=None, start_date=None, end_date=None):
    found_files = []

    # Convert filters
    min_size = int(min_size) * 1024 if min_size else 0
    max_size = int(max_size) * 1024 if max_size else float('inf')

    start_timestamp = time.mktime(time.strptime(start_date, "%Y-%m-%d")) if start_date else 0
    end_timestamp = time.mktime(time.strptime(end_date, "%Y-%m-%d")) if end_date else float('inf')

    for root, dirs, files in os.walk(drive):
        for file in files:
            if file_type and not file.endswith(file_type):
                continue

            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                modified = os.path.getmtime(file_path)

                if not (min_size <= size <= max_size):
                    continue
                if not (start_timestamp <= modified <= end_timestamp):
                    continue

                modified_time = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
                found_files.append({
                    'path': file_path,
                    'modified_time': modified_time,
                    'size_kb': round(size / 1024, 2)
                })
            except Exception:
                continue

    found_files.sort(key=lambda x: x['modified_time'], reverse=True)
    return found_files


def recover_files(files, save_dir):
    recovered = []
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for file_info in files:
        file_path = os.path.normpath(file_info['path'])
        if not os.path.exists(file_path):
            print(f"[❌] File not found: {file_path}")
            continue

        try:
            file_name = os.path.basename(file_path)
            save_path = os.path.join(save_dir, file_name)

            # Avoid overwriting
            base, ext = os.path.splitext(save_path)
            counter = 1
            while os.path.exists(save_path):
                save_path = f"{base}({counter}){ext}"
                counter += 1

            shutil.copy2(file_path, save_path)
            recovered.append(save_path)
        except PermissionError:
            print(f"[⚠️] Permission denied: {file_path}")
        except Exception as e:
            print(f"[⚠️] Error copying {file_path}: {e}")

    return recovered
