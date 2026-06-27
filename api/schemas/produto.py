import marshmallow as ma

class ProdutoSchema(ma.Schema):
    id = ma.fields.Integer(dump_only=True)
    codigo = ma.fields.String(required=True)
    descricao = ma.fields.String(required=True)
    unidade = ma.fields.String(required=True)


class ProdutoCreateSchema(ma.Schema):
    codigo = ma.fields.String(required=True)
    descricao = ma.fields.String(required=True)
    unidade = ma.fields.String(required=True)


class ProdutoUpdateSchema(ma.Schema):
    codigo = ma.fields.String()
    descricao = ma.fields.String()
    unidade = ma.fields.String()


class ProdutoQuerySchema(ma.Schema):
    page = ma.fields.Integer(load_default=1)
    per_page = ma.fields.Integer(load_default=20)
    q = ma.fields.String(load_default=None, allow_none=True)


class ProdutoListSchema(ma.Schema):
    items = ma.fields.List(ma.fields.Nested(ProdutoSchema))
    page = ma.fields.Integer()
    per_page = ma.fields.Integer()
    total = ma.fields.Integer()
    pages = ma.fields.Integer()


CreateProduct = ProdutoCreateSchema
UpdateProduct = ProdutoUpdateSchema
