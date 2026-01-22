import json
import os

DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_tasks():
    _ensure_data_dir()
    if not os.path.exists(TASKS_FILE): return []
    try:
        with open(TASKS_FILE, 'r') as file: return json.load(file)
    except: return []

def save_tasks(tasks):
    _ensure_data_dir()
    with open(TASKS_FILE, 'w') as file: json.dump(tasks, file, indent=4)

def load_settings():
    _ensure_data_dir()
    default = {"theme": "System"}
    if not os.path.exists(SETTINGS_FILE): return default
    try:
        with open(SETTINGS_FILE, 'r') as file: return json.load(file)
    except: return default

def save_settings(settings):
    _ensure_data_dir()
    with open(SETTINGS_FILE, 'w') as file: json.dump(settings, file, indent=4)