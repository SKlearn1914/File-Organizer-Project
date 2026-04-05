from flask import Flask, render_template, request, jsonify, send_file
import os
import shutil
import csv
from datetime import datetime

app = Flask(__name__)

# Global Variables
folder_path = ""
file_types = {
    "Documents": ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.xls'],
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.eps'],
    "Audio": ['.mp3', '.wav', '.ogg', '.m4a'],
    "Video": ['.mp4', '.mov', '.avi', '.mkv', '.mpeg'],
    "Archives": ['.zip', '.rar', '.7z', '.tar'],
    "Programming": ['.cpp', '.java', '.py'],
    "Others": []
}

undo_list = []
log_data = []

@app.route('/')
def index():
    return render_template('index.html')

# Confirm Folder
@app.route('/set-folder', methods=['POST'])
def set_folder():
    global folder_path
    path = request.json.get('path')

    if not path:
        return jsonify({"status": "error", "message": "Path is empty"})

    if os.path.isdir(path):
        folder_path = path
        return jsonify({"status": "success", "message": "Folder confirmed"})
    else:
        return jsonify({"status": "error", "message": "Invalid folder path"})

# Add category
@app.route('/add-category', methods=['POST'])
def add_category():
    global file_types

    data = request.get_json()
    name = data.get("name", "").strip()
    exts = data.get("extensions", [])

    if not name or not exts:
        return jsonify({"status": "error", "message": "Invalid input"})

    # normalize extensions
    exts = [e.lower().strip() for e in exts]

    file_types[name] = exts

    return jsonify({"status": "success", "file_types": file_types})


# remove category
@app.route('/remove-category', methods=['POST'])
def remove_category():
    global file_types

    data = request.get_json()
    name = data.get("name")

    if name in file_types:
        del file_types[name]
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Category not found"})
    
    
#   get category
@app.route('/get-categories')
def get_categories():
    return jsonify(file_types)



# Preview
@app.route('/preview')
def preview():
    if not folder_path:
        return jsonify({"error": "No folder selected"})

    preview_data = []
    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    for file in files:
        ext = os.path.splitext(file)[1].lower()
        category = "Others"

        for cat, exts in file_types.items():
            if ext in exts:
                category = cat
                break

        preview_data.append({"file": file, "category": category})

    return jsonify(preview_data)

# Organize Files
@app.route('/organize', methods=['POST'])
def organize():
    global undo_list, log_data

    # ✅ Get data FIRST
    data = request.get_json(silent=True) or {}
    custom_categories = data.get("categories", {})

    # ✅ Merge AFTER getting data
    all_categories = {**file_types, **custom_categories}

    undo_list.clear()
    log_data.clear()

    if not folder_path:
        return jsonify({"status": "error", "message": "No folder selected"})

    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    for file in files:
        file_path = os.path.join(folder_path, file)
        ext = os.path.splitext(file)[1].lower()
        category = "Others"

        for cat, exts in all_categories.items():
            if ext in exts:
                category = cat
                break

        dest_folder = os.path.join(folder_path, category)
        os.makedirs(dest_folder, exist_ok=True)

        dest_path = os.path.join(dest_folder, file)
        shutil.move(file_path, dest_path)

        log_entry = f"{file} -> {category}"
        log_data.append(log_entry)
        undo_list.append((dest_path, file_path))

    return jsonify({"status": "done", "total": len(files)})
# Undo
@app.route('/undo', methods=['POST'])
def undo():
    for src, dest in undo_list:
        if os.path.exists(src):
            shutil.move(src, dest)

    undo_list.clear()
    return jsonify({"status": "undone"})

# Export CSV
@app.route('/export')
def export():
    file_path = "log.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Category", "Time"])

        for entry in log_data:
            filename, category = entry.split("->")
            writer.writerow([
                filename.strip(),
                category.strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

    return send_file(file_path, as_attachment=True)
