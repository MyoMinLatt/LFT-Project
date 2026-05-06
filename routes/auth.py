from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()

# Dummy user (replace with real DB if needed)
class User(UserMixin):
    id = 1
    username = "admin"
    password = "password"  # plain text for demo, use hashing in production

@login_manager.user_loader
def load_user(user_id):
    return User() if int(user_id) == 1 else None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            user = User()
            login_user(user)
            return redirect(url_for("home.home"))
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
