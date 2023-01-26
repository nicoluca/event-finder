from werkzeug.security import check_password_hash, generate_password_hash

from flask import Flask, session, render_template, request, redirect
from flask_session import Session

import sqlite3

from helpers import login_required, apology
import helpers
import db_helpers

app = Flask(__name__)
# Configure application
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

print("Setting up database...")
db_helpers.create_connection()
db_helpers.create_user_table_if_not_exists()
db_helpers.create_event_table_if_not_exists()
db_helpers.create_event_attendees_table_if_not_exists()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db_helpers.get_username_and_hash(str(request.form.get("email")))
        print(rows)
        if rows is None:
            return apology("invalid email", 403)

        print(rows)
        # Ensure username exists and password is correct
        if not check_password_hash(rows[0][1], request.form.get("password")):
            return apology("invalid password", 403)

        # Remember which user has logged in
        session["user_id"] = db_helpers.get_user_id_from_email(request.form.get("email"))[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("Please provide username.", 403)
        elif not request.form.get("password"):
            return apology("Please provide password.", 403)
        elif not request.form.get("confirmation"):
            return apology("Please confirm password.", 403)

        # Check email is valid
        if not helpers.is_valid_email(request.form.get("email")):
            return apology("Please provide a valid email.", 403)
        
        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.", 403)

        # Check email is available
        if db_helpers.check_email_exists(request.form.get("email")):
            return apology("Email already exists.", 403)
        
        # Check username is available
        if db_helpers.check_username_exists(request.form.get("username")):
            return apology("Username already exists.", 403)

        # Insert user into database
        db_helpers.create_user(request.form.get("username"), request.form.get("email"), generate_password_hash(request.form.get("password")))
        session["user_id"] = db_helpers.get_user_id(request.form.get("email"))
        return redirect("/")

    else:
        return render_template("register.html")
