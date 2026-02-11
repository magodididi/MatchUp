from flask import Flask, render_template, session, redirect, url_for
from auth.routes import auth
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(auth)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from utils.storage import load_users

@app.route("/")
def index():
    user_logged_in = "user" in session
    user = None
    if user_logged_in:
        users = load_users()
        user = users.get(session["user"])
    return render_template("index.html", user_logged_in=user_logged_in, user=user)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
