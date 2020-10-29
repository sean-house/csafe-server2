from db import db
from typing import List


class RelationshipModel(db.Model):
    __tablename__ = "relationship"

    id = db.Column(db.Integer, primary_key=True)
    keyholder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    safeholder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    safeholder = db.relationship("UserModel", backref='safeholder', foreign_keys=[safeholder_id])
    keyholder = db.relationship("UserModel", backref='keyholder', foreign_keys=[keyholder_id])

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
    def find_by_id(cls, _id) -> "RelationshipModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_safeholder_id(cls, _id) -> List["RelationshipModel"]:
        return cls.query.filter_by(safeholder_id=_id).all()

    @classmethod
    def find_by_keyholder_id(cls, _id) -> List["RelationshipModel"]:
        return cls.query.filter_by(keyholder_id=_id).all()

    @classmethod
    def find_all(cls) -> List["RelationshipModel"]:
        """
        :param
        """
        return cls.query.all()

