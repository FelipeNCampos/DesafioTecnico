import marshmallow as ma

class RegisterSchema(ma.Schema):
    nome = ma.fields.String(required=True)
    email = ma.fields.Email(required=True)
    password = ma.fields.String(required=True, load_only=True)
    perfil = ma.fields.String(load_default="operador")

class LoginSchema(ma.Schema):
    email = ma.fields.Email(required=True)
    password = ma.fields.String(required=True, load_only=True)

class TokenSchema(ma.Schema):
    access_token = ma.fields.String()
    token_type = ma.fields.String()
    user = ma.fields.Dict()
