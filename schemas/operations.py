from marshmallow import Schema, fields


class SafeClaimSchema(Schema):
    # class Meta:
    #     # model = UserModel
    #     load_only = ("password",)
    #     dump_only = ("id",)
    #     load_instance = True

    hardware_id = fields.String(required=True)
