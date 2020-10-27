# from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models.safe import SafeModel


class SafeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SafeModel
        load_only = ('public_key', )
        include_relationships = True
        load_instance = True

    # hardware_id = fields.Str()
    # username = fields.Str(required=True)
    # password = fields.Str(required=True)
    # email = fields.Str(required=True)
    # displayname = fields.Str(required=True)