# from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models.safe import SafeModel


class SafeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SafeModel
        load_only = ('public_key', 'displayname')
        include_relationships = True
        load_instance = True
