import os
import sys
import subprocess
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===============================
# PROJECT DEFINITIONS
# ===============================

PROJECTS = {
    "stego": {
        "name": "Stego-Suite",
        "folder": "Stego-Suite-Python",
        "icon": "🕵️",
        "color": "text-cyan-400",
        "description": "Advanced Steganography Tool. Hide files inside images & audio using LSB & appending techniques."
    },
    "dynes": {
        "name": "DyNES Encryption",
        "folder": "DyNES_Project",
        "icon": "🔐",
        "color": "text-blue-400",
        "description": "Dynamic Network Encryption Standard using Feistel Networks & Chaos Theory."
    },
    "hash": {
        "name": "File Integrity Checker",
        "folder": "Hash_Tool",
        "icon": "🧬",
        "color": "text-green-400",
        "description": "Cryptographic hash scanner (MD5, SHA-256, SHA-512) to verify file authenticity."
    },
    "netprobe": {
        "name": "Net-Probe Scanner",
        "folder": "Net_Probe",
        "icon": "📡",
        "color": "text-purple-400",
        "description": "Active TCP port scanner with radar-style network visualization."
    },
    "metawiper": {
        "name": "Meta-Wiper",
        "folder": "Meta_Wiper",
        "icon": "🧹",
        "color": "text-yellow-400",
        "description": "Privacy tool to strip hidden EXIF metadata from images."
    }
}

# ===============================
# ROUTES
# ===============================

@app.route("/")
def home():
    return render_template("index.html", projects=PROJECTS)


@app.route("/launch/<project_id>")
def launch(project_id):
    if project_id not in PROJECTS:
        return "Invalid Project", 404

    folder_name = PROJECTS[project_id]["folder"]
    folder_path = os.path.join(BASE_DIR, folder_name)

    if not os.path.exists(folder_path):
        return "Project folder not found", 404

    # Find first .py file inside folder
    for file in os.listdir(folder_path):
        if file.endswith(".py"):
            script_path = os.path.join(folder_path, file)
            subprocess.Popen([sys.executable, script_path])
            break

    return redirect(url_for("home"))

# ===============================
# RUN SERVER
# ===============================

if __name__ == "__main__":
    print("🚀 CYBER_SUITE // COMMAND_NODE INITIALIZING...")
    app.run(host="127.0.0.1", port=5000, debug=False)