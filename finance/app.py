import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, password_check

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


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
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # Retrieve user's stocks
    stocks = db.execute(
        "SELECT symbol, shares, price as purchase_price FROM portfolios WHERE user_id = ?", user_id)

    total_value = 0
    for stock in stocks:
        quote = lookup(stock['symbol'])
        stock['current_price'] = quote['price']
        stock['current_total'] = stock['current_price'] * stock['shares']
        stock['purchase_total'] = stock['purchase_price'] * stock['shares']
        stock['gain_loss'] = stock['current_total'] - stock['purchase_total']
        total_value += stock['current_total']

    # Retrieve user's cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash']
    print(f"User cash on portfolio page: {cash}")  # Debug print statement

    # Calculate grand total
    grand_total = total_value + cash

    return render_template("portfolio.html", stocks=stocks, usd=usd, grand_total=grand_total, cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol = symbol.upper()
        shares = request.form.get("shares")

        if not symbol:
            return apology("Missing symbol")

        data = lookup(symbol)
        if data is None:
            return apology("Invalid symbol")

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("Invalid number of shares")
        except ValueError:
            return apology("Shares must be a positive integer")

        user_id = session["user_id"]
        cash_current = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash']
        print(f"Current cash before purchase: {cash_current}")  # Debug print statement
        total_cost = data["price"] * shares
        print(f"Total cost of purchase: {total_cost}")  # Debug print statement

        if total_cost > cash_current:
            return apology("Insufficient funds")

        db.execute("BEGIN")

        try:
            # Only subtract total cost once
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)
            cash_after_purchase = db.execute(
                "SELECT cash FROM users WHERE id = ?", user_id)[0]['cash']
            print(f"Cash after purchase: {cash_after_purchase}")  # Debug print statement

            original_shares = db.execute(
                "SELECT shares, price FROM portfolios WHERE user_id = ? AND symbol = ?", user_id, symbol)

            if not original_shares:
                db.execute("INSERT INTO portfolios (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                           user_id, data["symbol"], shares, data["price"])
            else:
                original_shares = original_shares[0]
                new_total_shares = shares + original_shares['shares']
                new_average_price = (
                    (original_shares['shares'] * original_shares['price']) + (shares * data["price"])) / new_total_shares
                db.execute("UPDATE portfolios SET shares = ?, price = ? WHERE user_id = ? AND symbol = ?",
                           new_total_shares, new_average_price, user_id, symbol)

            db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, ?, ?, ?, ?)",
                       user_id, data["symbol"], shares, data["price"], "buy")

            db.execute("COMMIT")

            flash("Bought!")
            return redirect("/")

        except Exception as e:
            db.execute("ROLLBACK")
            return apology(f"An error occurred: {str(e)}")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    if request.method == "GET":
        database = db.execute("SELECT * FROM transactions WHERE user_id = ?", session['user_id'])
        return render_template("history.html", database=database, usd=usd)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if lookup(symbol) == None:
            return apology("The symbol is invalid")
        else:
            data = lookup(symbol)
            return render_template("quoted.html", price=data["price"], symbol=data["symbol"], usd=usd)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        username = request.form.get("username")

        if not username:
            return apology("Please fill the username while registering")

        usernames = db.execute("SELECT username FROM users WHERE username = ?", username)

        if usernames:
            return apology("Username is not unique, try another username")

        pass1 = request.form.get("password")
        pass2 = request.form.get("confirmation")

        if not pass1 or not pass2:
            return apology("Passowrd and/or repeated passowrd missing")

        if pass1 != pass2:
            return apology("The Passwords filled out are not the same !")

        password_error = password_check(pass1)
        if password_error:
            return apology(password_error)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, generate_password_hash(pass1))
        return render_template("login.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session['user_id']

    if request.method == "GET":
        symbols = db.execute("SELECT symbol FROM portfolios WHERE user_id = ?", user_id)
        return render_template("sell.html", symbols=symbols)

    if request.method == "POST":
        shares = request.form.get("shares")
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Missing symbol")

        symbol = symbol.upper()

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("Shares must be a positive integer")
        except ValueError:
            return apology("Invalid number of shares")

        db.execute("BEGIN TRANSACTION")

        try:
            stock = db.execute(
                "SELECT shares FROM portfolios WHERE user_id = ? AND symbol = ?", user_id, symbol)

            if not stock or stock[0]['shares'] < shares:
                db.execute("ROLLBACK")
                return apology("Not enough shares")

            quote = lookup(symbol)
            if not quote:
                db.execute("ROLLBACK")
                return apology("Failed to get current price")

            price = quote['price']
            total_sale = price * shares

            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_sale, user_id)

            new_shares = stock[0]['shares'] - shares
            if new_shares == 0:
                db.execute("DELETE FROM portfolios WHERE user_id = ? AND symbol = ?", user_id, symbol)
            else:
                db.execute("UPDATE portfolios SET shares = ? WHERE user_id = ? AND symbol = ?",
                           new_shares, user_id, symbol)

            db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, ?, ?, ?, ?)",
                       user_id, symbol, -shares, price, "sell")

            db.execute("COMMIT")

            flash("Sold!")
            return redirect("/")

        except Exception as e:
            db.execute("ROLLBACK")
            return apology(f"An error occurred: {str(e)}")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change the password"""
    if request.method == "GET":
        return render_template("change_password.html")
    if request.method == "POST":
        old_pass = request.form.get("old_password")
        new_pass = request.form.get("new_password")
        confirm_new_pass = request.form.get("confirm_new_password")

        if not old_pass:
            return apology("must provide password", 403)

        if not new_pass or not confirm_new_pass:
            return apology("Both the New Password fields must be filled")

        if new_pass != confirm_new_pass:
            return apology("The new password fields must be the same")

        password_error = password_check(new_pass)
        if password_error:
            return apology(password_error)

        user = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])

        if len(user) != 1 or not check_password_hash(user[0]["hash"], old_pass):
            return apology("invalid old password", 403)

        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(new_pass), session['user_id'])
        flash("Password successfully changed!")
        return redirect("/")
    
if __name__ == "__main__":
app.run()
