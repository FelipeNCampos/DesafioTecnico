from api.database import db
from api.errors import ConflictError, ValidationError
from api.models.user import User
from api.decorators.roles import roles_required

VALID_PROFILES = ("gerente", "operador")


def user_to_dict(user):
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "perfil": user.perfil,
    }


def register_user(data):
    perfil = data.get("perfil", "operador")
    if perfil not in VALID_PROFILES:
        raise ValidationError("Perfil invalido. Use 'gerente' ou 'operador'.")

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        raise ConflictError("Email ja cadastrado.")
    
    if data.get("perfil") == "gerente":
        if not roles_required("gerente"):
            raise ValidationError("Nao e permitido registrar um gerente via API. Solicite cadastro por um administrador.")

    user = User(
        nome=data["nome"].strip(),
        email=email,
        password=User.hash_password(data["password"]),
        perfil=perfil,
    )
    db.session.add(user)
    db.session.commit()
    return user

@roles_required("gerente")
def register_gerente(data):
    data["perfil"] = "gerente"
    return register_user(data)

def authenticate(email, password):
    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not user.verify_password(password):
        return None
    return user


def token_payload(user, include_user=True):
    payload = {
        "access_token": user.create_access_token(),
        "token_type": "Bearer",
    }
    if include_user:
        payload["user"] = user_to_dict(user)
    return payload
