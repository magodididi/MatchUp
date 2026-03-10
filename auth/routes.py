from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from auth.security import hash_password, verify_password
from auth.validators import is_valid_password, is_valid_email  # Добавлен импорт
from utils.storage import load_users, save_users
from datetime import date
from flask import Flask
import uuid
import os
from contextlib import contextmanager
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

auth = Blueprint("auth", __name__)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@contextmanager
def user_data():
    users = load_users()
    try:
        yield users
    finally:
        save_users(users)


from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from auth.security import hash_password, verify_password
from auth.validators import is_valid_password, is_valid_email  # Добавлен импорт
from utils.storage import load_users, save_users
from datetime import date
from flask import Flask
import uuid
import os
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = "supersecretkey"

auth = Blueprint("auth", __name__)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@contextmanager
def user_data():
    users = load_users()
    try:
        yield users
    finally:
        save_users(users)



# ----------------- Регистрация -----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()
        confirm_password = request.form.get("confirm_password", "")

        if not login or not password or not email or not confirm_password:
            flash("Заполните все поля")
            return render_template("register.html")

        if len(login) < 3 or len(login) > 20:
            flash("Логин должен быть от 3 до 20 символов")
            return render_template("register.html")

        if not is_valid_email(email):
            flash("Введите корректный email адрес")
            return render_template("register.html")

        if not is_valid_password(password):
            flash("Пароль должен быть 6–72 символа, с буквой и цифрой")
            return render_template("register.html")

        if password != confirm_password:
            flash("Пароли не совпадают")
            return render_template("register.html")

        with user_data() as users:
            if login in users:
                flash("Пользователь с таким логином уже существует")
                return render_template("register.html")

            # Проверка на существующий email
            for u in users.values():
                if u.get("email") == email:
                    flash("Пользователь с таким email уже существует")
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
                "gender": "",
                "reset_token": None,
                "likes": [],
                "passed": [],
                "matches": [],
                "chats": {}
            }

        flash("Регистрация успешна! Войдите в аккаунт")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

# ----------------- Вход -----------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        with user_data() as users:
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

    with user_data() as users:
        current_user = users.get(session["user"])
        if not current_user:
            session.pop("user", None)
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            try:
                _handle_profile_update(current_user, users)
                flash("Профиль обновлён")
                return redirect(url_for("auth.profile"))
            except ValueError as e:
                flash(str(e))
                # продолжаем рендерить страницу с ошибкой

        return _render_profile_page(current_user)



def _handle_profile_update(user, users):
    # ── Основные данные ───────────────────────────────
    name = request.form.get("name", "").strip()
    if not name:
        flash("Имя обязательно")
        raise ValueError("Имя обязательно")   # или return, но тогда дублирование

    birth_date_str = request.form.get("birth_date", "")
    if not birth_date_str:
        flash("Дата рождения обязательна")
        raise ValueError("Дата рождения обязательна")

    birth_date = date.fromisoformat(birth_date_str)
    user.update({
        "name": name,
        "birth_day": birth_date.day,
        "birth_month": birth_date.month,
        "birth_year": birth_date.year,
        "age": _calculate_age(birth_date),
        "zodiac": calculate_zodiac(birth_date.day, birth_date.month),
    })

    # ── Фото ──────────────────────────────────────────
    _handle_profile_photo(user)
    _handle_album_photos(user)

    # ── Остальные поля ────────────────────────────────
    user.update({
        "bio": request.form.get("bio", ""),
        "school": request.form.get("school", ""),
        "profession": request.form.get("profession", ""),
        "status": request.form.get("status", ""),
        "looking_for": request.form.get("looking_for", ""),
        "hobbies": request.form.getlist("hobbies"),
        "gender": request.form.get("gender", ""),
    })



def _handle_profile_photo(user):
    file = request.files.get("profile_photo")
    if file and file.filename and allowed_file(file.filename):
        user["profile_photo"] = save_file(file)


def _handle_album_photos(user):
    files = request.files.getlist("album")
    new_paths = [save_file(f) for f in files if f.filename and allowed_file(f.filename)]
    if new_paths:
        user.setdefault("album", []).extend(new_paths)


def _calculate_age(birth_date: date) -> int:
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def _render_profile_page(user):
    context = {
        "user": user,
        "hobbies": ["Спорт", "Музыка", "Кино", "Путешествия", "Чтение", "Игры", "Кулинария", "Машины", "Психология"],
        "search_options": ["Любовь", "Общение", "Дружба"],
        "status_options": ["Активный", "В поиске", "Скрытый"],
        "gender_options": ["Мужской", "Женский"],
    }
    return render_template("profile.html", **context)

# ----------------- Сброс пароля -----------------
@auth.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        with user_data() as users:
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

        from utils.mail import send_reset_email
        link = url_for("auth.reset_password", token=token, _external=True)
        send_reset_email(email, link)
        flash("Ссылка для сброса пароля отправлена на email")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")

@auth.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    with user_data() as users:
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
            flash("Пароль успешно обновлён")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)

@auth.route("/swipe")
def swipe():
    if "user" not in session:
        flash("Войдите, чтобы смотреть анкеты")
        return redirect(url_for("auth.login"))

    with user_data() as users:
        current_user_login = session["user"]
        me = users.get(current_user_login)

        if not me:
            session.pop("user", None)
            return redirect(url_for("auth.login"))

        seen = set(me.get("likes", []) + me.get("passed", []))

        candidates = []

        for login, user in users.items():
            if login == current_user_login:
                continue
            if login in seen:
                continue
            if not user.get("profile_photo"):
                continue

            my_gender = me.get("gender", "")
            target_gender = user.get("gender", "")
            if my_gender and target_gender:
                expected_opp = "Женский" if my_gender == "Мужской" else "Мужской" if my_gender == "Женский" else None
                if expected_opp and target_gender != expected_opp:
                    continue

            common_hobbies = set(me.get("hobbies", [])) & set(user.get("hobbies", []))
            match_score = len(common_hobbies) * 10

            if user.get("looking_for") and me.get("status") in user["looking_for"]:
                match_score += 15
            if me.get("looking_for") and user.get("status") in me["looking_for"]:
                match_score += 15

            candidates.append({
                "login": login,
                "name": user.get("name", login),
                "age": user.get("age", "?"),
                "zodiac": user.get("zodiac", ""),
                "gender": target_gender,
                "bio": user.get("bio", "")[:120] + ("..." if len(user.get("bio", "")) > 120 else ""),
                "profile_photo": user.get("profile_photo", ""),
                "album_count": len(user.get("album", [])),
                "common_hobbies": list(common_hobbies)[:4],
                "score": match_score
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)
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

    if not target_login or action not in ["like", "pass"]:
        flash("Ошибка действия")
        return redirect(url_for("auth.swipe"))

    with user_data() as users:
        me_login = session["user"]
        me = users.get(me_login)
        target = users.get(target_login)

        if not me or not target:
            flash("Пользователь не найден")
            return redirect(url_for("auth.swipe"))

        if action == "like":
            if target_login not in me["likes"]:
                me["likes"].append(target_login)

            if me_login in target.get("likes", []):
                if target_login not in me["matches"]:
                    me["matches"].append(target_login)
                    target["matches"].append(me_login)
                flash(f"Взаимный матч с {target.get('name', target_login)}! 🎉")

        elif action == "pass":
            if target_login not in me["passed"]:
                me["passed"].append(target_login)

    return redirect(url_for("auth.swipe"))

@auth.route("/matches")
def matches():
    if "user" not in session:
        flash("Войдите, чтобы видеть матчи")
        return redirect(url_for("auth.login"))

    with user_data() as users:
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
                "last_active": "недавно"
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

    with user_data() as users:
        me_login = session["user"]
        me = users.get(me_login)

        if not me or partner not in users or partner not in me.get("matches", []):
            flash("Чат недоступен")
            return redirect(url_for("auth.matches"))

        partner_user = users[partner]

        messages = me.get("chats", {}).get(partner, [])

        updated = False
        for msg in messages:
            if msg.get("from") == partner and not msg.get("read", False):
                msg["read"] = True
                updated = True

        # save уже произойдёт автоматически в finally

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
    
    with user_data() as users:
        me_login = session["user"]
        me = users.get(me_login)
        partner_user = users.get(partner)
        
        if not me or not partner_user or partner not in me.get("matches", []):
            flash("Ошибка отправки")
            return redirect(url_for("auth.matches"))
        
        message_id = str(uuid.uuid4())
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        message = {
            "id": message_id,
            "from": me_login,
            "text": text,
            "time": current_time,
            "read": False,
            "edited": False
        }
        
        # Добавляем отправителю
        me.setdefault("chats", {}).setdefault(partner, []).append(message.copy())
        
        # Добавляем получателю
        partner_user.setdefault("chats", {}).setdefault(me_login, []).append(message)
        
        return redirect(url_for("auth.chat", partner=partner))

@auth.route("/api/unread-count")
def unread_count():
    if "user" not in session:
        return jsonify({"unread_count": 0})
    
    with user_data() as users:
        me = users.get(session["user"])
        if not me:
            return jsonify({"unread_count": 0})
        
        unread_total = 0
        for partner, messages in me.get("chats", {}).items():
            for msg in messages:
                if msg.get("from") != session["user"] and not msg.get("read", False):
                    unread_total += 1
        
        return jsonify({"unread_count": unread_total})

@auth.route("/chat/mark-read/<message_id>", methods=["POST"])
def mark_message_read(message_id):
    if "user" not in session:
        return jsonify({"success": False})
    
    with user_data() as users:
        me = users.get(session["user"])
        if not me:
            return jsonify({"success": False})
        
        for partner, messages in me.get("chats", {}).items():
            for msg in messages:
                if msg.get("id") == message_id and msg.get("from") != session["user"]:
                    msg["read"] = True
                    return jsonify({"success": True})
        
        return jsonify({"success": False})

@auth.route("/chat/delete-message/<message_id>", methods=["POST"])
def delete_message(message_id):
    if "user" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})
    
    with user_data() as users:
        me = users.get(session["user"])
        if not me:
            return jsonify({"success": False, "error": "User not found"})
        
        for partner, messages in me.get("chats", {}).items():
            for i, msg in enumerate(messages):
                if msg.get("id") == message_id and msg.get("from") == session["user"]:
                    # Удаляем сообщение
                    deleted_msg = messages.pop(i)
                    
                    # Также удаляем у получателя
                    if partner in users:
                        partner_user = users[partner]
                        partner_messages = partner_user.get("chats", {}).get(session["user"], [])
                        for j, p_msg in enumerate(partner_messages):
                            if p_msg.get("id") == message_id:
                                partner_messages.pop(j)
                                break
                    
                    return jsonify({"success": True})
        
        return jsonify({"success": False, "error": "Message not found"})

@auth.route("/chat/edit-message/<message_id>", methods=["POST"])
def edit_message(message_id):
    if "user" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})
    
    data = request.get_json()
    new_text = data.get("text", "").strip()
    
    if not new_text:
        return jsonify({"success": False, "error": "Message cannot be empty"})
    
    with user_data() as users:
        me = users.get(session["user"])
        if not me:
            return jsonify({"success": False, "error": "User not found"})
        
        for partner, messages in me.get("chats", {}).items():
            for msg in messages:
                if msg.get("id") == message_id and msg.get("from") == session["user"]:
                    # Обновляем текст и добавляем метку о редактировании
                    msg["text"] = new_text
                    msg["edited"] = True
                    msg["edited_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Также обновляем у получателя
                    if partner in users:
                        partner_user = users[partner]
                        partner_messages = partner_user.get("chats", {}).get(session["user"], [])
                        for p_msg in partner_messages:
                            if p_msg.get("id") == message_id:
                                p_msg["text"] = new_text
                                p_msg["edited"] = True
                                p_msg["edited_at"] = msg["edited_at"]
                                break
                    
                    return jsonify({"success": True})
        
        return jsonify({"success": False, "error": "Message not found"})
