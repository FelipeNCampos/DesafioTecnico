from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from api.forms import ContagemForm, EnderecoForm, LoginForm, ProdutoForm


bp = Blueprint("web", __name__)


def _headers():
    token = session.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _api_request(method, path, *, json=None, query_string=None):
    client = current_app.test_client()
    response = client.open(
        path,
        method=method.upper(),
        json=json,
        query_string=query_string,
        headers=_headers(),
    )
    payload = response.get_json(silent=True) or {}
    return response.status_code, payload


def _message(payload, fallback):
    return payload.get("message") or payload.get("error") or fallback


def _login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("access_token"):
            flash("Entre para acessar o painel web.", "warning")
            return redirect(url_for("web.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped


def _clear_session_on_auth_error(status_code):
    if status_code in (401, 422):
        session.clear()
        flash("Sessao expirada. Entre novamente.", "warning")
        return True
    return False


def _fetch_list(path, q=None, page=1, per_page=20):
    params = {"page": page, "per_page": per_page}
    if q:
        params["q"] = q
    status, payload = _api_request("GET", path, query_string=params)
    if _clear_session_on_auth_error(status):
        return status, {}
    if status >= 400:
        flash(_message(payload, "Nao foi possivel carregar os dados."), "danger")
        return status, {"items": [], "page": page, "pages": 1, "total": 0}
    return status, payload


def _options():
    _, produtos = _fetch_list("/api/produtos", per_page=100)
    _, enderecos = _fetch_list("/api/enderecos", per_page=100)
    return produtos.get("items", []), enderecos.get("items", [])


@bp.route("/")
def index():
    if session.get("access_token"):
        return redirect(url_for("web.produtos_list"))
    return redirect(url_for("web.login"))


@bp.route("/web")
def dashboard():
    return redirect(url_for("web.produtos_list"))


@bp.route("/web/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        status, payload = _api_request(
            "POST",
            "/auth/login",
            json={"email": form.email.data, "password": form.password.data},
        )
        if status == 200:
            session["access_token"] = payload["access_token"]
            session["token_type"] = payload.get("token_type", "Bearer")
            session["user"] = payload.get("user", {})
            flash("Login realizado com sucesso.", "success")
            return redirect(request.args.get("next") or url_for("web.produtos_list"))
        flash(_message(payload, "Credenciais invalidas."), "danger")
    return render_template("login.html", form=form)


@bp.route("/web/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Voce saiu do painel.", "info")
    return redirect(url_for("web.login"))


@bp.route("/web/produtos")
@_login_required
def produtos_list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    status, payload = _fetch_list("/api/produtos", q=q, page=page)
    if _clear_session_on_auth_error(status):
        return redirect(url_for("web.login"))
    return render_template("produtos_list.html", produtos=payload, q=q, active_page="produtos")


@bp.route("/web/produtos/novo", methods=["GET", "POST"])
@_login_required
def produtos_novo():
    form = ProdutoForm()
    if form.validate_on_submit():
        status, payload = _api_request(
            "POST",
            "/api/produtos",
            json={
                "codigo": form.codigo.data,
                "descricao": form.descricao.data,
                "unidade": form.unidade.data,
            },
        )
        if status == 201:
            flash("Produto cadastrado com sucesso.", "success")
            return redirect(url_for("web.produtos_list"))
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        flash(_message(payload, "Nao foi possivel cadastrar o produto."), "danger")
    return render_template("produtos_form.html", form=form, title="Novo produto", active_page="produtos")


@bp.route("/web/produtos/<int:produto_id>/editar", methods=["GET", "POST", "DELETE"])
@_login_required
def produtos_editar(produto_id):
    form = ProdutoForm()
    if request.method == "GET":
        status, produto = _api_request("GET", f"/api/produtos/{produto_id}")
        if status == 200:
            form.codigo.data = produto.get("codigo")
            form.descricao.data = produto.get("descricao")
            form.unidade.data = produto.get("unidade")
        else:
            if _clear_session_on_auth_error(status):
                return redirect(url_for("web.login"))
            flash(_message(produto, "Produto nao encontrado."), "danger")
            return redirect(url_for("web.produtos_list"))

    if form.validate_on_submit():
        status, payload = _api_request(
            "PUT",
            f"/api/produtos/{produto_id}",
            json={
                "codigo": form.codigo.data,
                "descricao": form.descricao.data,
                "unidade": form.unidade.data,
            },
        )
        if status == 200:
            flash("Produto atualizado com sucesso.", "success")
            return redirect(url_for("web.produtos_list"))
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        flash(_message(payload, "Nao foi possivel atualizar o produto."), "danger")
    return render_template("produtos_form.html", form=form, title="Editar produto", produto_id=produto_id, active_page="produtos")

@bp.route("/web/produtos/<int:produto_id>/deletar", methods=["POST"])
@_login_required
def produtos_deletar(produto_id):
    status, payload = _api_request("DELETE", f"/api/produtos/{produto_id}")

    if _clear_session_on_auth_error(status):
        return redirect(url_for("web.login"))

    if status in (200, 204):
        flash("Produto deletado com sucesso.", "success")
    else:
        flash(_message(payload, "Nao foi possivel deletar o produto."), "danger")

    return redirect(url_for("web.produtos_list"))

@bp.route("/web/enderecos")
@_login_required
def enderecos_list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    status, payload = _fetch_list("/api/enderecos", q=q, page=page)
    if _clear_session_on_auth_error(status):
        return redirect(url_for("web.login"))
    return render_template("enderecos_list.html", enderecos=payload, q=q, active_page="enderecos")


@bp.route("/web/enderecos/novo", methods=["GET", "POST"])
@_login_required
def enderecos_novo():
    form = EnderecoForm()
    if form.validate_on_submit():
        status, payload = _api_request(
            "POST",
            "/api/enderecos",
            json={"codigo": form.codigo.data, "descricao": form.descricao.data or None},
        )
        if status == 201:
            flash("Endereco cadastrado com sucesso.", "success")
            return redirect(url_for("web.enderecos_list"))
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        flash(_message(payload, "Nao foi possivel cadastrar o endereco."), "danger")
    return render_template("enderecos_form.html", form=form, title="Novo endereco", active_page="enderecos")


@bp.route("/web/enderecos/<int:endereco_id>/editar", methods=["GET", "POST"])
@_login_required
def enderecos_editar(endereco_id):
    form = EnderecoForm()
    if request.method == "GET":
        status, endereco = _api_request("GET", f"/api/enderecos/{endereco_id}")
        if status == 200:
            form.codigo.data = endereco.get("codigo")
            form.descricao.data = endereco.get("descricao")
        else:
            if _clear_session_on_auth_error(status):
                return redirect(url_for("web.login"))
            flash(_message(endereco, "Endereco nao encontrado."), "danger")
            return redirect(url_for("web.enderecos_list"))

    if form.validate_on_submit():
        status, payload = _api_request(
            "PUT",
            f"/api/enderecos/{endereco_id}",
            json={"codigo": form.codigo.data, "descricao": form.descricao.data or None},
        )
        if status == 200:
            flash("Endereco atualizado com sucesso.", "success")
            return redirect(url_for("web.enderecos_list"))
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        flash(_message(payload, "Nao foi possivel atualizar o endereco."), "danger")
    return render_template("enderecos_form.html", form=form, title="Editar endereco", active_page="enderecos", endereco_id=endereco_id)

@bp.route("/web/enderecos/<int:endereco_id>/deletar", methods=["POST"])
@_login_required
def enderecos_deletar(endereco_id):
    status, payload = _api_request("DELETE", f"/api/enderecos/{endereco_id}")

    if _clear_session_on_auth_error(status):
        return redirect(url_for("web.login"))

    if status in (200, 204):
        flash("Endereco deletado com sucesso.", "success")
    else:
        flash(_message(payload, "Nao foi possivel deletar o endereco."), "danger")

    return redirect(url_for("web.enderecos_list"))


@bp.route("/web/contagens/novo", methods=["GET", "POST"])
@_login_required
def contagens_novo():
    form = ContagemForm()
    produtos, enderecos = _options()
    if form.validate_on_submit():
        payload = {
            "sku": form.sku.data,
            "codigo_endereco": form.codigo_endereco.data,
            "quantidade": form.quantidade.data,
            "usuario": (session.get("user") or {}).get("nome"),
        }
        if form.contado_em.data:
            payload["contado_em"] = form.contado_em.data.isoformat()
        status, response = _api_request("POST", "/api/contagens", json=payload)
        if status == 201:
            flash("Contagem registrada com sucesso.", "success")
            return redirect(url_for("web.saldo", codigo_endereco=form.codigo_endereco.data))
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        flash(_message(response, "Nao foi possivel registrar a contagem."), "danger")
    return render_template(
        "contagens_form.html",
        form=form,
        produtos=produtos,
        enderecos=enderecos,
        usuario=session.get("user") or {},
        active_page="contagens",
    )


@bp.route("/web/saldo")
@_login_required
def saldo():
    _, enderecos_payload = _fetch_list("/api/enderecos", per_page=100)
    enderecos = enderecos_payload.get("items", [])
    codigo_endereco = request.args.get("codigo_endereco", "").strip()
    saldo_payload = None
    if codigo_endereco:
        status, saldo_payload = _api_request("GET", f"/api/contagens/saldo/{codigo_endereco}")
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        if status >= 400:
            flash(_message(saldo_payload, "Nao foi possivel carregar o saldo."), "danger")
            saldo_payload = None
    return render_template(
        "saldo_endereco.html",
        enderecos=enderecos,
        codigo_endereco=codigo_endereco,
        saldo=saldo_payload,
        active_page="saldo",
    )


@bp.route("/web/divergencia")
@_login_required
def divergencia():
    _, enderecos_payload = _fetch_list("/api/enderecos", per_page=100)
    enderecos = enderecos_payload.get("items", [])
    codigo_endereco = request.args.get("codigo_endereco", "").strip()
    relatorio = None
    if codigo_endereco:
        status, relatorio = _api_request("GET", f"/api/relatorios/divergencia/{codigo_endereco}")
        if _clear_session_on_auth_error(status):
            return redirect(url_for("web.login"))
        if status >= 400:
            flash(_message(relatorio, "Nao foi possivel carregar o relatorio."), "danger")
            relatorio = None
    return render_template(
        "divergencia_endereco.html",
        enderecos=enderecos,
        codigo_endereco=codigo_endereco,
        relatorio=relatorio,
        active_page="divergencia",
    )
