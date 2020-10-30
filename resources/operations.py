from uuid import uuid4
from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from datetime import date

from models.safe import SafeModel
from models.user import UserModel
from models.relationship import RelationshipModel
from schemas.safe import SafeSchema
from schemas.user import UserSchema
from schemas.operations import SafeClaimSchema, KH_Claim_SHSchema
import messages.en as msgs


safe_claim_schema = SafeClaimSchema()
kh_claim_sh_schema = KH_Claim_SHSchema()
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
        Generate, save and return a digital key for the Safeholder to pass to their chosen Keyholder
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
        # Allocate this user as safeholder - generate the digital key first
        requested_safe.safeholder = this_user
        digital_key = str(uuid4())
        requested_safe.digital_key = digital_key
        requested_safe.save_to_db()
        return {"digital_key": digital_key}, 200

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


class KHClaimSH(Resource):
    """
    Endpoint associated with a keyholder establishing rleationship with a safeholder
    :param
    """
    @classmethod
    @jwt_required
    def post(cls):
        """
        For a KH to claim a SH they must pass the SH displayname AND a correct digital key for that user's safe
        :param
        """
        parms = kh_claim_sh_schema.load(request.get_json())
        safeholder = UserModel.find_by_displayname(parms['displayname'])
        potential_kh = UserModel.find_by_id(get_jwt_identity())
        # First check if the safeholder exists
        if not safeholder:
            return {"msg": msgs.USER_NONEXISTANT.format(parms['displayname'])}, 400
        # Then check if potential KH is trying to claim themself as a SH
        if safeholder.id == potential_kh.id:
            return {"msg": msgs.KH_EQ_SH}, 401
        # Now check if the safeholder has a safe - and its digital key matches
        safeholder_safes = SafeModel.find_by_safeholder_id(safeholder.id)
        if not safeholder_safes:  # Safeholder has no safes
            return {"msg": msgs.INCORRECT_KEY}, 401
        for safe in safeholder_safes:
            if safe.digital_key == parms['digital_key']:
                # We have a hit - now check if the SH is not already in a relationship for that safe
                relationship_list = RelationshipModel.find_by_safe_id(safe.hardware_id)
                for relationship in relationship_list:
                    if (relationship.safeholder_id == safeholder.id) and (relationship.end_date is None):
                        return {"msg": msgs.SH_IN_RELATIONSHIP}, 401
                # OK now we can set up the relationship
                relationship = RelationshipModel(
                        keyholder_id=potential_kh.id,
                        safeholder_id=safeholder.id,
                        safe_id=safe.hardware_id,
                        start_date=date.today()
                )
                relationship.save_to_db()
                # TODO Add message to relationship message table to confirm relationship established
                return {"msg": msgs.RELATIONSHIP_ESTABLISHED}, 200
        # If we get here the safeholder had no safes that the digital key fitted
        return {"msg": msgs.INCORRECT_KEY}, 401

    @classmethod
    @jwt_required
    def delete(cls):
        """
        Delete a relationship that already exists
        :return:
        """
        parms = kh_claim_sh_schema.load(request.get_json())
        safeholder = UserModel.find_by_displayname(parms['displayname'])
        keyholder = UserModel.find_by_id(get_jwt_identity())
        # First check if the safeholder exists
        if not safeholder:
            return {"msg": msgs.USER_NONEXISTANT.format(parms['displayname'])}, 400
        # Now check if the safeholder has a safe - and its digital key matches
        safeholder_safes = SafeModel.find_by_safeholder_id(safeholder.id)
        if not safeholder_safes:  # Safeholder has no safes
            return {"msg": msgs.INCORRECT_KEY}, 401
        for safe in safeholder_safes:
            if safe.digital_key == parms['digital_key']:
                # We have a hit - now check if the KH is the KH for that relationship
                relationship_list = RelationshipModel.find_by_safe_id(safe.hardware_id)
                for relationship in relationship_list:
                    if (relationship.keyholder_id == keyholder.id) and (relationship.end_date is None):
                        # OK, we have an active relationship between this KH and the SH
                        relationship.end_date = date.today()
                        relationship.save_to_db()
                        # Set a new digital_key for the safe
                        digital_key = str(uuid4())
                        safe.digital_key = digital_key
                        safe.save_to_db()
                        # TODO Send email to SH informing them the KH has released them - and give new digital key
                        return {"msg": msgs.RELATIONSHIP_TERMINATED}, 200
                return {"msg": msgs.INCORRECT_KH}, 401
        return {"msg": msgs.INCORRECT_KEY}, 401
