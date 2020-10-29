from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models.relationship import RelationshipModel


class RelationshipSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RelationshipModel
        include_relationships = True
        load_instance = True

