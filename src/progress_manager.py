import json
import datetime
import os 
import sys

def get_base_path():
    return os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()

PROGRESS_FILE = os.path.join(get_base_path(), "progress.json")

def get_progress():
    try:
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"streak": 0, "last_date": None, "completed_today": False}

def update_streak():
    progress = get_progress()
    today = datetime.date.today()
    last_date_str = progress.get("last_date")
    
    if last_date_str:
        last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
    else:
        last_date = None

    if last_date == today:
        return progress["streak"], False

    if last_date == today - datetime.timedelta(days=1):
        progress["streak"] += 1
    else:
        progress["streak"] = 1
    
    progress["last_date"] = str(today)
    progress["completed_today"] = True
    
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)
        
    return progress["streak"], True

def check_current_streak():
    progress = get_progress()
    today = datetime.date.today()
    last_date_str = progress.get("last_date")
    
    if not last_date_str:
        return 0
    
    last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
    
    if last_date < today - datetime.timedelta(days=1):
        return 0
    
    return progress["streak"]