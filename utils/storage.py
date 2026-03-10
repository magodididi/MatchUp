import json
import os
from contextlib import contextmanager

DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except json.JSONDecodeError:
        return {}

    migrated = False
    for login, u in users.items():
        if "likes" not in u:
            u["likes"] = []
            migrated = True
        if "passed" not in u:
            u["passed"] = []
            migrated = True
        if "matches" not in u:
            u["matches"] = []
            migrated = True
        if "chats" not in u:
            u["chats"] = {}
            migrated = True
        if "gender" not in u:                  # ← НОВОЕ
            u["gender"] = ""
            migrated = True

    if migrated:
        save_users(users)
        print("✅ users.json обновлён (добавлено поле gender)")

    return users

def save_users(users: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)



@contextmanager
def user_data():
    users = load_users()
    try:
        yield users
    finally:
        save_users(users)