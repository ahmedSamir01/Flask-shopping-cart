from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)

db = SQL("sqlite:///info.db")

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# define a route for main page
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    if session["name"]: 
        return redirect("/")
    return render_template("login.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":
        name = request.form.get("name")
        mail = request.form.get("mail")

        savedName = db.execute("SELECT name FROM users WHERE mail = ?", mail)
        mails = db.execute("SELECT mail FROM users WHERE mail = ?", mail)
        
        session["name"] = name
        session["mail"] = mail

        # if first time (register)
        if not mails:
            if not name == "admin": db.execute("INSERT INTO users (name, mail) VALUES(?, ?)", name, mail)
            print("register")
            return redirect("/profile")

        else:
            # login not first time
            if name == savedName[0]["name"]:
                print("login")
                return redirect("/profile")
            else:
                session["name"] = None
                session["mail"] = None
                return 'already used!'

    # if only reload with name (user)
    if session["name"]:
        items = db.execute("SELECT * FROM items")
        return render_template("profile.html", name=session["name"], items=items)

    # if only reload with no name (user)
    return redirect("/login")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    # validation
    if not session.get("name"): 
        return redirect("/login")

    if request.form.get("id"):
        id = request.form.get("id")
        # Delete dependencies then  the user
        db.execute("DELETE FROM cart WHERE item_id = ?", id)
        db.execute("DELETE FROM users WHERE id = ?", id)
    users = db.execute("SELECT * FROM users")
    return render_template("dashboard.html", users=users)

@app.route("/cart", methods=["GET", "POST"])
def cart():

    # validation
    if not session.get("name"): 
        return redirect("/login")

    item_id = db.execute("SELECT id FROM users WHERE mail = ?", session["mail"])[0]["id"]
    session["id"] = item_id
    if request.method == "POST":
        if request.form.get("id"):
            id = request.form.get("id")
            db.execute("DELETE FROM cart WHERE id = ?", id)
        else:
            title = request.form.get("title")
            db.execute("INSERT INTO cart(title, item_id) VALUES(?, ?)", title, item_id)
        
    items = db.execute("SELECT * FROM cart WHERE item_id = ?", session["id"])
    return render_template("cart.html", items=items)

@app.route("/logout")
def logout():
    session["name"] = None
    session["mail"] = None
    session["id"] = None
    return redirect("/")