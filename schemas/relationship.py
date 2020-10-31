from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import Schema, fields

from models.relationship import RelationshipModel, RelationshipMessageModel


class RelationshipSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RelationshipModel
        include_relationships = True
        load_instance = True


class RelationshipMessageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RelationshipMessageModel
        dump_only = ('originator_id', 'message_timestamp', 'seen_by_kh', 'seen_by_sh')
        include_relationships = True
        load_instance = False


class MessageGetSchema(Schema):
    type = fields.String(required=True)
    relationship_id = fields.Int(required=True)


class MessagePostSchema(Schema):
    relationship_id = fields.Int(required=True)
    message = fields.String(required=True)

