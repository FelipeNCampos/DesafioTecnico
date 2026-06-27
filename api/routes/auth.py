from flask import request
from flask_smorest import Blueprint

from api.errors import BadRequestError
from api.schemas.auth import LoginSchema, RegisterSchema, TokenSchema
from api.services import auth_service

blp = Blueprint("auth", "auth", url_prefix="/auth", description="Autenticacao")


@blp.route("/register", methods=["POST"])
@blp.arguments(RegisterSchema)
@blp.response(201, TokenSchema)
@blp.doc(security=[])
def register(data):
    user = auth_service.register_user(data)
    return auth_service.token_payload(user)


@blp.route("/login", methods=["POST"])
@blp.arguments(LoginSchema)
@blp.response(200, TokenSchema)
@blp.doc(security=[])
def login(data):
    user = auth_service.authenticate(data["email"], data["password"])
    if not user:
        raise BadRequestError("Credenciais invalidas.", status_code=401, error="invalid_credentials")
    return auth_service.token_payload(user)


@blp.route("/token", methods=["POST"])
@blp.response(200, TokenSchema)
@blp.doc(
    security=[],
    requestBody={
        "required": True,
        "content": {
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "format": "email"},
                        "password": {"type": "string"},
                        "grant_type": {"type": "string", "default": "password"},
                    },
                    "required": ["username", "password"],
                }
            }
        },
    },
)
def token():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        raise BadRequestError("username e password sao obrigatorios.")

    user = auth_service.authenticate(username, password)
    if not user:
        raise BadRequestError("Credenciais invalidas.", status_code=401, error="invalid_credentials")
    return auth_service.token_payload(user, include_user=False)
