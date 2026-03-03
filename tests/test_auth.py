# tests/test_auth.py
def test_register_success(client, temp_storage):
    data = {
        "login": "testuser",
        "password": "Pass123",
        "email": "test@example.com"
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Регистрация успешна" in response.data.decode("utf-8")

    users = load_users()
    assert "testuser" in users
    assert users["testuser"]["email"] == "test@example.com"


def test_register_duplicate_login(client, temp_storage):
    # сначала создаём пользователя
    client.post("/register", data={"login": "dup", "password": "Pass123", "email": "a@b.ru"})
    
    response = client.post("/register", data={
        "login": "dup", "password": "Pass123", "email": "a@b.ru"
    }, follow_redirects=True)
    assert "Пользователь с таким логином уже существует" in response.data.decode("utf-8")


def test_login_success(client, temp_storage):
    # регистрируем
    client.post("/register", data={"login": "logintest", "password": "Pass123", "email": "x@y.ru"})
    
    response = client.post("/login", data={
        "login": "logintest", "password": "Pass123"
    }, follow_redirects=True)
    assert "Профиль" in response.data.decode("utf-8")


def test_forgot_password(client, temp_storage):
    client.post("/register", data={"login": "resetuser", "password": "Pass123", "email": "reset@test.ru"})
    
    response = client.post("/forgot", data={"email": "reset@test.ru"}, follow_redirects=True)
    assert "Ссылка для сброса пароля отправлена" in response.data.decode("utf-8")