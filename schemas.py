from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)
    first_name = fields.String()
    last_name = fields.String()
    birthday = fields.String()
    disabled = fields.Bool(default=False)


class UserEditSchema(Schema):
    login = fields.String(required=True)
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    birthday = fields.String()
    disabled = fields.Bool(default=False)


class PermissionsSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    role = fields.String(validate=validate.OneOf(["admin", "readonly"]))


class LoginSchema(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)


class ResponseUsersSchema(Schema):
    id = fields.Integer()
    login = fields.String()
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()


class ResponseUserSchema(Schema):
    id = fields.Integer()
    login = fields.String()
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    birthday = fields.String()
    disabled = fields.Bool()


class ResponseSchema(Schema):
    data = fields.Dict()

