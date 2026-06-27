from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, IntegerField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class WebForm(FlaskForm):
    class Meta:
        csrf = False


class ProdutoForm(WebForm):
    codigo = StringField("SKU", validators=[DataRequired(), Length(max=80)])
    descricao = StringField("Descricao", validators=[DataRequired(), Length(max=200)])
    unidade = StringField("Unidade", validators=[DataRequired(), Length(max=20)])


class EnderecoForm(WebForm):
    codigo = StringField("Codigo", validators=[DataRequired(), Length(max=80)])
    descricao = StringField("Descricao", validators=[Optional(), Length(max=200)])


class ContagemForm(WebForm):
    sku = StringField("Produto", validators=[DataRequired(), Length(max=80)])
    codigo_endereco = StringField("Endereco", validators=[DataRequired(), Length(max=80)])
    quantidade = IntegerField("Quantidade", validators=[DataRequired(), NumberRange(min=0)])
    contado_em = DateTimeLocalField("Contado em", validators=[Optional()], format="%Y-%m-%dT%H:%M")
