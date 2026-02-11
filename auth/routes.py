from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from auth.security import hash_password, verify_password
from auth.validators import is_valid_password
from utils.storage import load_users, save_users
from datetime import date
from flask import Flask
import uuid
import os


app = Flask(__name__)
app.secret_key = "supersecretkey"

auth = Blueprint("auth", __name__)


# Допустимые расширения файлов для фото
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Папка для сохранения загруженных файлов
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ----------------- Регистрация -----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()

        if not login or not password or not email:
            flash("Заполните все поля")
            return render_template("register.html")

        if not is_valid_password(password):
            flash("Пароль должен быть 6–72 символа, с буквой и цифрой")
            return render_template("register.html")

        users = load_users()
        if login in users:
            flash("Пользователь с таким логином уже существует")
            return render_template("register.html")

        users[login] = {
            "password": hash_password(password),
            "email": email,
            "name": "",
            "age": "",
            "bio": "",
            "birth_day": None,
            "birth_month": None,
            "birth_year": None,
            "zodiac": "",
            "profile_photo": "",
            "album": [],
            "school": "",
            "profession": "",
            "status": "",
            "looking_for": "",
            "hobbies": [],
            "reset_token": None
        }


        save_users(users)
        flash("Регистрация успешна! Войдите в аккаунт")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ----------------- Вход -----------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        users = load_users()
        user = users.get(login)

        if not user or not verify_password(password, user["password"]):
            flash("Неверный логин или пароль")
            return render_template("login.html")

        session["user"] = login
        return redirect(url_for("auth.profile"))

    return render_template("login.html")


# ----------------- Вспомогательная функция -----------------
def calculate_zodiac(day: int, month: int) -> str:
    """Возвращает знак зодиака по дате рождения"""
    zodiac_dates = [
        (120, "Козерог"), (219, "Водолей"), (321, "Рыбы"),
        (420, "Овен"), (521, "Телец"), (621, "Близнецы"),
        (722, "Рак"), (823, "Лев"), (923, "Дева"),
        (1023, "Весы"), (1122, "Скорпион"), (1222, "Стрелец"),
        (1231, "Козерог")
    ]
    md = month * 100 + day
    for limit, sign in zodiac_dates:
        if md <= limit:
            return sign
    return "Козерог"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file_storage):
    """Сохраняет файл и возвращает путь для хранения в JSON"""
    if file_storage and allowed_file(file_storage.filename):
        filename = str(uuid.uuid4()) + "_" + file_storage.filename
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file_storage.save(filepath)
        return "/static/uploads/" + filename
    return None

@auth.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    users = load_users()
    user = users[session["user"]]

    all_hobbies = ["Спорт", "Музыка", "Кино", "Путешествия", "Чтение", "Игры", "Кулинария"]
    search_options = ["Любовь", "Общение", "Дружба"]
    status_options = ["Активный", "В поиске", "Скрытый"]

    if request.method == "POST":
        # ---------------- Основные поля ----------------
        name = request.form.get("name", "").strip()
        birth_date_str = request.form.get("birth_date", "")

        if not name:
            flash("Имя обязательно")
            return redirect(url_for("auth.profile"))
        if not birth_date_str:
            flash("Дата рождения обязательна")
            return redirect(url_for("auth.profile"))

        # Парсим дату рождения
        birth_date = date.fromisoformat(birth_date_str)
        user["birth_day"] = birth_date.day
        user["birth_month"] = birth_date.month
        user["birth_year"] = birth_date.year

        # Расчёт возраста
        today = date.today()
        user["age"] = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        # Знак зодиака
        user["zodiac"] = calculate_zodiac(birth_date.day, birth_date.month)

        # ---------------- Фото ----------------
        profile_photo_file = request.files.get("profile_photo")
        album_files = request.files.getlist("album")

        if profile_photo_file and profile_photo_file.filename:
            user["profile_photo"] = save_file(profile_photo_file)

        # Альбом: добавляем новые фото к существующим
        album_paths = user.get("album", [])
        new_album_paths = [save_file(f) for f in album_files if f.filename]
        if new_album_paths:
            album_paths.extend(new_album_paths)
        user["album"] = album_paths

        # ---------------- Остальные поля ----------------
        user["name"] = name
        user["bio"] = request.form.get("bio", "")
        user["school"] = request.form.get("school", "")
        user["profession"] = request.form.get("profession", "")
        user["status"] = request.form.get("status", "")
        user["looking_for"] = request.form.get("looking_for", "")
        user["hobbies"] = request.form.getlist("hobbies")

        save_users(users)
        flash("Профиль обновлён")
        return redirect(url_for("auth.profile"))

    # ---------------- GET ----------------
    return render_template(
        "profile.html",
        user=user,
        hobbies=all_hobbies,
        search_options=search_options,
        status_options=status_options
    )


# ----------------- Сброс пароля -----------------
@auth.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        users = load_users()

        login_found = None
        for login, u in users.items():
            if u["email"] == email:
                login_found = login
                break

        if not login_found:
            flash("Пользователь с таким email не найден")
            return render_template("forgot_password.html")

        token = str(uuid.uuid4())
        users[login_found]["reset_token"] = token
        save_users(users)

        from utils.mail import send_reset_email
        link = url_for("auth.reset_password", token=token, _external=True)
        send_reset_email(email, link)
        flash("Ссылка для сброса пароля отправлена на email")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    users = load_users()
    login_found = None

    for login, u in users.items():
        if u.get("reset_token") == token:
            login_found = login
            break

    if not login_found:
        flash("Неверный токен сброса")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if not is_valid_password(password):
            flash("Пароль должен быть 6–72 символа, с буквой и цифрой")
            return render_template("reset_password.html", token=token)

        users[login_found]["password"] = hash_password(password)
        users[login_found]["reset_token"] = None
        save_users(users)
        flash("Пароль успешно обновлён")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)
