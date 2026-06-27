from sqlalchemy.exc import IntegrityError

from api.database import db
from api.errors import ConflictError, NotFoundError
from api.models.endereco import Endereco
from api.services.helpers import clamp_pagination


def endereco_to_dict(endereco):
    return {
        "id": endereco.id,
        "codigo": endereco.codigo,
        "descricao": endereco.descricao,
    }


def list_enderecos(params):
    page, per_page = clamp_pagination(params.get("page"), params.get("per_page"))
    query = Endereco.query.order_by(Endereco.codigo.asc())
    q = params.get("q")
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter((Endereco.codigo.ilike(pattern)) | (Endereco.descricao.ilike(pattern)))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [endereco_to_dict(item) for item in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


def get_endereco(endereco_id):
    endereco = db.session.get(Endereco, endereco_id)
    if not endereco:
        raise NotFoundError("Endereco nao encontrado.")
    return endereco


def get_endereco_by_codigo(codigo):
    endereco = Endereco.query.filter_by(codigo=codigo).first()
    if not endereco:
        raise NotFoundError("Endereco nao encontrado.")
    return endereco


def create_endereco(data):
    codigo = data["codigo"].strip().upper()
    if Endereco.query.filter_by(codigo=codigo).first():
        raise ConflictError("Codigo de endereco ja cadastrado.")

    endereco = Endereco(
        codigo=codigo,
        descricao=(data.get("descricao") or "").strip() or None,
    )
    db.session.add(endereco)
    db.session.commit()
    return endereco


def update_endereco(endereco_id, data):
    endereco = get_endereco(endereco_id)
    if "codigo" in data:
        codigo = data["codigo"].strip().upper()
        exists = Endereco.query.filter(Endereco.codigo == codigo, Endereco.id != endereco.id).first()
        if exists:
            raise ConflictError("Codigo de endereco ja cadastrado.")
        endereco.codigo = codigo
    if "descricao" in data:
        endereco.descricao = (data.get("descricao") or "").strip() or None
    db.session.commit()
    return endereco


def delete_endereco(endereco_id):
    endereco = get_endereco(endereco_id)
    try:
        db.session.delete(endereco)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError("Endereco possui contagens vinculadas e nao pode ser removido.") from exc
