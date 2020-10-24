from marshmallow import Schema, fields


class UserSchema(Schema):
    class Meta:
        # model = UserModel
        load_only = ("password",)
        dump_only = ("id",)
        load_instance = True

    id = fields.Integer()
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Str(required=True)
    displayname = fields.Str(required=True)
