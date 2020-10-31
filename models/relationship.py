from requests import Response
from typing import List, Union

from db import db
from models.user import UserModel
import messages.en as msgs
from libs.mailgun import Mailgun


class RelationshipModel(db.Model):
    __tablename__ = "relationship"

    id = db.Column(db.Integer, primary_key=True)
    keyholder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    safeholder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    safe_id = db.Column(db.String(64), db.ForeignKey("safe.hardware_id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    safeholder = db.relationship("UserModel", backref='safeholder', foreign_keys=[safeholder_id])
    keyholder = db.relationship("UserModel", backref='keyholder', foreign_keys=[keyholder_id])
    safe = db.relationship("SafeModel", backref='safe', foreign_keys=[safe_id])

    def save_to_db(self) -> None:
        """
        :cvar
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """
        :param
        """
        db.session.delete(self)
        db.session.commit()

    def send_relationship_email(self, status: str) -> Union[Response, None]:
        """
        Send an email to the Safeholder on start of stop of a new relationship.
        status='start' for a new relationship, 'end' for a termination
        """
        if status == 'start':
            return Mailgun.send_email(from_email=msgs.FROM_EMAIL,
                                      from_title=msgs.FROM_TITLE,
                                      to_email=[self.safeholder.email],
                                      subject=msgs.RELATIONSHIP_MAIL_SUBJECT,
                                      text=msgs.RELATIONSHIP_START_MAIL_BODY.format(name=self.safeholder.username,
                                                                            kh_displayname=self.keyholder.displayname),
                                      html=msgs.RELATIONSHIP_START_MAIL_BODY_HTML.format(name=self.safeholder.username,
                                                                            kh_displayname=self.keyholder.displayname)
                                      )
        if status == 'end':
            return Mailgun.send_email(from_email=msgs.FROM_EMAIL,
                                      from_title=msgs.FROM_TITLE,
                                      to_email=[self.safeholder.email],
                                      subject=msgs.RELATIONSHIP_MAIL_SUBJECT,
                                      text=msgs.RELATIONSHIP_END_MAIL_BODY.format(name=self.safeholder.username,
                                                                            kh_displayname=self.keyholder.displayname,
                                                                            digital_key=self.safe.digital_key),
                                      html=msgs.RELATIONSHIP_END_MAIL_BODY_HTML.format(name=self.safeholder.username,
                                                                            kh_displayname=self.keyholder.displayname,
                                                                            digital_key=self.safe.digital_key)
                                      )

    @classmethod
    def find_by_id(cls, _id) -> "RelationshipModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_safeholder_id(cls, _id) -> List["RelationshipModel"]:
        return cls.query.filter_by(safeholder_id=_id).all()

    @classmethod
    def find_by_keyholder_id(cls, _id) -> List["RelationshipModel"]:
        return cls.query.filter_by(keyholder_id=_id).all()

    @classmethod
    def find_by_safe_id(cls, _safe_id) -> List["RelationshipModel"]:
        return cls.query.filter_by(safe_id=_safe_id).all()

    @classmethod
    def find_all(cls) -> List["RelationshipModel"]:
        """
        :param
        """
        return cls.query.all()

