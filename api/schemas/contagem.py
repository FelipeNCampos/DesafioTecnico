import marshmallow as ma


class ContagemCreateSchema(ma.Schema):
    sku = ma.fields.String(required=True)
    codigo_endereco = ma.fields.String(required=True)
    quantidade = ma.fields.Integer(required=True)
    usuario = ma.fields.String(load_default=None, allow_none=True)
    contado_em = ma.fields.DateTime(load_default=None, allow_none=True)


class ContagemSchema(ma.Schema):
    id = ma.fields.Integer()
    sku = ma.fields.String()
    produto = ma.fields.String()
    codigo_endereco = ma.fields.String()
    endereco = ma.fields.String(allow_none=True)
    quantidade = ma.fields.Integer()
    usuario = ma.fields.String()
    contado_em = ma.fields.String()


class HistoricoQuerySchema(ma.Schema):
    data_inicio = ma.fields.DateTime(load_default=None, allow_none=True)
    data_fim = ma.fields.DateTime(load_default=None, allow_none=True)


class SaldoItemSchema(ma.Schema):
    sku = ma.fields.String()
    produto = ma.fields.String()
    codigo_endereco = ma.fields.String()
    quantidade = ma.fields.Integer()
    contado_em = ma.fields.String()


class SaldoSchema(ma.Schema):
    codigo_endereco = ma.fields.String()
    items = ma.fields.List(ma.fields.Nested(SaldoItemSchema))


class HistoricoSchema(ma.Schema):
    sku = ma.fields.String()
    items = ma.fields.List(ma.fields.Nested(ContagemSchema))
