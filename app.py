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

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

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


# Hardcoded profile-page data — replaced with real queries in Step 5
PROFILE_USER = {
    "name": "Demo User",
    "email": "demo@spendly.com",
    "initials": "D",
    "member_since": "2026-07-03",
}

PROFILE_STATS = {
    "total_spent": 8340.25,
    "transaction_count": 6,
    "top_category": "Shopping",
}

PROFILE_TRANSACTIONS = [
    {"date": "2026-07-01", "description": "Groceries for the week", "category": "Food", "amount": 1240.50},
    {"date": "2026-06-28", "description": "Metro card top-up", "category": "Transport", "amount": 350.00},
    {"date": "2026-06-25", "description": "Electricity bill", "category": "Bills", "amount": 2120.00},
    {"date": "2026-06-21", "description": "Pharmacy", "category": "Health", "amount": 480.75},
    {"date": "2026-06-18", "description": "Movie night", "category": "Entertainment", "amount": 650.00},
    {"date": "2026-06-15", "description": "Running shoes", "category": "Shopping", "amount": 3499.00},
]

PROFILE_CATEGORIES = [
    {"name": "Shopping", "total": 3499.00, "percent": 42},
    {"name": "Bills", "total": 2120.00, "percent": 25},
    {"name": "Food", "total": 1240.50, "percent": 15},
    {"name": "Entertainment", "total": 650.00, "percent": 8},
    {"name": "Health", "total": 480.75, "percent": 6},
    {"name": "Transport", "total": 350.00, "percent": 4},
]


@app.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html",
        user=PROFILE_USER,
        stats=PROFILE_STATS,
        transactions=PROFILE_TRANSACTIONS,
        categories=PROFILE_CATEGORIES,
    )


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
