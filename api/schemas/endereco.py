import marshmallow as ma


class EnderecoSchema(ma.Schema):
    id = ma.fields.Integer(dump_only=True)
    codigo = ma.fields.String(required=True)
    descricao = ma.fields.String(allow_none=True)


class EnderecoCreateSchema(ma.Schema):
    codigo = ma.fields.String(required=True)
    descricao = ma.fields.String(load_default=None, allow_none=True)


class EnderecoUpdateSchema(ma.Schema):
    codigo = ma.fields.String()
    descricao = ma.fields.String(allow_none=True)


class EnderecoQuerySchema(ma.Schema):
    page = ma.fields.Integer(load_default=1)
    per_page = ma.fields.Integer(load_default=20)
    q = ma.fields.String(load_default=None, allow_none=True)


class EnderecoListSchema(ma.Schema):
    items = ma.fields.List(ma.fields.Nested(EnderecoSchema))
    page = ma.fields.Integer()
    per_page = ma.fields.Integer()
    total = ma.fields.Integer()
    pages = ma.fields.Integer()
