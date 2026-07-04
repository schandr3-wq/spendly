import functools
import sqlite3

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from database.db import (
    create_user,
    get_db,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
    update_user,
    update_user_password,
)

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key"

with app.app_context():
    init_db()
    seed_db()


def login_required(view):
    """Redirect to the login page if no user is signed in."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    """Return the signed-in user's row, or None if the account is gone."""
    return get_user_by_id(session["user_id"])


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method != "POST":
        abort(405)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return render_template("register.html")

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("register.html")

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        flash("Email already registered.", "error")
        return render_template("register.html")

    flash("Account created. Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("login.html")

    if request.method != "POST":
        abort(405)

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("All fields are required.", "error")
        return render_template("login.html")

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    flash("Welcome back, {}!".format(user["name"]), "success")
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if user is None:
        session.clear()
        flash("Please sign in to continue.", "error")
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("profile.html", user=user)

    if request.method != "POST":
        abort(405)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name or not email:
        flash("All fields are required.", "error")
        return redirect(url_for("profile"))

    try:
        update_user(user["id"], name, email)
    except sqlite3.IntegrityError:
        flash("Email already registered.", "error")
        return redirect(url_for("profile"))

    session["user_name"] = name
    flash("Account details updated.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/password", methods=["POST"])
@login_required
def profile_password():
    user = current_user()
    if user is None:
        session.clear()
        flash("Please sign in to continue.", "error")
        return redirect(url_for("login"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("All fields are required.", "error")
        return redirect(url_for("profile"))

    if not check_password_hash(user["password_hash"], current_password):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("profile"))

    if new_password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("profile"))

    update_user_password(user["id"], new_password)
    flash("Password updated.", "success")
    return redirect(url_for("profile"))


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
