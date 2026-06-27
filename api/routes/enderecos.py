from flask_smorest import Blueprint

from api.decorators.roles import roles_required
from api.schemas.endereco import (
    EnderecoCreateSchema,
    EnderecoListSchema,
    EnderecoQuerySchema,
    EnderecoSchema,
    EnderecoUpdateSchema,
)
from api.services import endereco_service

blp = Blueprint("enderecos", __name__, url_prefix="/api/enderecos", description="Enderecos")


@blp.route("", methods=["POST"])
@blp.arguments(EnderecoCreateSchema)
@blp.response(201, EnderecoSchema)
@roles_required("gerente", "operador")
def create_endereco(data):
    endereco = endereco_service.create_endereco(data)
    return endereco_service.endereco_to_dict(endereco)


@blp.route("", methods=["GET"])
@blp.arguments(EnderecoQuerySchema, location="query")
@blp.response(200, EnderecoListSchema)
@roles_required("gerente", "operador")
def list_enderecos(params):
    return endereco_service.list_enderecos(params)


@blp.route("/<int:endereco_id>", methods=["GET"])
@blp.response(200, EnderecoSchema)
@roles_required("gerente", "operador")
def get_endereco(endereco_id):
    endereco = endereco_service.get_endereco(endereco_id)
    return endereco_service.endereco_to_dict(endereco)


@blp.route("/codigo/<string:codigo>", methods=["GET"])
@blp.response(200, EnderecoSchema)
@roles_required("gerente", "operador")
def get_endereco_by_codigo(codigo):
    endereco = endereco_service.get_endereco_by_codigo(codigo.upper())
    return endereco_service.endereco_to_dict(endereco)


@blp.route("/<int:endereco_id>", methods=["PUT"])
@blp.arguments(EnderecoUpdateSchema)
@blp.response(200, EnderecoSchema)
@roles_required("gerente")
def update_endereco(data, endereco_id):
    endereco = endereco_service.update_endereco(endereco_id, data)
    return endereco_service.endereco_to_dict(endereco)


@blp.route("/<int:endereco_id>", methods=["DELETE"])
@roles_required("gerente")
def delete_endereco(endereco_id):
    endereco_service.delete_endereco(endereco_id)
    return {"message": "Endereco deletado com sucesso"}
