from sqlalchemy.sql import expression

from db import db
from typing import List
#from datetime import datetime


class SafeModel(db.Model):
    __tablename__ = "safe"

    hardware_id = db.Column(db.String(64), primary_key=True)
    digital_key = db.Column(db.String(80), nullable=True)
    bolt_engaged = db.Column(db.Boolean, server_default=expression.false())
    hinge_closed = db.Column(db.Boolean, server_default=expression.false())
    lid_closed = db.Column(db.Boolean, server_default=expression.false())
    safeholder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    last_update = db.Column(db.DateTime(), nullable=False)
    public_key = db.Column(db.Text, nullable=True)
    auth_to_unlock = db.Column(db.Boolean, server_default=expression.false())
    unlock_time = db.Column(db.DateTime(), nullable=False)
    scan_freq = db.Column(db.Integer, server_default='300', nullable=False)
    report_freq = db.Column(db.Integer, server_default='1', nullable=False)
    proximity_unit = db.Column(db.Enum('M', 'H', 'D', 'W', name='_proximity_unit'), nullable=False, server_default="M")
    display_proximity = db.Column(db.Boolean, server_default=expression.true(), nullable=False)

    safeholder = db.relationship("UserModel")


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

    @classmethod
    def find_by_digital_key(cls, digi_key) -> List["SafeModel"]:
        print(f"Find by location called for: {digi_key}")
        return cls.query.filter_by(digital_key=digi_key).all()

    @classmethod
    def find_by_id(cls, _id) -> "SafeModel":
        return cls.query.filter_by(hardware_id=_id).first()

    @classmethod
    def find_all(cls) -> List["SafeModel"]:
        """
        :param
        """
        return cls.query.all()

    @classmethod
    def find_available(cls) -> List["SafeModel"]:
        """
        :param
        """
        return cls.query.filter_by(safeholder_id=None).all()

class SafeEventModel(db.Model):
    __tablename__ = 'safe_event'

    hardware_id = db.Column(db.String(64), db.ForeignKey("safe.hardware_id"), primary_key=True)
    timestamp = db.Column(db.DateTime(), primary_key=True)
    event_code = db.Column(db.Integer, nullable=False)
    detail = db.Column(db.String(40), nullable=False)

    safe = db.relationship("SafeModel")

    def save_to_db(self) -> None:
        """
        :cvar
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls) -> List["SafeEventModel"]:
        """

        :return:
        """
        return cls.query.all()

