# tests/test_swipe.py
import json
from utils.storage import load_users, save_users

def test_like_creates_match_if_mutual(client, temp_storage):
    # подготовка двух пользователей
    users = {
        "u1": {"likes": [], "matches": [], "passed": [], "gender": "Мужской", "profile_photo": "/photo.jpg"},
        "u2": {"likes": ["u1"], "matches": [], "passed": [], "gender": "Женский", "profile_photo": "/photo.jpg"}
    }
    save_users(users)

    with client.session_transaction() as sess:
        sess["user"] = "u1"

    response = client.post("/swipe/action", data={"target": "u2", "action": "like"}, follow_redirects=True)
    
    users = load_users()
    assert "u2" in users["u1"]["matches"]
    assert "u1" in users["u2"]["matches"]
    assert "Взаимный матч" in response.data.decode("utf-8")


def test_pass_just_adds_to_passed(client, temp_storage):
    save_users({"u1": {"passed": [], "gender": "Мужской", "profile_photo": "/p.jpg"},
                "u2": {"gender": "Женский", "profile_photo": "/p.jpg"}})

    with client.session_transaction() as sess:
        sess["user"] = "u1"

    client.post("/swipe/action", data={"target": "u2", "action": "pass"})

    users = load_users()
    assert "u2" in users["u1"]["passed"]