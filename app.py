from dotenv import load_dotenv
load_dotenv(verbose=True)  # Must do this before anything else.  Mailgun loads env variables on load

import logging
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from marshmallow import ValidationError

import os
import sys

from db import db
from ma import ma
from resources.user import UserRegister, UserList, UserLogin, TokenRefresh
# from resources.measurement import Measurement, MeasurementList
from resources.confirmation import Confirmation, ConfirmationByUser
app = Flask(__name__)
cors = CORS(app)
print(f"Using settings from {os.environ['APPLICATION_SETTINGS']}")
app.config.from_object('default_config')
app.config.from_envvar("APPLICATION_SETTINGS")

api = Api(app)

jwt = JWTManager(app)
migrate = Migrate(app=app, db=db)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_error(err):
    return jsonify(err.messages), 400


api.add_resource(UserRegister, "/register")
api.add_resource(UserList, "/users")
# api.add_resource(Measurement, "/measurement")
# api.add_resource(MeasurementList, "/measurements/<string:location>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Confirmation, "/confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/check/<int:user_id>")

if __name__ == "__main__":
    intent = os.environ.get('FLASK_INTENT', None)
    # Set up logging
    if intent == 'prod':
        loglevel = logging.INFO
    else:
        loglevel = logging.DEBUG
    logging.basicConfig(filename='app.log',
                        format='%(asctime)s %(message)s',
                        filemode='w',
                        level=loglevel)

    db.init_app(app)
    ma.init_app(app)
    if intent == 'dev':
        print('Running with "dev" environment')
        logging.info('Running with "dev" environment')
        app.run(port=5000, debug=True, use_reloader=False)  # important to mention debug=True
    elif intent == 'prod':
        print('Running with "prod" environment')
        logging.info('Running with "prod" environment')
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print('ERROR:  No FLASK_INTENT environment variable')
        logging.error('ERROR:  No FLASK_INTENT environment variable')
        sys.exit(-1)
