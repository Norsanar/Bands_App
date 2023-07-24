import os
# since flask runs twice in debug mode, this prevents mysqlconnection from
# unnecessarily asking for the database user and password. Credit:
# https://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode#:~:text=When%20building%20a%20Flask%20service,Flask%20service%20only%20initialises%20once.
if not __name__ == "__main__" or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    from flask_app.controllers import users, bands

from flask_app import app

if __name__=="__main__":
    app.run(debug=True)