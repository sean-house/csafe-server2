from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import jwt_required

from models.relationship import RelationshipModel
from schemas.relationship import RelationshipSchema
import messages.en as msgs

relationship_schema = RelationshipSchema()

class GetRelationStatus(Resource):
    """
    Method associated with the Relationship Model
    """

    @classmethod
    # @jwt_required
    def get(cls):
        return {"relationships": [relationship_schema.dump(relation) for relation in RelationshipModel.find_all()]}


