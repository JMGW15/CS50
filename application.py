from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from functools import wraps
import time
from datetime import datetime

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database for t4nt
db = SQL("sqlite:///t4nt.db")

#require login for the app
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def login():

    # forget any user_id
    session.clear()

    if request.method == "POST":
        # set incoming login submission as login variable
        login = request.form.get("login")
        #print(login)

        #check if the login is in the eligible db
        user_check = db.execute("SELECT login FROM eligible WHERE login = :login", login=request.form.get("login"))
        #print(user_check)

        #if the login is not in the db surface error - could be more gracefully done in javascript
        if user_check == []:
            return render_template("login_error.html")

        # remember which user has logged in
        session["user_id"] = user_check[0]["login"]

        # redirect user to home page
        return redirect(url_for("schedule"))

    #else send user to login template
    else:
        return render_template("login.html")


@app.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():

    #get current date - https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
    currentdate = datetime.now().strftime('%Y-%m-%d')
    #print(currentdate)
    #remember the logged in user per their login name
    login=session["user_id"]

    # if user reached route via GET
    if request.method == "GET":

        #http://sqlite.1065341.n5.nabble.com/time-in-AM-PM-td9114.html converting time
        #retrieve all the events they are registered from in the registered databse, but join with the events db to retrieve event info
        #use case constraint to modify 24hr time to 12hr time
        registered_events_data = db.execute("SELECT events.event_id as reg_event_id, events.event_date as reg_event_date, events.event_name as reg_event_name, events.event_description as reg_event_description, events.event_presenter as reg_event_presenter, CASE WHEN CAST(strftime('%H', events.event_start_time, 'localtime') AS INTEGER) = 12 THEN strftime('%H:%M', events.event_start_time, 'localtime') || ' PM' WHEN CAST(strftime('%H', events.event_start_time, 'localtime') AS INTEGER) > 12 THEN strftime('%H:%M', events.event_start_time, '-12 Hours', 'localtime') || ' PM' ELSE strftime('%H:%M', events.event_start_time, 'localtime') || ' AM' END  as reg_event_start_time, events.event_end_time as reg_event_end_time, events.event_location as reg_event_location FROM events INNER JOIN registered ON events.event_ID = registered.event_ID where login = :login ORDER BY reg_event_date asc", login = login)
        #print(registered_events_data)

        #create an empty dictionary
        registered_events=[]
        #print(registered_events)

        #if the returning data is not null
        if registered_events_data != []:

            #loop over every row in the query data
            for rows in registered_events_data:
                #create list
                registered_event_info = {}
                registered_event_info["reg_event_id"] = rows["reg_event_id"]
                registered_event_info["reg_event_date"] = rows["reg_event_date"]
                registered_event_info["reg_event_name"] = rows["reg_event_name"]
                registered_event_info["reg.event_description"] = rows["reg_event_description"]
                registered_event_info["reg_event_presenter"] = rows["reg_event_presenter"]
                registered_event_info["reg_event_start_time"] = rows["reg_event_start_time"]
                registered_event_info["reg_event_end_time"] = rows["reg_event_end_time"]
                registered_event_info["reg_event_location"] = rows["reg_event_location"]

                #append data to the list
                registered_events.append(registered_event_info)

        # query database for future events events
        # use case constraint to modify 24hr time to 12hr time
        events_data = db.execute("SELECT event_ID, event_date, event_name, event_description, event_presenter, CASE WHEN CAST(strftime('%H', event_start_time, 'localtime') AS INTEGER) = 12 THEN strftime('%H:%M', event_start_time, 'localtime') || ' PM' WHEN CAST(strftime('%H', event_start_time, 'localtime') AS INTEGER) > 12 THEN strftime('%H:%M', event_start_time, '-12 Hours', 'localtime') || ' PM' ELSE strftime('%H:%M', event_start_time, 'localtime') || ' AM' END  as event_start_time, event_end_time, event_location, total_seats, filled_seats FROM events WHERE event_date >= date('now') ORDER BY event_date asc")

        #create empty dictionary
        events=[]
        #print(events_data)

        #if the query returns non null
        if events_data != []:

            #loop over every row in the query data
            for rows in events_data:
                #create list
                event_info = {}
                event_info["event_id"] = rows["event_ID"]
                event_info["event_date"] = rows["event_date"]
                event_info["event_name"] = rows["event_name"]
                event_info["event_description"] = rows["event_description"]
                event_info["event_presenter"] = rows["event_presenter"]
                event_info["event_start_time"] = rows["event_start_time"]
                event_info["event_end_time"] = rows["event_end_time"]
                event_info["event_location"] = rows["event_location"]
                event_info["event_total_seats"] = rows["total_seats"]
                event_info["event_filled_seats"] = rows["filled_seats"]

                #append data to the list
                events.append(event_info)

        #return dictionaries and login variable to the schedule template
        return render_template("schedule.html", events=events, registered_events=registered_events, login=login)

    else:
        return redirect(url_for("schedule"))

@app.route("/deregister", methods=["GET", "POST"])
@login_required
def deregister():
    # if user reached route via GET since we are sending an event parameter through the URL
    if request.method == "GET":

        #remember the login of the user
        login=session["user_id"]

        # set incoming "e" value to a variable.  This represents the event ID
        event_reg_id=request.args.get("e")
        #print(event_reg_id)

        #if a person deregisters, delete that row from the registered table, set open seats in the events table to +1, and set filled seats in the events table to -1
        row = db.execute("DELETE from registered where event_ID = :event_ID AND login = :login", event_ID=event_reg_id, login=login)
        update_open_seats = db.execute("UPDATE events SET open_seats = (open_seats + 1) WHERE event_id = :event_id", event_id=event_reg_id)
        update_filled_seats = db.execute("UPDATE events SET filled_seats = (filled_seats - 1) WHERE event_id = :event_id", event_id=event_reg_id)
        #print(update_open_seats)
        #print(update_filled_seats)
        #return redirect(url_for("schedule"))

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():

    # if user reached route via GET since the event ID is passed in the e parameter
    if request.method == "GET":

        #remember the individual that is logged in
        login=session["user_id"]

        # set incoming "e" value to a variable
        event_reg_id=request.args.get("e")
        #print(event_reg_id)

        #confirm that event exists
        events_data = db.execute("SELECT event_ID FROM events WHERE event_ID = :event_ID", event_ID=event_reg_id)
        #print(events_data)

        #if the event data is null render error - could be handled more gracefully
        if events_data == []:
            return render_template("register_error.html")

        #if the event data is not null
        else:
            #check if session is full
            open_seats = db.execute("SELECT open_seats FROM events WHERE event_ID = :event_ID", event_ID=event_reg_id)
            #print(open_seats)

            #check if user already registered
            registered_already = db.execute("SELECT * FROM registered WHERE login = :login AND event_ID = :event_ID", event_ID=event_reg_id, login=login)
            #print(registered_already)

            #if they are already registered render error - could be handled more gracefully
            if not registered_already == []:
                return render_template("register_error1.html")

            #if open seats is less than 1 render error - could be handled more gracefully
            if (open_seats[0]["open_seats"])< 1:
                return render_template("register_error2.html")

            #if there is availability and they have not registered previously, enter a new row in the registered table
            row = db.execute("INSERT INTO registered (event_ID, login, action) VALUES(:event_ID, :login, :action)", event_ID=event_reg_id, login=login, action="registered")
            #print(row)
            #update open seats in the events table +1 and filled seats in the events table -1
            update_open_seats = db.execute("UPDATE events SET open_seats = (open_seats - 1) WHERE event_id = :event_id", event_id=event_reg_id)
            update_filled_seats = db.execute("UPDATE events SET filled_seats = (filled_seats + 1) WHERE event_id = :event_id", event_id=event_reg_id)

        #drop them back at the schedule page
        return redirect(url_for("schedule"))

    else:
        return render_template("schedule.html")

@app.route("/register_error", methods=["GET", "POST"])
def register_error():

     # if user reached route via GET
    if request.method == "GET":
        #hardcoded error
        return render_template(
            "register_error.html")

    else:
        return render_template("register_error.html")

@app.route("/register_error1", methods=["GET", "POST"])
def register_error1():

     # if user reached route via GET
    if request.method == "GET":
        #hardcoded error
        return render_template("register_error1.html")

    else:
        return render_template("register_error1.html")


@app.route("/register_error2", methods=["GET", "POST"])
def register_error2():

     # if user reached route via GET
    if request.method == "GET":
        #hardcoded error
        return render_template("register_error2.html")

    else:
        return render_template("register_error2.html")

@app.route("/events", methods=["GET", "POST"])
@login_required
def events():

     # if user reached route via POST
    if request.method == "POST":
        #print(request.form.get("total_seats"))
        #print(request.form.get("event_start_time"))
        #print(request.form.get("event_date"))
        #print(request.form.get("event_name"))

        #take incoming values and insert a new row into the events db
        row = db.execute("INSERT INTO events (event_date, event_name, event_description, event_presenter, event_start_time, event_end_time, event_location, total_seats) VALUES(:event_date, :event_name, :event_description, :event_presenter, :event_start_time, :event_end_time, :event_location, :total_seats)", event_date=request.form.get("event_date"), event_name=request.form.get("event_name"), event_description=request.form.get("event_description"), event_presenter=request.form.get("event_presenter"), event_start_time=request.form.get("event_start_time"), event_end_time=request.form.get("event_end_time"), event_location=request.form.get("event_location"), total_seats=request.form.get("total_seats"))
        #grab the new event ID - could introduce race conditions
        max_event = db.execute("SELECT max(event_id) as max_event FROM events")
        #print(max_event)
        #update open seats to equal total seats
        set_open_seats = db.execute("UPDATE events SET open_seats = total_seats WHERE event_id = :event_id", event_id=max_event[0]["max_event"])

        #drop at the schedule to see the new event in the schedule
        return redirect(url_for("schedule"))
    else:
        return render_template("events.html")



@app.route("/list", methods=["GET", "POST"])
@login_required
def list():

    #remember login
    login=session["user_id"]

    # if user reached route via GET
    if request.method == "GET":

        #capture incoming event ID in a variable
        event_reg_id=request.args.get("e")

        #query db for event name and store in a variable
        event_name = db.execute("SELECT event_name FROM events WHERE event_ID = :event_ID", event_ID=event_reg_id)
        event_name_sm=event_name[0]["event_name"]

        #query registered for list of future events individual is registered for
        lists_events_data = db.execute("SELECT events.event_name as list_event_name, eligible.login as list_login, eligible.name as list_name, eligible.email as list_email FROM eligible INNER JOIN registered ON eligible.login = registered.login INNER JOIN events ON registered.event_id = events.event_id where registered.event_id = :registered_event_id", registered_event_id = event_reg_id)

        #create empty dict
        lists_events=[]
        #print(lists_events_data)

        #loop over every row in the query data
        for rows in lists_events_data:
            #create list
            lists_event_info = {}
            lists_event_info["list_login"] = rows["list_login"]
            lists_event_info["list_name"] = rows["list_name"]
            lists_event_info["list_email"] = rows["list_email"]

           #append list
            lists_events.append(lists_event_info)

        #send dictionaries to the template for lists
        return render_template("list.html", lists_events=lists_events, event_name_sm=event_name_sm)

@app.route("/about", methods=["GET", "POST"])
def about():

     # if user reached route via POST
    if request.method == "POST":
        return render_template("about.html")

    else:
        return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():

     # if user reached route via POST
    if request.method == "POST":
        return render_template("contact.html")

    else:
        return render_template("contact.html")