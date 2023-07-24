from flask_app import app
from flask import redirect, request, render_template, session
from flask_app.models.user import User
from flask_app.models.band import Band

# PAGE view user dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    user = User.get_user(session["user_id"])
    return render_template("dashboard.html", user=user,
                           bands=Band.get_all_with_founder())

# PAGE view the user's bands
@app.route("/mybands")
def mybands():
    if "user_id" not in session:
        return redirect("/")
    user = User.get_founder(session["user_id"])
    return render_template("mybands.html", user=user)

# PAGE form for entering a new band
@app.route("/new")
def new_band():
    if "user_id" not in session:
        return redirect("/")
    user = User.get_user(session["user_id"])
    return render_template("new.html", user=user)

# PAGE form for editing an existing band
@app.route("/edit/<int:band_id>")
def edit_band(band_id):
    if "user_id" not in session:
        return redirect("/")
    user = User.get_user(session["user_id"])
    band = Band.get_band(band_id)
    return render_template("edit.html", user=user, band=band)

# ACTION add a new band
@app.route("/add_band", methods=["POST"])
def add_band():
    if "user_id" not in session:
        return redirect("/")
    data = dict(request.form)
    data["found"] = session["user_id"]
    if not Band.validate_band(data):
        return redirect("/new")
    Band.save(data)
    return redirect("/dashboard")

# ACTION update an existing band
@app.route("/update/<int:band_id>", methods=["POST"])
def update(band_id):
    if "user_id" not in session:
        return redirect("/")
    data = dict(request.form)
    data["id"] = band_id
    if not Band.validate_band(data):
        return redirect(f"/edit/{band_id}")
    Band.update(data)
    return redirect("/dashboard")

# ACTION destroy an existing band
@app.route("/destroy/<int:band_id>")
def destroy_band(band_id):
    if "user_id" not in session:
        return redirect("/")
    Band.delete(band_id)
    return redirect("/dashboard")