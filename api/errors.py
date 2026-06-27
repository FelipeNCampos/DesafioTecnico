from http import HTTPStatus

from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 400
    error = "bad_request"

    def __init__(self, message, status_code=None, error=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.error = error or self.error
        self.details = details


class BadRequestError(ApiError):
    status_code = 400
    error = "bad_request"


class NotFoundError(ApiError):
    status_code = 404
    error = "not_found"


class ConflictError(ApiError):
    status_code = 409
    error = "conflict"


class ValidationError(ApiError):
    status_code = 422
    error = "validation_error"


class ForbiddenError(ApiError):
    status_code = 403
    error = "forbidden"


def error_response(message, status_code, error=None, details=None):
    payload = {
        "error": error or HTTPStatus(status_code).phrase.lower().replace(" ", "_"),
        "message": message,
    }
    if details:
        payload["details"] = details
    return jsonify(payload), status_code


def register_error_handlers(app, jwt):
    @app.errorhandler(ApiError)
    def handle_api_error(exc):
        return error_response(exc.message, exc.status_code, exc.error, exc.details)

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(exc):
        return error_response("Dados de entrada invalidos", 422, "validation_error", exc.messages)

    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return error_response(exc.description, exc.code, exc.name.lower().replace(" ", "_"))

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        app.logger.exception("Erro inesperado", exc_info=exc)
        return error_response("Erro interno do servidor", 500, "internal_server_error")

    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return error_response("Token JWT ausente ou invalido", 401, "missing_token", {"reason": reason})

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return error_response("Token JWT invalido", 422, "invalid_token", {"reason": reason})

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return error_response("Token JWT expirado", 401, "token_expired")
