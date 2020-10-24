import traceback
from time import time
import logging

from flask import make_response, render_template
from flask_restful import Resource
from flask_jwt_extended import jwt_required

import messages.en as msgs
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """
        Return confirmation HTML page
        """
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        error_msg = (False, 400)
        headers = {"Content-Type": "text/html"}

        if not confirmation:
            error_msg = msgs.NOT_FOUND, 404
        elif confirmation.confirmed:
            error_msg = msgs.ALREADY_CONFIRMED, 400
        elif confirmation.expired:
            error_msg = msgs.EXPIRED, 400

        if error_msg[ 0 ]:
            return make_response(
                    render_template("confirmation_error_page.html",
                                    error_msg=error_msg[ 0 ]),
                    error_msg[ 1 ],
                    headers,
            )

        else:
            # No errors so we can set the confirmation
            confirmation.confirmed = True
            confirmation.save_to_db()

            logging.debug(f"Returning confirmation page for {confirmation.user.username}")
            return make_response(
                    render_template("confirmation_success_page.html",
                                    username=confirmation.user.username,
                                    email=confirmation.user.email),
                    200,
                    headers,
            )


class ConfirmationByUser(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        """
        Get confirmations for user - use for testing
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": msgs.USER_NONEXISTANT}, 404
        return (
            {
                "current_time": int(time()),
                # we filter the result by expiration time in descending order for convenience
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(cls, user_id: int):
        """
        This endpoint resend the confirmation email with a new confirmation model. It will force the current
        confirmation model to expire so that there is only one valid link at once.
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": msgs.USER_NONEXISTANT.format(user_id)}, 404
        logging.debug(f"Processing confirmation resend for {user.username}")
        try:
            # find the most current confirmation for the user
            confirmation = user.most_recent_confirmation  # using property decorator
            if confirmation:
                if confirmation.confirmed:
                    return {"message": msgs.ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)  # create a new confirmation
            new_confirmation.save_to_db()
            # Does `user` object know the new confirmation by now? Yes.
            # An excellent example where lazy='dynamic' comes into use.
            user.send_confirmation_email()  # re-send the confirmation email
            return {"message": msgs.RESEND_SUCCESSFUL}, 201
        except MailGunException as e:
            logging.error(f"CONFIRMATION: Mailgun error {str(e)}")
            return {"message": str(e)}, 500
        except Exception as e:
            traceback.print_exc()
            return {"message": msgs.RESEND_FAILED}, 500
