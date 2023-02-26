from requests import Response
from flask import request, url_for
from db import db
from typing import List, Union

from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel
import messages.en as msgs


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    pw_salt = db.Column(db.LargeBinary(80), nullable=False)
    pw_hash = db.Column(db.LargeBinary(100), nullable=False)
    displayname = db.Column(db.String(100), nullable=False, unique=True)
    confirmation = db.relationship(
            "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        # ordered by expiration time (in descending order)
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def save_to_db(self) -> None:
        """
        Save the User record to the database
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """
        Delete the user record from the database
        """
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Union[Response, None]:
        """
        Send an address confirmation email to the user
        """
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        return Mailgun.send_email(from_email=msgs.FROM_EMAIL,
                                  from_title=msgs.FROM_TITLE,
                                  to_email=[self.email],
                                  subject=msgs.CONFIRMATION_MAIL_SUBJECT,
                                  text=msgs.CONFIRMATION_MAIL_BODY.format(name=self.username, link=link),
                                  html=msgs.CONFIRMATION_MAIL_BODY_HTML.format(name=self.username, link=link)
                                  )

    @classmethod
    def find_all(cls) -> List['UserModel']:
        """
        :param
        """
        return cls.query.all()

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> 'UserModel':
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_displayname(cls, displayname: str) -> 'UserModel':
        return cls.query.filter_by(displayname=displayname).first()
