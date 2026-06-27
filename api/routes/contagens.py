from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint

from api.decorators.roles import roles_required
from api.schemas.contagem import (
    ContagemCreateSchema,
    ContagemSchema,
    HistoricoQuerySchema,
    HistoricoSchema,
    SaldoSchema,
)
from api.services import contagem_service

blp = Blueprint("contagens", __name__, url_prefix="/api/contagens", description="Contagens")


@blp.route("", methods=["POST"])
@blp.arguments(ContagemCreateSchema)
@blp.response(201, ContagemSchema)
@roles_required("gerente", "operador")
def registrar_contagem(data):
    contagem = contagem_service.registrar_contagem(data, int(get_jwt_identity()))
    return contagem_service.contagem_to_dict(contagem)


@blp.route("/saldo/<string:codigo_endereco>", methods=["GET"])
@blp.response(200, SaldoSchema)
@roles_required("gerente", "operador")
def saldo_por_endereco(codigo_endereco):
    return contagem_service.saldo_por_endereco(codigo_endereco)


@blp.route("/historico/<string:sku>", methods=["GET"])
@blp.arguments(HistoricoQuerySchema, location="query")
@blp.response(200, HistoricoSchema)
@roles_required("gerente", "operador")
def historico_por_sku(params, sku):
    return contagem_service.historico_por_sku(sku, params)
