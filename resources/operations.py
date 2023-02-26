from uuid import uuid4
import logging
from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from sqlalchemy.sql import expression
from datetime import date, datetime, timezone

from models.safe import SafeModel
from models.user import UserModel
from models.relationship import RelationshipModel, RelationshipMessageModel
from schemas.safe import SafeSchema
from schemas.user import UserSchema
from schemas.operations import SafeClaimSchema, KH_Claim_SHSchema, SafeOpsSchema, SafeSummarySchema
from schemas.relationship import RelationshipMessageSchema, MessageGetSchema, MessagePostSchema
import messages.en as msgs

# Set up the schema objects
safe_claim_schema = SafeClaimSchema()
kh_claim_sh_schema = KH_Claim_SHSchema()
user_schema = UserSchema()
safe_schema = SafeSchema()
message_get_schema = MessageGetSchema()
message_post_schema = MessagePostSchema()
relationship_message_schema = RelationshipMessageSchema()
safe_ops_schema = SafeOpsSchema()
safe_summary_schema = SafeSummarySchema()


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
            return {"error": msgs.CLAIM_NO_SAFE}, 400
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
            return {"error": msgs.CLAIM_NO_SAFE}, 400
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
                # Send email to Safeholder to confirm start of relationship
                relationship.send_relationship_email(status='start')
                # Log the start of the relationship
                logging.info(f"RELATIONSHIP: START {relationship.keyholder.username} - "
                             f"{relationship.safeholder.username}")
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
        now = datetime.now(timezone.utc)
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
                        # Set a new digital_key for the safe - and unlock it (for safety)
                        digital_key = str(uuid4())
                        safe.digital_key = digital_key
                        safe.auth_to_unlock = expression.true()
                        safe.unlock_time = now
                        safe.last_update = now
                        safe.save_to_db()
                        # Then terminate the relationship - and send a mail to the safeholder
                        relationship.end_date = date.today()
                        relationship.send_relationship_email(status='end')
                        relationship.save_to_db()
                        # Log the end of the relationship
                        logging.info(f"RELATIONSHIP: END {relationship.keyholder.username} - "
                                     f"{relationship.safeholder.username}")

                        return {"msg": msgs.RELATIONSHIP_TERMINATED}, 200
                return {"msg": msgs.INCORRECT_KH}, 401
        return {"msg": msgs.INCORRECT_KEY}, 401


class Message(Resource):
    """
    Endpoints associated with setting and getting relationship messages
    :parameter
    """
    @classmethod
    @jwt_required
    def get(cls):
        """
        Request argument type may be 'all', 'unread',  argument relationship = unique ID for the relationship
        :parameter
        """
        parms = message_get_schema.load(request.args)

        if parms['type'] == 'unread':
            return {
                       "messages": [relationship_message_schema.dump(message) for message in
                                    RelationshipMessageModel.find_unread_by_relationship(
                                        _relationship_id=parms['relationship_id'])]
                   }, 200
        elif parms['type'] == 'all':
            return {
                       "messages": [relationship_message_schema.dump(message) for message in
                                    RelationshipMessageModel.find_all(
                                        _relationship_id=parms['relationship_id'])]
                   }, 200
        else:
            return{"error": msgs.BAD_REQUEST}, 400

    @classmethod
    @jwt_required
    def post(cls):
        """
        :parameter
        """
        parms = message_post_schema.load(request.get_json())
        this_user_id = get_jwt_identity()
        requested_relationship = RelationshipModel.find_by_id(_id=parms['relationship_id'])
        if requested_relationship:
            now = datetime.now(timezone.utc)
            # Check the role of this user
            seen_by_sh = None
            seen_by_kh = None
            if this_user_id == requested_relationship.safeholder_id:
                seen_by_sh = now
            elif this_user_id == requested_relationship.keyholder_id:
                seen_by_kh = now
            else:
                return {"msg": msgs.NOT_AUTHORISED}, 400
            # Check the relationship is not terminated
            if requested_relationship.end_date is not None:
                return {"msg": msgs.RELATIONSHIP_TERMINATED}, 400
            # OK, so now create the message
            message = RelationshipMessageModel(
                    relationship_id=parms['relationship_id'],
                    originator_id=this_user_id,
                    message=parms['message'],
                    message_timestamp=now,
                    seen_by_kh=seen_by_kh,
                    seen_by_sh=seen_by_sh
                    )
            message.save_to_db()
            return {"msg": "OK"}, 200
        # No relationship exists
        return {"error": msgs.NOT_AUTHORISED}, 400


class SafeOps(Resource):
    """
    Endpoints associated with getting and setting safe parameters
    :parameter
    """
    @classmethod
    @jwt_required
    def get(cls):
        """
        Get safe parameters when hardware_id is specified as request args and this_user is a keyholder
        covering the requested safe
        :parameter
        """
        parms = safe_ops_schema.load(request.args)
        this_user_id = get_jwt_identity()
        relationship_list = RelationshipModel.find_by_keyholder_id(this_user_id)
        for relationship in relationship_list:
            if relationship.safe_id == parms['hardware_id']:
                requested_safe = relationship.safe
                return {"safe": safe_ops_schema.dump(requested_safe)}, 200
        # The user is not a KH for that safe so retrun an error
        else:
            return {"error": msgs.INCORRECT_KH}, 400

    @classmethod
    @jwt_required
    def post(cls):
        """
        Update safe parameters.  Include JSON object containing the parameters to be updated.
        "hardware_id" is mandatory.
        other fields are optional.  Fields not specified will not be changed.
        :parameter
        """
        parms = safe_ops_schema.load(request.get_json())
        now = datetime.now(timezone.utc)
        this_user_id = get_jwt_identity()
        relationship_list = RelationshipModel.find_by_keyholder_id(this_user_id)
        for relationship in relationship_list:
            if relationship.safe_id == parms['hardware_id']:
                # Delete hardware_id from parms since we do not want to use to update the model object
                parms.pop('hardware_id', None)
                # Then update the safe object with the remaining values
                for key, value in parms.items():
                    print(key, value)
                    setattr(relationship.safe, key, value)
                # The set the last_updated field
                relationship.safe.last_update = now
                relationship.safe.save_to_db()
                return {"safe": safe_ops_schema.dump(relationship.safe)}, 200
        # The user is not a KH for that safe so retrun an error
        return {"error": msgs.INCORRECT_KH}, 400


class SafeSummary(Resource):
    """
    GET method only with no parameters to request summary of the logged on user's relationships; the safe, its status
    the keyholder and safeholder displaynames
    :parameter
    """
    @classmethod
    @jwt_required
    def get(cls):
        """
        :parameter
        """
        this_user_id = get_jwt_identity()
        this_user = UserModel.find_by_id(this_user_id)
        relationship_list = RelationshipModel.find_any(this_user_id)
        safe_list = SafeModel.find_by_safeholder_id(this_user_id)
        summary_list = []
        safe_ids = []
        # First scan the safes in relationships
        for relationship in relationship_list:
            safe_ids.append(relationship.safe.hardware_id)
            summary_item = {'hardware_id': relationship.safe.hardware_id,
                            'locked': all([relationship.safe.hinge_closed,
                                          relationship.safe.lid_closed,
                                          relationship.safe.bolt_engaged]),
                            'safeholder_displayname': relationship.safeholder.displayname,
                            'keyholder_displayname': relationship.keyholder.displayname}
            summary_list.append(summary_item)
        # then scan the safes not not in relationships
        for safe in safe_list:
            if safe.hardware_id not in safe_ids:
                summary_item = {
                    'hardware_id': safe.hardware_id,
                    'locked': all([safe.hinge_closed,
                                   safe.lid_closed,
                                   safe.bolt_engaged]),
                    'safeholder_displayname': this_user.displayname,
                    'keyholder_displayname': None
                }
                summary_list.append(summary_item)
        return {"safe_list": [safe_summary_schema.dump(item) for item in summary_list]}, 200