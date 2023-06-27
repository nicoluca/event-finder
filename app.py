from werkzeug.security import check_password_hash, generate_password_hash

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from dotenv import load_dotenv
import sqlite3

from helpers import login_required, apology
import helpers
import db_helpers

import os

def create_app():
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

    print("Requesting environment variables...")
    load_dotenv()

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
        if "user_id" not in session:
            return redirect("/login")
        if session["user_id"] is None:
            return redirect("/login")
        if not db_helpers.get_username(session["user_id"]):
            return redirect("/login")
        return render_template("index.html", username=db_helpers.get_username(session["user_id"]))

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
            # Ensure username exists 
            if len(rows) != 1 or rows[0][0] is None:
                return apology("invalid email", 403)
            
            # password is correct
            if not check_password_hash(rows[0][1], request.form.get("password")):
                return apology("invalid password", 403)

            # Remember which user has logged in
            session["user_id"] = db_helpers.get_user_id_from_email(request.form.get("email"))

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
            #session["user_id"] = db_helpers.get_user_id(request.form.get("email"))
            return redirect("/")

        else:
            return render_template("register.html")

    ### Event Creation ###
    @app.route("/create", methods=["GET", "POST"])
    def create():
        if request.method == "POST":
            print("Creating event...")
            event = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "datetime_str": request.form.get("datetime"),
            "location": request.form.get("address") + ", " + request.form.get("city") + ", " + request.form.get("postcode"),
            "organiser": session["user_id"]
            }

            if not event["name"] or not event["description"] or not event["datetime_str"] or not event["location"]:
                return apology("Please fill in all fields.", 403)
            print(event)
            db_helpers.create_event(event["name"], event["description"], event["datetime_str"], event["location"], event["organiser"])
            print("Event created successfully:")

            return redirect("/")

        return render_template("create.html", api_key=os.getenv('MAPBOX_TOKEN'))

    ### My Events ###
    @app.route("/myevents/", methods=["GET"])
    def myevents():    
        organiser_events = db_helpers.get_events_by_organiser(session["user_id"])

        formatted_events = []
        for event in organiser_events:
            formatted_events.append({
                "id": event[0],
                "name": event[1],
                "description": event[2],
                "datetime": event[3],
                "location": event[4],
                "attending": db_helpers.get_number_of_attendees(event[0]),
                "organiser": event[5]
            })
        print(formatted_events)

        attending_events = db_helpers.get_events_by_attendee(session["user_id"])
        formatted_attending_events = []
        for event in attending_events:
            formatted_attending_events.append({
                "id": event[0],
                "name": event[1],
                "description": event[2],
                "datetime": event[3],
                "location": event[4],
                "organiser": db_helpers.get_username(event[5])
            })
        print(formatted_attending_events)
        return render_template("myevents.html", my_events=formatted_events, attending_events=formatted_attending_events)

    ### Delete Event ###
    @app.route("/myevents/<int:event_id>", methods=["DELETE"])
    def delete(event_id):
        print("Deleting event...")
        db_helpers.delete_event(event_id)
        print("Event deleted successfully:" + str(event_id))
        return '', 204
    
    ### Leave Event ###
    @app.route("/myevents/<int:event_id>", methods=["POST"])
    def leave(event_id):
        print("Leaving event...")
        db_helpers.leave_event(user_id=session["user_id"], event_id=event_id)
        print("Event left successfully:" + str(event_id))
        return '', 204

    ### Browse Events ###
    @app.route("/browse/", methods=["GET"])
    def browse():
        events = db_helpers.get_events()
        print(events)
        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event[0],
                "name": event[1],
                "description": event[2],
                "datetime": event[3],
                "location": event[4],
                "organiser": db_helpers.get_username(event[5]),
                "attending": db_helpers.check_user_is_attending_event(user_id=session["user_id"], event_id=event[0]),
                "is_organiser": event[5] == session["user_id"]
            })
        print(formatted_events)
        return render_template("browse.html", events=formatted_events, api_key=os.getenv('MAPBOX_TOKEN'))

    ### Join Event ###
    @app.route("/browse/<int:event_id>", methods=["POST"])
    def join(event_id):
        print("Joining event:" + str(event_id))
        if db_helpers.check_user_is_attending_event(user_id=session["user_id"], event_id=event_id):
            return apology("You are already attending this event.", 403)
        db_helpers.join_event(session["user_id"], event_id)
        print("Event joined successfully:" + str(event_id))
        return redirect("/browse/")
    
    return app
    
app = create_app()