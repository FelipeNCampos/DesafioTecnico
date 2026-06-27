from flask_smorest import Blueprint

from api.decorators.roles import roles_required
from api.schemas.produto import (
    ProdutoCreateSchema,
    ProdutoListSchema,
    ProdutoQuerySchema,
    ProdutoSchema,
    ProdutoUpdateSchema,
)
from api.services import produto_service

blp = Blueprint("produtos", __name__, url_prefix="/api/produtos", description="Produtos")


@blp.route("", methods=["POST"])
@blp.arguments(ProdutoCreateSchema)
@blp.response(201, ProdutoSchema)
@roles_required("gerente", "operador")
def create_produto(data):
    produto = produto_service.create_produto(data)
    return produto_service.produto_to_dict(produto)


@blp.route("", methods=["GET"])
@blp.arguments(ProdutoQuerySchema, location="query")
@blp.response(200, ProdutoListSchema)
@roles_required("gerente", "operador")
def list_produtos(params):
    return produto_service.list_produtos(params)


@blp.route("/<int:produto_id>", methods=["GET"])
@blp.response(200, ProdutoSchema)
@roles_required("gerente", "operador")
def get_produto(produto_id):
    produto = produto_service.get_produto(produto_id)
    return produto_service.produto_to_dict(produto)


@blp.route("/sku/<string:codigo>", methods=["GET"])
@blp.response(200, ProdutoSchema)
@roles_required("gerente", "operador")
def get_produto_by_codigo(codigo):
    produto = produto_service.get_produto_by_codigo(codigo.upper())
    return produto_service.produto_to_dict(produto)


@blp.route("/<int:produto_id>", methods=["PUT"])
@blp.arguments(ProdutoUpdateSchema)
@blp.response(200, ProdutoSchema)
@roles_required("gerente")
def update_produto(data, produto_id):
    produto = produto_service.update_produto(produto_id, data)
    return produto_service.produto_to_dict(produto)


@blp.route("/<int:produto_id>", methods=["DELETE"])
@roles_required("gerente")
def delete_produto(produto_id):
    produto_service.delete_produto(produto_id)
    return {"message": "Produto deletado com sucesso"}
