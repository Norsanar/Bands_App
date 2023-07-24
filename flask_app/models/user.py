from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import band as band_model
import re

# regex for valid emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db = "band_together"
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.found_bands = []

    # return the users full name
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # return all users
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for user in results:
            users.append(cls(user))
        return users

    # get one user by id
    @classmethod
    def get_user(cls, id):
        query = "SELECT * FROM users WHERE id=%(id)s;"
        if isinstance(id, int):
            data = {"id": id}
        elif isinstance(id, dict):
            data = id
        # there should only be one entry
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return False

    # return the user with a particular email. May either enter a string or dictionary
    @classmethod
    def get_user_by_email(cls, email):
        query = "SELECT * FROM users WHERE email=%(email)s;"
        if isinstance(email, str):
            data = {"email": email}
        elif isinstance(email, dict):
            data = email
        # there should only be one entry
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return False

    # get all of a persons founded bands
    @classmethod
    def get_founder(cls, id):
        if isinstance(id, int):
            data = {"id": id}
        elif isinstance(id, dict):
            data = id
        query = "SELECT * FROM users LEFT JOIN bands " + \
                "ON bands.founder_id = users.id WHERE users.id = %(id)s;"
        bands = connectToMySQL(cls.db).query_db(query, data)
        founder = cls(bands[0])
        for band in bands:
            # fortunately, there is only one name clash here
            new_band = dict(band)
            new_band["id"] = band["bands.id"]
            founder.found_bands.append(band_model.Band(new_band))
        return founder

    # add a user into the database
    @classmethod
    def save(cls, data):
        # the database has default values for created_at and updated_at
        query = "INSERT INTO users (first_name, last_name, password, " + \
                "email) VALUES " + \
                "(%(fname)s, %(lname)s, %(pass)s, %(email)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    # remove a user from the database
    @classmethod
    def delete(cls, id):
        query = "DELETE FROM users WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, {"id": id})

    # check that a new user is valid
    @staticmethod
    def validate_user(user):
        is_valid = True
        # check that first name is only letters
        if not user["fname"].isalpha():
            flash("First name contains non-letter characters", "reg_err")
            is_valid = False
        # check that user name is over length
        if len(user["fname"]) < 2:
            flash("First name is less than two characters", "reg_err")
            is_valid = False
        # check that last name is only letters
        if not user["lname"].isalpha():
            flash("Last name contains non-letter characters", "reg_err")
            is_valid = False
        # check that user name is over length
        if len(user["lname"]) < 2:
            flash("Last name is less than two characters", "reg_err")
            is_valid = False
        # check for valid email address
        if not EMAIL_REGEX.match(user["email"]):
            flash("Email address is not valid", "reg_err")
            is_valid = False
        # make sure email is unique
        if User.get_user_by_email(user["email"]):
            flash("Email address is already taken", "reg_err")
            is_valid = False
        # check password is over eight characters
        if len(user["pass"]) < 8:
            flash("Password is less than eight characters", "reg_err")
            is_valid = False
        # check that passwords match
        if user["pass"] != user["pconf"]:
            flash("Passwords do not match", "reg_err")
            is_valid = False
        return is_valid