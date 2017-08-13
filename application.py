from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *
import helpers

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

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():

 # if user reached route via POST
    if request.method == "GET":
    
         # query database for username
        portfolio_data = db.execute("SELECT symbol, SUM(shares) AS shares FROM portfolio WHERE id = :id GROUP BY symbol", id = session["user_id"])
        portfolio=[]
        user_cash=0
        grand_total=0
        
        if portfolio_data != []:
            
            #loop over every row in the query data        
            for rows in portfolio_data:
                symbols = rows["symbol"] 
                portfolio_lookup = lookup(symbols)
                # create empty list
                portfolio_info = {}
                portfolio_info["symbol"] = portfolio_lookup["symbol"]
                portfolio_info["shares"] = rows["shares"]
                portfolio_info["name"] = portfolio_lookup["name"]
                portfolio_info["price"] = portfolio_lookup["price"]
                portfolio_info["value"] = portfolio_info["shares"] * portfolio_lookup["price"]
                #portfolio_dict = {'symbol': symbol, 'name': portfolio_lookup["name"], 'shares': total_shares, 'price': portfolio_lookup["price"], 'value': value}
                
                #add new list items to dictionary
                if portfolio_info["shares"] > 0:
                    portfolio.append(portfolio_info)
            
            #get curent cash from user table
            current_cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
            user_cash = (round(current_cash[0]["cash"], 2))
            
            #create variable for account value
            account_value = 0
            
            #iterate on portfolio table to calc account value from adding value field
            for i in range(len(portfolio)):
                account_value += (round(portfolio[i]['value'], 2))
            
            print(account_value)
            
            grand_total = user_cash + account_value
            
            print(grand_total)
            
            #return the dictionary to the html template
            return render_template("index.html", portfolio=portfolio, user_cash=user_cash, grand_total=grand_total)
        
        else:
            #get curent cash from user table
            current_cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
            user_cash = (round(current_cash[0]["cash"], 2))
            
            #create variable for account value
            account_value = 0
            print(account_value)
            
            grand_total = user_cash + account_value
            print(grand_total)
            
            #return the dictionary to the html template
            return render_template("index.html", user_cash=user_cash, grand_total=grand_total)
        
        return render_template("index.html", portfolio=portfolio, user_cash=user_cash, grand_total=grand_total)
            
    else:
        return redirect(url_for("index"))
        

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    # if user reached route via POST
    if request.method == "POST":
    
        # ensure symbol was submitted  
        if not request.form.get("symbol"):
            return apology("Must provide stock symbol")
            
        # ensure num of share was submitted
        if not request.form.get("shares"):
            return apology("Must provide number of shares")
            
        #lookup symbol
        symbol_detail = lookup(request.form.get("symbol"))
        
        #if the lookup function returns nothing - return apology
        if symbol_detail == None:
            return apology("Stock symbol not found")
        
        #return shares as an integer
        reqshares = int(request.form.get("shares"))
        print(reqshares)
        
        #return the users cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        
        #calculate total cost
        total_cost = (symbol_detail["price"] * reqshares)
        print(total_cost)
        
        if float(total_cost) > float(user_cash[0]["cash"]):
            return apology("Not enough cash to complete the purchse")
        
        #add to portfolio and subtract cash
        else:
            db.execute("INSERT INTO portfolio (id, buy_price, name, symbol, shares) VALUES(:id, :buy_price, :name, :symbol, :shares)", id = session["user_id"], buy_price=symbol_detail["price"], name=symbol_detail["name"], symbol=symbol_detail["symbol"], shares=request.form.get("shares"))
            
            #subtract purchase price from cash
            update_cash = db.execute("UPDATE users SET cash = (cash - :buy_price) WHERE id = :id", buy_price=total_cost, id = session["user_id"])
            print(update_cash)
        
            return redirect(url_for("index"))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")
        


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    
     # if user reached route via POST
    if request.method == "GET":
    
         # query database for username
        portfolio_data = db.execute("SELECT buy_timestamp, symbol, shares, buy_price, CASE WHEN shares <0 THEN 'SELL'ELSE 'BUY' END AS action FROM portfolio WHERE id = :id ORDER BY buy_timestamp ASC", id = session["user_id"])
        portfolio=[]
        #user_cash=0
        #grand_total=0
        
        if portfolio_data != []:
            
            #loop over every row in the query data        
            for rows in portfolio_data:
                portfolio_info = {}
                portfolio_info["timestamp"] = rows["buy_timestamp"]
                portfolio_info["symbols"] = rows["symbol"] 
                portfolio_info["shares"] = rows["shares"]
                portfolio_info["buy_price"] = rows["buy_price"]
                portfolio_info["action"] = rows["action"]
                #portfolio_dict = {'symbol': symbol, 'name': portfolio_lookup["name"], 'shares': total_shares, 'price': portfolio_lookup["price"], 'value': value}
                
                #add new list items to dictionary
                portfolio.append(portfolio_info)
            
            #return the dictionary to the html template
            return render_template("history.html", portfolio=portfolio)
        
        return render_template("history.html", portfolio=portfolio)
    
    else:
        return render_template("history.html")
        
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct  
        print("incoming password: " + request.form.get("password"))
        print(rows)
        print(rows[0]["hash"])
        
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    
    # if user reached route via POST
    if request.method == "POST":
         
        # ensure symbol was submitted  
        if not request.form.get("symbol"):
            return apology("Must provide stock symbol")
        
        #lookup symbol
        symbol_detail = lookup(request.form.get("symbol"))
        
        if symbol_detail == None:
            return apology("Stock symbol not found")
        
        else:
            print("redirecting to quoted")
            return render_template("quoted.html", symbol=symbol_detail["symbol"], price=symbol_detail["price"], name=symbol_detail["name"])
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        print("redirecting to quote")
        return render_template("quote.html")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # forget any user_id
    session.clear()
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
            
        # ensure passwordcheck was submitted
        elif not request.form.get("passwordcheck"):
            return apology("must confirm password")
            
        # ensure passwordcheck was submitted
        elif request.form.get("password")!=request.form.get("passwordcheck"):
            return apology("passwords must match")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) == 1:
            return apology("username already exists")
            
        # hash password
        hash_value = pwd_context.hash(request.form.get("password"))

        #register the username (look into hash function)
        row = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form["username"], hash=hash_value)

        # remember which user has logged in
        session["user_id"] = row

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
        

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    
    # if user reached route via POST
    if request.method == "POST":
        
        # ensure symbol was submitted  
        if not request.form.get("symbol"):
            return apology("Must provide stock symbol")
            
        # ensure num of share was submitted
        if not request.form.get("shares"):
            return apology("Must provide number of shares")
            
        #lookup symbol
        sell_symbol_detail = lookup(request.form.get("symbol"))
        print(sell_symbol_detail)
        
        #if the lookup function returns nothing - return apology
        if sell_symbol_detail == None:
            return apology("Stock symbol not valid")
        
        #return shares as an integer
        sell_shares = int(request.form.get("shares"))
        print(sell_shares)
        
        portfolio_sell_shares = sell_shares * -1
        print(portfolio_sell_shares)
        
        # query database for username
        portfolio_data = db.execute("SELECT symbol, SUM(shares) AS shares FROM portfolio WHERE id = :id AND symbol = :symbol GROUP BY symbol", id = session["user_id"], symbol = request.form["symbol"])
        print(portfolio_data)
        
        
        if portfolio_data == []:
            return apology("You do not own this stock")
        
        if int(portfolio_data[0]["shares"]) == 0:
            return apology("You do not own this stock")
            
        if int(sell_shares) > int(portfolio_data[0]["shares"]):
            return apology("You do not own enough shares")
            
        if int(sell_shares) <= int(portfolio_data[0]["shares"]):
            profit = sell_shares * sell_symbol_detail["price"]
            print(profit)
            db.execute("INSERT INTO portfolio (id, buy_price, name, symbol, shares) VALUES(:id, :buy_price, :name, :symbol, :shares)", id = session["user_id"], buy_price=sell_symbol_detail["price"], name=sell_symbol_detail["name"], symbol=sell_symbol_detail["symbol"], shares=portfolio_sell_shares)
            update_cash = db.execute("UPDATE users SET cash = (cash + :profit) WHERE id = :id", profit=profit, id = session["user_id"])
            return redirect(url_for("index"))
        
        else: 
            return redirect(url_for("index"))
            
    else:
        return render_template("sell.html")

    
    return redirect(url_for("index"))

@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    
     # if user reached route via POST
    if request.method == "POST":
        
        # ensure symbol was submitted  
        if not request.form.get("cash"):
            return apology("Must provide cash amount to deposit")
            
        new_cash = request.form.get("cash")
        update_cash = db.execute("UPDATE users SET cash = (cash + :new_cash) WHERE id = :id", new_cash = new_cash, id = session["user_id"])
        return redirect(url_for("index"))
        
    else:    
        return render_template("deposit.html")
    
    