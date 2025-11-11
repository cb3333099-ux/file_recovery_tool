import os
import threading
import webbrowser
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from tkinter import Tk, filedialog
from file_operations import scan_files, recover_files

app = Flask(__name__)
CORS(app)

progress = {'scan': 0, 'recover': 0}


# 🗂️ Folder Selection (using Tkinter)
def browse_folder():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path


# 🌐 Homepage
@app.route('/')
def index():
    return render_template('index.html')


# 📁 Browse Drive
@app.route('/browse_drive', methods=['GET'])
def browse_drive():
    path = browse_folder()
    return jsonify({'path': path})


# 💾 Browse Save Directory
@app.route('/browse_save', methods=['GET'])
def browse_save():
    path = browse_folder()
    return jsonify({'path': path})


# 🔍 Scan Files by Type
@app.route('/scan_files', methods=['GET'])
def scan_files_route():
    drive = request.args.get('drive')
    file_type = request.args.get('fileType')
    files = scan_files(drive, file_type)

    # Add file sizes
    for f in files:
        if os.path.exists(f['path']):
            f['size'] = os.path.getsize(f['path']) // 1024  # KB

    progress['scan'] = 100
    return jsonify({'files': files})


# ♻️ Recover Selected Files
@app.route('/recover_files', methods=['POST'])
def recover_files_route():
    data = request.get_json()
    save_dir = data['saveDir']
    files = [{'path': f.split(" - ")[1].split(" (")[0]} for f in data['files']]
    recover_files(files, save_dir)
    progress['recover'] = 100
    return jsonify({'status': 'success'})


# 📊 Progress Status
@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(progress)


# 🗑️ Permanently Delete Selected Files
@app.route('/delete_files', methods=['POST'])
def delete_files_route():
    data = request.get_json()
    files = [f.split(" - ")[1].split(" (")[0] for f in data['files']]
    deleted = []

    for file_path in files:
        try:
            os.remove(file_path)
            deleted.append(file_path)
        except Exception as e:
            print(f"Could not delete {file_path}: {e}")

    return jsonify({'deleted': deleted})


# 🚀 Auto-open Browser on Start
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
