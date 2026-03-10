import pytest
from utils.storage import load_users, save_users

def test_full_swipe_to_match_flow(client, temp_storage):
    # Подготовка пользователей
    users = {
        "user1": {"likes": [], "matches": [], "passed": [], "gender": "Мужской", "profile_photo": "/photo1.jpg"},
        "user2": {"likes": [], "matches": [], "passed": [], "gender": "Женский", "profile_photo": "/photo2.jpg"}
    }
    save_users(users)

    # Логин как user1 и лайк user2
    with client.session_transaction() as sess:
        sess["user"] = "user1"
    client.post("/swipe/action", data={"target": "user2", "action": "like"})

    # Логин как user2 и лайк user1 (должен создать матч)
    with client.session_transaction() as sess:
        sess["user"] = "user2"
    response = client.post("/swipe/action", data={"target": "user1", "action": "like"}, follow_redirects=True)

    users = load_users()
    assert "user2" in users["user1"]["matches"]
    assert "user1" in users["user2"]["matches"]
    assert "Взаимный матч" in response.data.decode("utf-8")

    # Проверка страницы матчей
    response = client.get("/matches")
    assert "user1" in response.data.decode("utf-8")  # Видит матч