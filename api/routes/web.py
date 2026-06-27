from flask import Blueprint, render_template

from api.forms import ContagemForm, EnderecoForm, ProdutoForm


bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    return render_template(
        "index.html",
        app_name="Estoque X",
        produto_form=ProdutoForm(),
        endereco_form=EnderecoForm(),
        contagem_form=ContagemForm(),
    )
