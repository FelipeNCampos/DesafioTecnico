from flask import Flask
from flask_smorest import Api

from api.config import Config
from api.database import db
from api.errors import register_error_handlers
from api.extensions import jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config["API_TITLE"] = "Estoque X API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
                "OAuth2PasswordBearer": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "tokenUrl": "/auth/token",
                            "scopes": {},
                        }
                    },
                },
            }
        },
        "security": [{"OAuth2PasswordBearer": []}, {"BearerAuth": []}],
    }

    db.init_app(app)
    jwt.init_app(app)
    register_error_handlers(app, jwt)

    from api.models import Contagem, Endereco, Produto, User  # noqa: F401

    with app.app_context():
        db.create_all()

    api = Api(app)

    from api.routes import auth, contagens, enderecos, produtos, relatorios, web

    app.register_blueprint(web.bp)
    api.register_blueprint(auth.blp)
    api.register_blueprint(produtos.blp)
    api.register_blueprint(enderecos.blp)
    api.register_blueprint(contagens.blp)
    api.register_blueprint(relatorios.blp)

    return app
