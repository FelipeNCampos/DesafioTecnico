from flask_smorest import Blueprint

from api.decorators.roles import roles_required
from api.schemas.relatorio import DivergenciaSchema
from api.services import relatorios_service

blp = Blueprint("relatorios", __name__, url_prefix="/api/relatorios", description="Relatorios")


@blp.route("/divergencia/<string:codigo_endereco>", methods=["GET"])
@blp.response(200, DivergenciaSchema)
@roles_required("gerente")
def divergencia_por_endereco(codigo_endereco):
    return relatorios_service.divergencia_por_endereco(codigo_endereco)
