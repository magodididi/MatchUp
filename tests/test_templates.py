# tests/test_templates.py
from bs4 import BeautifulSoup
from utils.storage import save_users

def test_swipe_template_renders_correctly(client, temp_storage):
    save_users({"testuser": {"name": "Test", "age": 25, "zodiac": "Лев", "gender": "Мужской", "profile_photo": "/test.jpg", "bio": "Bio"}})

    with client.session_transaction() as sess:
        sess["user"] = "anotheruser"  # Чтобы увидеть кандидата

    response = client.get("/swipe")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    assert soup.find("div", class_="name-age").text == "Test, 25"
    assert soup.find("img")["src"] == "/test.jpg"
    assert "Лев • Мужской" in soup.text