from utils.storage import load_users, save_users

def test_matches_page_shows_mutual(client, temp_storage):
    users = {
        "me": {"matches": ["partner"], "gender": "Мужской", "profile_photo": "/me.jpg"},
        "partner": {"name": "Катя", "age": 21, "zodiac": "Рак", "profile_photo": "/cat.jpg", "hobbies": ["Музыка"]}
    }
    save_users(users)

    with client.session_transaction() as sess:
        sess["user"] = "me"

    response = client.get("/matches")
    assert response.status_code == 200
    assert "Катя" in response.data.decode("utf-8")


def test_send_message(client, temp_storage):
    users = {
        "me": {"matches": ["partner"], "chats": {}, "gender": "Мужской"},
        "partner": {"matches": ["me"], "chats": {}, "gender": "Женский"}
    }
    save_users(users)

    with client.session_transaction() as sess:
        sess["user"] = "me"

    response = client.post("/chat/partner/send", data={"message": "Привет!"}, follow_redirects=True)
    assert response.status_code == 200

    users = load_users()
    assert len(users["me"]["chats"]["partner"]) == 1
    assert users["me"]["chats"]["partner"][0]["text"] == "Привет!"