# api/decorators/roles.py
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from api.errors import ForbiddenError

def roles_required(*allowed_roles):
    """
    Ex: @roles_required("gerente") ou @roles_required("gerente", "operador")
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            perfil = claims.get("perfil")
            if perfil not in allowed_roles:
                raise ForbiddenError(
                    "Acesso restrito",
                    details={"required_roles": allowed_roles, "perfil": perfil},
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
