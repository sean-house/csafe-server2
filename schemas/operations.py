from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class SafeClaimSchema(Schema):
    hardware_id = fields.String(required=True)

class KH_Claim_SHSchema(Schema):
    displayname = fields.String(required=True)
    digital_key = fields.String(required=True)




