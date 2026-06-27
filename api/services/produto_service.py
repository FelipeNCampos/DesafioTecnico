from sqlalchemy.exc import IntegrityError

from api.database import db
from api.errors import ConflictError, NotFoundError
from api.models.produto import Produto
from api.services.helpers import clamp_pagination


def produto_to_dict(produto):
    return {
        "id": produto.id,
        "codigo": produto.codigo,
        "descricao": produto.descricao,
        "unidade": produto.unidade,
    }


def list_produtos(params):
    page, per_page = clamp_pagination(params.get("page"), params.get("per_page"))
    query = Produto.query.order_by(Produto.codigo.asc())
    q = params.get("q")
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter((Produto.codigo.ilike(pattern)) | (Produto.descricao.ilike(pattern)))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [produto_to_dict(item) for item in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


def get_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        raise NotFoundError("Produto nao encontrado.")
    return produto


def get_produto_by_codigo(codigo):
    produto = Produto.query.filter_by(codigo=codigo).first()
    if not produto:
        raise NotFoundError("Produto nao encontrado.")
    return produto


def create_produto(data):
    codigo = data["codigo"].strip().upper()
    if Produto.query.filter_by(codigo=codigo).first():
        raise ConflictError("SKU ja cadastrado.")

    produto = Produto(
        codigo=codigo,
        descricao=data["descricao"].strip(),
        unidade=data["unidade"].strip().upper(),
    )
    db.session.add(produto)
    db.session.commit()
    return produto


def update_produto(produto_id, data):
    produto = get_produto(produto_id)
    if "codigo" in data:
        codigo = data["codigo"].strip().upper()
        exists = Produto.query.filter(Produto.codigo == codigo, Produto.id != produto.id).first()
        if exists:
            raise ConflictError("SKU ja cadastrado.")
        produto.codigo = codigo
    if "descricao" in data:
        produto.descricao = data["descricao"].strip()
    if "unidade" in data:
        produto.unidade = data["unidade"].strip().upper()
    db.session.commit()
    return produto


def delete_produto(produto_id):
    produto = get_produto(produto_id)
    try:
        db.session.delete(produto)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError("Produto possui contagens vinculadas e nao pode ser removido.") from exc
