from flask_app import app
from flask import redirect, request, render_template, session, flash
from flask_bcrypt import Bcrypt
from flask_app.models.user import User

bcrypt = Bcrypt(app)

# PAGE create a new user
@app.route("/")
def home():
    return render_template("index.html")

# ACTION login user
@app.route("/login", methods=["POST"])
def login():
    user = User.get_user_by_email(request.form)
    if not (user and
            bcrypt.check_password_hash(user.password, request.form["pass"])):
        flash("Email or password is invalid", "login")
        return redirect("/")
    session["user_id"] = user.id
    return redirect("/dashboard")

# ACTION logout user
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ACTION add new user to database
@app.route("/add_user", methods=["POST"])
def add_user():
    data = dict(request.form)
    if not User.validate_user(data):
        return redirect("/")
    data["pass"] = bcrypt.generate_password_hash(data["pass"])
    user_id = User.save(data)
    if user_id:
        session["user_id"] = user_id
    return redirect("/dashboard")