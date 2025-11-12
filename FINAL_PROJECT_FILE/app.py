from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from tkinter import Tk, filedialog
from file_operations import scan_files, recover_files
import threading, webbrowser, uuid, os, base64
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

progress = {'scan': 0, 'recover': 0}
jobs = {}

# Folder picker
def browse_folder():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/browse_drive')
def browse_drive():
    return jsonify({'path': browse_folder()})


@app.route('/browse_save')
def browse_save():
    return jsonify({'path': browse_folder()})


@app.route('/scan', methods=['POST'])
def scan_files_route():
    data = request.get_json()
    drive = data.get('drive')
    file_type = data.get('file_type')
    min_size = data.get('min_size')
    max_size = data.get('max_size')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'running', 'files': []}
    progress['scan'] = 0

    def run_scan():
        try:
            files = scan_files(drive, file_type, min_size, max_size, start_date, end_date)
            jobs[job_id]['files'] = files
            jobs[job_id]['status'] = 'done'
            progress['scan'] = 100
        except Exception as e:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = str(e)
            progress['scan'] = 0

    threading.Thread(target=run_scan).start()
    return jsonify({'job_id': job_id}), 202


@app.route('/recover', methods=['POST'])
def recover_files_route():
    data = request.get_json()
    save_dir = data.get('save_dir')
    files = data.get('files', [])
    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'running', 'recovered': []}
    progress['recover'] = 0

    def run_recover():
        try:
            recovered = recover_files(files, save_dir)
            jobs[job_id]['recovered'] = recovered
            jobs[job_id]['status'] = 'done'
            progress['recover'] = 100
        except Exception as e:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = str(e)
            progress['recover'] = 0

    threading.Thread(target=run_recover).start()
    return jsonify({'job_id': job_id}), 202


@app.route('/progress')
def get_progress():
    return jsonify(progress)


@app.route('/job_result')
def job_result():
    job_id = request.args.get('job_id')
    if not job_id or job_id not in jobs:
        return jsonify({'error': 'invalid job id'}), 404
    return jsonify(jobs[job_id])


@app.route('/preview')
def preview_file():
    file_path = unquote(request.args.get('path', ''))
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    ext = os.path.splitext(file_path)[1].lower()

    # --- Image Preview ---
    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
        with open(file_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode('utf-8')
        return jsonify({
            'type': 'image',
            'content': f"data:image/{ext.replace('.', '')};base64,{encoded}"
        })

    # --- Text Preview ---
    elif ext in ['.txt', '.log', '.md']:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)
            return jsonify({'type': 'text', 'content': content})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        return jsonify({'error': 'Unsupported file type'}), 400


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
