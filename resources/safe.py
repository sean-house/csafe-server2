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
from flask_jwt_extended import jwt_required

from models.safe import SafeModel, SafeEventModel
from schemas.safe import SafeSchema
from libs.crypto import Crypto

# from models.confirmation import ConfirmationModel
# from models.user import UserModel
# from schemas.user import UserSchema
# from libs.mailgun import MailGunException
import messages.en as msgs

safe_schema = SafeSchema()
crypto_handler = Crypto()

event_codes = {
    "STARTING_OPERATION": 1,
    "SAFE_LOCKED": 2,
    "SAFE_OPEN": 3,
    "SAFE_TERMINATED": 999
}
DEFAULT_EVENT = 800

class SafeList(Resource):
    @classmethod
    # @jwt_required
    def get(cls):
        return {"safes": [safe_schema.dump(safe) for safe in SafeModel.find_all()]}

class AvailableSafes(Resource):
    @classmethod
    @jwt_required
    def get(clscls):
        return {"safes": [safe_schema.dump(safe) for safe in SafeModel.find_available()]}

class SafeRegister(Resource):
    @classmethod
    def post(cls):
        public_key = crypto_handler.pub_key()
        parms = request.get_json()
        print(f"Received register request: {parms}")
        if 'hwid' in parms and 'pkey' in parms:
            # Check if we have a safe with this id already
            this_safe = SafeModel.find_by_id(parms['hwid'])
            if this_safe:
                # We already know about this safe
                logging.info(f"SAFE: Rejected repeated safe registration hw_id: {parms['hwid']}")
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
        valid_request = False
        now = datetime.utcnow()
        parms = request.get_json()
        if all(map(lambda x: x in parms, ['hwid', 'sig', 'msg'])):
            # Check if we have a safe with this ID
            this_safe = SafeModel.find_by_id(parms[ 'hwid' ])
            if this_safe:
                # Check message is valid
                msg_valid, message = crypto_handler.decrypt(msg=parms['msg'], sig=parms['sig'],
                                                            pkey=this_safe.public_key)
                if msg_valid:
                    # Interpret content and update database
                    # Remember, message may be multiple lines
                    print(f"Message received = {message}")
                    if '\n' in message:
                        message_lines = message.split('\n')
                    else:
                        message_lines = [message, ]
                    status_parts = message_lines[0].split(',')
                    if len(status_parts) == 6:
                        this_safe.last_update = status_parts[2]
                        if status_parts[3] == 'True':
                            this_safe.hinge_closed = True
                        if status_parts[4] == 'True':
                            this_safe.lid_closed = True
                        if status_parts[5] == 'True':
                            this_safe.bolt_engaged = True
                        # Now check if there are any time-based updates to make
                        if this_safe.unlock_time < now:
                            this_safe.auth_to_unlock = True
                        this_safe.save_to_db()
                        if len(message_lines) > 1:
                            # Add entries to Safe events database
                            for i in range(len(message_lines) - 1):
                                if message_lines[i + 1].startswith('EVENT'):
                                    event_parts = message_lines[i + 1].split(',')
                                    if len(event_parts) == 3:
                                        event = SafeEventModel(hardware_id=this_safe.hardware_id,
                                                               event_code=event_codes.get(event_parts[2], DEFAULT_EVENT),
                                                               detail=event_parts[2],
                                                               timestamp=event_parts[1])
                                        event.save_to_db()
                        logging.info(f"Safe parameters updated for {this_safe.hardware_id}")
                        # Now construct a response, encrypt, sign and return it
                        server_message_base = 'Auth_to_unlock:{}:{}\nUnlock_time:{}\nSettings:SCANFREQ={' \
                                              '}:REPORTFREQ={}:PROXIMITYUNIT={}:DISPLAYPROXIMITY={}'
                        if this_safe.auth_to_unlock:
                            auth_msg = 'TRUE'
                        else:
                            auth_msg = 'FALSE'
                        if this_safe.display_proximity:
                            disp_msg = 'TRUE'
                        else:
                            disp_msg = 'FALSE'
                        server_message = server_message_base.format(auth_msg, now, this_safe.unlock_time,
                                                                    this_safe.scan_freq, this_safe.report_freq,
                                                                    this_safe.proximity_unit, disp_msg)
                        msg_enc_64, msg_sig_64 = crypto_handler.encrypt(msg=server_message,
                                                                        safe_pkey=this_safe.public_key)
                        return {"msg": msg_enc_64.decode('utf-8'), "sig": msg_sig_64.decode('utf-8')}, 200
                else:
                    logging.info(f"Invalid checking message received from {parms['hwid']}")
                    return {"error": msgs.SAFE_CHECKIN_ERROR}, 400
            else:
                return {"error": msgs.SAFE_CHECKIN_ERROR}, 400
        logging.info(f"Improperly formed checkin request: {parms}")
        return {"error": msgs.SAFE_CHECKIN_ERROR}, 400
