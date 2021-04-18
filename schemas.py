from marshmallow import Schema, fields, validate


class User(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)
    first_name = fields.String()
    last_name = fields.String()
    birthday = fields.String()
    disabled = fields.Bool(default=False)


class Permissions(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    role = fields.String(validate=validate.OneOf(["admin", "readonly"]))


class Login(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)
