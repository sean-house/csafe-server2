from typing import Tuple
from datetime import datetime
import logging

import os
# import hashlib
# import hmac
# import json
# import traceback

from flask_restful import Resource
from flask import request, jsonify

from models.safe import SafeModel
from schemas.safe import SafeSchema
from libs.crypto import Crypto

# from models.confirmation import ConfirmationModel
# from models.user import UserModel
# from schemas.user import UserSchema
# from libs.mailgun import MailGunException
import messages.en as msgs

safe_schema = SafeSchema()
crypto_handler = Crypto()

class SafeList(Resource):
    @classmethod
    # @jwt_required
    def get(cls):
        return {"safes": [safe_schema.dump(safe) for safe in SafeModel.find_all()]}

class SafeRegister(Resource):
    @classmethod
    def post(cls):
        public_key = crypto_handler.pub_key()
        parms = request.get_json()
        if 'hwid' in parms and 'pkey' in parms:
            # Check if we have a safe with this id already
            this_safe = SafeModel.find_by_id(parms['hwid'])
            if this_safe:
                # We already know about this safe
                return {"error": msgs.SAFE_REGISTRATION_ERROR}, 400
            else:
                now = datetime.utcnow()
                this_safe = SafeModel(
                        hardware_id=parms['hwid'],
                        public_key=parms['pkey'],
                        last_update=now,
                        unlock_time=now
                )
                this_safe.save_to_db()
                logging.info(f"SAFE: Registered new safe with hw_id: {parms['hwid']}")
                return {"key": public_key.decode("utf-8")}, 200
        else:
            return {"error": msgs.SAFE_REGISTRATION_ERROR}, 400

class SafeCheckin(Resource):
    @classmethod
    def post(cls):
        return {"checkin": "diagnostic response"}

