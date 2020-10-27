from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    jwt_required,
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)

from models.safe import SafeModel
from models.user import UserModel
from schemas.safe import SafeSchema
from schemas.user import UserSchema
from schemas.operations import SafeClaimSchema
import messages.en as msgs


safe_claim_schema = SafeClaimSchema()
user_schema = UserSchema()
safe_schema = SafeSchema()

class ClaimSafe(Resource):
    """
    Endpoints associated with the connection of a safe to a safeholder
    """
    @classmethod
    @jwt_required
    def post(cls):
        """
        Assign current logged on user as safeholder for the specified safe - assuming it is available
        """
        parms = safe_claim_schema.load(request.get_json())
        this_user = UserModel.find_by_id(get_jwt_identity())
        # Check if we have this safe
        requested_safe = SafeModel.find_by_id(parms['hardware_id'])
        if not requested_safe:
            return{"error": msgs.CLAIM_NO_SAFE}, 400
        # Then check if the safe is already claimed
        if requested_safe.safeholder:
            return {"error": msgs.CLAIM_NOT_AVAILABLE}, 400
        # Allocate this user as safeholder
        requested_safe.safeholder = this_user
        requested_safe.save_to_db()
        return {"msg": "ok"}, 200

    @classmethod
    @jwt_required
    def delete(cls):
        """
        Remove the current logged-on user as the holder of this safe - make it available for re-claiming
        """
        parms = safe_claim_schema.load(request.get_json())
        this_user = UserModel.find_by_id(get_jwt_identity())
        # Check if we have this safe
        requested_safe = SafeModel.find_by_id(parms['hardware_id'])
        if not requested_safe:
            return{"error": msgs.CLAIM_NO_SAFE}, 400
        # Next check if the safe is owned by this_user
        if requested_safe.safeholder is None:
            # The safe does not have an owner - cannot delete it
            return {"error": msgs.RELEASE_NOT_OWNED}, 400
        if requested_safe.safeholder.id != this_user.id:
            # The safe does not belong to you
            return {"error": msgs.RELEASE_NOT_OWNED}, 400
        # TODO - Need to also check if the safeholder is in a relationship - should not permit release if so
        # OK, we can remove the safeholder
        requested_safe.safeholder = None
        requested_safe.save_to_db()
        return {"msg": "ok"}, 200
