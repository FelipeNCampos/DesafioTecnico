from api.database import db
from api.errors import BadRequestError, NotFoundError, ValidationError
from api.models.contagem import Contagem
from api.models.endereco import Endereco
from api.models.produto import Produto
from api.models.user import User
from api.services.helpers import iso_utc, normalize_datetime


def contagem_to_dict(contagem):
    return {
        "id": contagem.id,
        "sku": contagem.produto.codigo,
        "produto": contagem.produto.descricao,
        "codigo_endereco": contagem.endereco.codigo,
        "endereco": contagem.endereco.descricao,
        "quantidade": contagem.quantidade,
        "usuario": contagem.usuario.nome,
        "contado_em": iso_utc(contagem.contado_em),
    }


def _get_produto_by_sku(sku):
    produto = Produto.query.filter_by(codigo=sku.strip().upper()).first()
    if not produto:
        raise NotFoundError("Produto nao encontrado para o SKU informado.")
    return produto


def _get_endereco_by_codigo(codigo):
    endereco = Endereco.query.filter_by(codigo=codigo.strip().upper()).first()
    if not endereco:
        raise NotFoundError("Endereco nao encontrado para o codigo informado.")
    return endereco


def registrar_contagem(data, usuario_id):
    if data["quantidade"] < 0:
        raise ValidationError("Quantidade nao pode ser negativa.")

    usuario = db.session.get(User, usuario_id)
    if not usuario:
        raise NotFoundError("Usuario autenticado nao encontrado.")

    produto = _get_produto_by_sku(data["sku"])
    endereco = _get_endereco_by_codigo(data["codigo_endereco"])

    contagem = Contagem(
        produto_id=produto.id,
        endereco_id=endereco.id,
        quantidade=data["quantidade"],
        usuario_id=usuario.id,
        contado_em=normalize_datetime(data.get("contado_em")),
    )
    db.session.add(contagem)
    db.session.commit()
    return contagem


def saldo_por_endereco(codigo_endereco):
    endereco = _get_endereco_by_codigo(codigo_endereco)
    contagens = (
        Contagem.query.filter_by(endereco_id=endereco.id)
        .join(Produto)
        .order_by(Contagem.produto_id.asc(), Contagem.contado_em.desc(), Contagem.id.desc())
        .all()
    )

    latest_by_produto = {}
    for contagem in contagens:
        if contagem.produto_id not in latest_by_produto:
            latest_by_produto[contagem.produto_id] = contagem

    return {
        "codigo_endereco": endereco.codigo,
        "items": [
            {
                "sku": contagem.produto.codigo,
                "produto": contagem.produto.descricao,
                "codigo_endereco": endereco.codigo,
                "quantidade": contagem.quantidade,
                "contado_em": iso_utc(contagem.contado_em),
            }
            for contagem in latest_by_produto.values()
        ],
    }


def historico_por_sku(sku, params):
    produto = _get_produto_by_sku(sku)
    data_inicio = params.get("data_inicio")
    data_fim = params.get("data_fim")
    if data_inicio and data_fim and data_inicio > data_fim:
        raise BadRequestError("data_inicio nao pode ser maior que data_fim.")

    query = Contagem.query.filter_by(produto_id=produto.id)
    if data_inicio:
        query = query.filter(Contagem.contado_em >= normalize_datetime(data_inicio))
    if data_fim:
        query = query.filter(Contagem.contado_em <= normalize_datetime(data_fim))

    contagens = query.order_by(Contagem.contado_em.asc(), Contagem.id.asc()).all()
    return {
        "sku": produto.codigo,
        "items": [contagem_to_dict(contagem) for contagem in contagens],
    }
