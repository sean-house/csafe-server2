import os

DEBUG = True
PROPAGATE_EXCEPTIONS = True
SQLALCHEMY_DATABASE_URI = os.environ.get(
        "FLASK_DB_URL", "sqlite:///dbase.db"
    )
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.environ.get('FLASK_SECRET', "qwertyuiop")
APP_SECRET_KEY = os.environ.get('FLASK_SECRET', "qwertyuiop")
