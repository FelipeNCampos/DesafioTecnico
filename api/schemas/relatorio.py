import marshmallow as ma


class DivergenciaItemSchema(ma.Schema):
    sku = ma.fields.String()
    produto = ma.fields.String()
    quantidade_atual = ma.fields.Integer(allow_none=True)
    quantidade_anterior = ma.fields.Integer(allow_none=True)
    diferenca = ma.fields.Integer(allow_none=True)
    status = ma.fields.String()
    contado_em_atual = ma.fields.String(allow_none=True)
    contado_em_anterior = ma.fields.String(allow_none=True)


class DivergenciaSchema(ma.Schema):
    codigo_endereco = ma.fields.String()
    items = ma.fields.List(ma.fields.Nested(DivergenciaItemSchema))
