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


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

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
            "gender": "",                     # ← НОВОЕ
            "reset_token": None,
            "likes": [],
            "passed": [],
            "matches": [],
            "chats": {}
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

    all_hobbies = ["Спорт", "Музыка", "Кино", "Путешествия", "Чтение", "Игры", "Кулинария", "Игры", "Машины", "Психология"]
    search_options = ["Любовь", "Общение", "Дружба"]
    status_options = ["Активный", "В поиске", "Скрытый"]
    gender_options = ["Мужской", "Женский"]

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
        user["gender"] = request.form.get("gender", "")   # ← НОВОЕ


        save_users(users)
        flash("Профиль обновлён")
        return redirect(url_for("auth.profile"))

    # ---------------- GET ----------------
    return render_template(
        "profile.html",
        user=user,
        hobbies=all_hobbies,
        search_options=search_options,
        status_options=status_options,
        gender_options=gender_options
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

@auth.route("/swipe")
def swipe():
    if "user" not in session:
        flash("Войдите, чтобы смотреть анкеты")
        return redirect(url_for("auth.login"))

    users = load_users()
    current_user_login = session["user"]
    me = users.get(current_user_login)

    if not me:
        session.pop("user", None)
        return redirect(url_for("auth.login"))

    # Собираем всех, кого уже видели (лайк + пропуск)
    seen = set(me.get("likes", []) + me.get("passed", []))

    # Список кандидатов
    candidates = []

    for login, user in users.items():
        if login == current_user_login:
            continue
        if login in seen:
            continue
        if not user.get("profile_photo"):  # без фото — пропускаем (можно убрать это условие позже)
            continue

        my_gender = me.get("gender", "")
        target_gender = user.get("gender", "")
        if my_gender and target_gender:
            expected_opp = "Женский" if my_gender == "Мужской" else "Мужской" if my_gender == "Женский" else None
            if expected_opp and target_gender != expected_opp:
                continue

        # Считаем совпадения по интересам
        common_hobbies = set(me.get("hobbies", [])) & set(user.get("hobbies", []))
        match_score = len(common_hobbies) * 10

        # Бонус если looking_for совпадает с моим статусом (или наоборот)
        if user.get("looking_for") and me.get("status") in user["looking_for"]:
            match_score += 15
        if me.get("looking_for") and user.get("status") in me["looking_for"]:
            match_score += 15

        candidates.append({
            "login": login,
            "name": user.get("name", login),
            "age": user.get("age", "?"),
            "zodiac": user.get("zodiac", ""),
            "gender": target_gender,                     # для отображения
            "bio": user.get("bio", "")[:120] + ("..." if len(user.get("bio", "")) > 120 else ""),
            "profile_photo": user.get("profile_photo", ""),
            "album_count": len(user.get("album", [])),
            "common_hobbies": list(common_hobbies)[:4],  # показываем до 4 общих
            "score": match_score
        })

    # Сортируем по убыванию совпадений (лучшие — первые)
    candidates.sort(key=lambda x: x["score"], reverse=True)

    # Берём первых 10 (или меньше)
    candidates = candidates[:10]

    return render_template(
        "swipe.html",
        candidates=candidates,
        current_user=me
    )

@auth.route("/swipe/action", methods=["POST"])
def swipe_action():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    target_login = request.form.get("target")
    action = request.form.get("action")

    print(f"[DEBUG] Действие: {action} от {session['user']} на {target_login}")

    if not target_login or action not in ["like", "pass"]:
        flash("Ошибка действия")
        return redirect(url_for("auth.swipe"))

    users = load_users()
    me_login = session["user"]
    me = users.get(me_login)
    target = users.get(target_login)

    if not me or not target:
        print("[DEBUG] Пользователь не найден")
        flash("Пользователь не найден")
        return redirect(url_for("auth.swipe"))

    if action == "like":
        if target_login not in me["likes"]:
            me["likes"].append(target_login)
            print(f"[DEBUG] Добавлен лайк: {target_login}")
        if me_login in target.get("likes", []):
            if target_login not in me["matches"]:
                me["matches"].append(target_login)
                target["matches"].append(me_login)
                print(f"[DEBUG] Матч! {me_login} ↔ {target_login}")
            flash(f"Взаимный матч с {target.get('name', target_login)}! 🎉")

    elif action == "pass":
        if target_login not in me["passed"]:
            me["passed"].append(target_login)
            print(f"[DEBUG] Добавлен пропуск: {target_login}")

    save_users(users)
    print("[DEBUG] Сохранено в users.json")
    return redirect(url_for("auth.swipe"))

@auth.route("/matches")
def matches():
    if "user" not in session:
        flash("Войдите, чтобы видеть матчи")
        return redirect(url_for("auth.login"))

    users = load_users()
    me_login = session["user"]
    me = users.get(me_login)

    if not me:
        session.pop("user", None)
        return redirect(url_for("auth.login"))

    match_logins = me.get("matches", [])
    match_profiles = []

    for login in match_logins:
        if login not in users:
            continue
        u = users[login]
        common_hobbies = set(me.get("hobbies", [])) & set(u.get("hobbies", []))

        match_profiles.append({
            "login": login,
            "name": u.get("name", login),
            "age": u.get("age", "?"),
            "zodiac": u.get("zodiac", ""),
            "bio": u.get("bio", "")[:100] + ("..." if len(u.get("bio", "")) > 100 else ""),
            "profile_photo": u.get("profile_photo", ""),
            "common_hobbies": list(common_hobbies)[:5],
            "last_active": "недавно"  # позже можно сделать реальное время
        })

    return render_template(
        "matches.html",
        matches=match_profiles,
        current_user=me
    )

@auth.route("/chat/<partner>")
def chat(partner):
    if "user" not in session:
        flash("Войдите, чтобы общаться")
        return redirect(url_for("auth.login"))

    users = load_users()
    me_login = session["user"]
    me = users.get(me_login)

    if not me or partner not in users or partner not in me.get("matches", []):
        flash("Чат недоступен")
        return redirect(url_for("auth.matches"))

    partner_user = users[partner]

    # Получаем сообщения
    my_chats = me.get("chats", {})
    messages = my_chats.get(partner, [])

    # Отмечаем как прочитанные ВСЕ сообщения ОТ партнёра
    updated = False
    for msg in messages:
        if msg.get("from") == partner and not msg.get("read", False):
            msg["read"] = True
            updated = True

    if updated:
        save_users(users)
        # Можно обновить messages после изменения, но т.к. это список в памяти — уже обновлён

    return render_template(
        "chat.html",
        partner=partner_user,
        partner_login=partner,
        messages=messages,
        me_login=me_login
    )

@auth.route("/chat/<partner>/send", methods=["POST"])
def send_message(partner):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    text = request.form.get("message", "").strip()
    if not text:
        return redirect(url_for("auth.chat", partner=partner))

    users = load_users()
    me_login = session["user"]
    me = users.get(me_login)
    partner_user = users.get(partner)

    if not me or not partner_user or partner not in me.get("matches", []):
        flash("Ошибка отправки")
        return redirect(url_for("auth.matches"))

    message = {
        "from": me_login,
        "text": text,
        "time": date.today().strftime("%Y-%m-%d %H:%M"),
        "read": False
    }

    # Добавляем себе
    if "chats" not in me:
        me["chats"] = {}
    if partner not in me["chats"]:
        me["chats"][partner] = []
    me["chats"][partner].append(message)

    # Добавляем собеседнику
    if "chats" not in partner_user:
        partner_user["chats"] = {}
    if me_login not in partner_user["chats"]:
        partner_user["chats"][me_login] = []
    partner_user["chats"][me_login].append(message)

    save_users(users)

    return redirect(url_for("auth.chat", partner=partner))