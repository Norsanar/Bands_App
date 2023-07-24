from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Band:
    db = "band_together"
    def __init__(self, data, founder=None):
        self.id = data["id"]
        self.founder = founder
        self.name = data["name"]
        self.genre = data["genre"]
        self.city = data["city"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    # return one band by id
    @classmethod
    def get_band(cls, id):
        query = "SELECT * FROM bands WHERE id=%(id)s;"
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

    # return all bands with the founder
    @classmethod
    def get_all_with_founder(cls):
        query = "SELECT * FROM bands JOIN users " + \
                "ON users.id = bands.founder_id ORDER BY users.id;"
        results = connectToMySQL(cls.db).query_db(query)
        founders = []
        if not results:
            return founders
        for row in results:
            # check if we should move onto the next founder
            if not (len(founders) and \
                    founders[-1].found_bands[0].id == row["users.id"]):
                new_founder = dict(row)
                new_founder["id"] = row["users.id"]
                founders.append(user.User(new_founder))
            founders[-1].found_bands.append(cls(row, founders[-1]))
        bands = []
        for founder in founders:
            bands += founder.found_bands
        return bands

    # add a band into the database
    @classmethod
    def save(cls, data):
        # the database has default values for created_at and updated_at
        query = "INSERT INTO bands (founder_id, name, genre, city) VALUES " + \
                "(%(found)s, %(name)s, %(genre)s, %(city)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    # update a band in the database
    @classmethod
    def update(cls, data):
        query = "UPDATE bands SET name = %(name)s, genre = %(genre)s, " + \
                "city = %(city)s, updated_at = NOW() WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    # remove a band from the database
    @classmethod
    def delete(cls, id):
        if isinstance(id, int):
            data = {"id": id}
        elif isinstance(id, dict):
            data = id
        query = "DELETE FROM bands WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    # check that a new band is valid
    @staticmethod
    def validate_band(band):
        is_valid = True
        if len(band["name"]) < 2:
            flash("Band name is less than two characters", "reg_err")
            is_valid = False
        if len(band["genre"]) < 2:
            flash("Music genre is less than two characters", "reg_err")
            is_valid = False
        if len(band["city"]) < 1:
            flash("Home city is blank", "reg_err")
            is_valid = False
        return is_valid