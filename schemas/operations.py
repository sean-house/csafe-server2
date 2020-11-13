from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class SafeClaimSchema(Schema):
    hardware_id = fields.String(required=True)

class KH_Claim_SHSchema(Schema):
    displayname = fields.String(required=True)
    digital_key = fields.String(required=True)


class SafeOpsSchema(Schema):
    hardware_id = fields.String(required=True)
    auth_to_unlock = fields.Boolean(required=False)
    unlock_time = fields.DateTime()
    scan_freq = fields.Int()
    report_freq = fields.Int()
    proximity_unit = fields.String()
    display_proximity = fields.Boolean()
    bolt_engaged = fields.Boolean(dump_only=True)
    hinge_closed = fields.Boolean(dump_only=True)
    lid_closed = fields.Boolean(dump_only=True)

class SafeSummarySchema(Schema):
    hardware_id = fields.String()
    locked = fields.Boolean()
    safeholder_displayname = fields.String()
    keyholder_displayname = fields.String()



