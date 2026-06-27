from datetime import datetime, timedelta, timezone

from api import create_app
from api.database import db
from api.models.contagem import Contagem
from api.models.endereco import Endereco
from api.models.produto import Produto
from api.models.user import User


PRODUTOS = [
    ("SKU001", "Parafuso sextavado", "UN"),
    ("SKU002", "Porca 10mm", "UN"),
    ("SKU003", "Arruela lisa", "UN"),
    ("SKU004", "Caixa plastica", "CX"),
    ("SKU005", "Pallet PBR", "PALETE"),
    ("SKU006", "Fita adesiva", "UN"),
    ("SKU007", "Etiqueta termica", "ROLO"),
    ("SKU008", "Cabo PP", "M"),
    ("SKU009", "Luva de seguranca", "PAR"),
    ("SKU010", "Filme stretch", "ROLO"),
]

ENDERECOS = [
    ("R01-P01-N01-A01", "Rua 01 posicao 01 nivel 01"),
    ("R01-P02-N01-A01", "Rua 01 posicao 02 nivel 01"),
    ("R02-P01-N02-A03", "Rua 02 posicao 01 nivel 02"),
    ("R02-P03-N01-A02", "Rua 02 posicao 03 nivel 01"),
    ("R03-P01-N03-A01", "Rua 03 posicao 01 nivel 03"),
]

USERS = [
    ("Felipe", "felipe@gmail.com", "coto1423", "gerente"),
    ("João", "joao@gmail.com", "joao123", "operador")
]
def get_or_create_user(nome, email, password, perfil):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(nome=nome, email=email, password=User.hash_password(password), perfil=perfil)
    db.session.add(user)
    db.session.commit()
    return user


def seed():
    app = create_app()
    with app.app_context():
        gerente = get_or_create_user("Gerente", "gerente@example.com", "gerente123", "gerente")
        operador = get_or_create_user("Operador", "operador@example.com", "operador123", "operador")

        for codigo, descricao, unidade in PRODUTOS:
            if not Produto.query.filter_by(codigo=codigo).first():
                db.session.add(Produto(codigo=codigo, descricao=descricao, unidade=unidade))

        for codigo, descricao in ENDERECOS:
            if not Endereco.query.filter_by(codigo=codigo).first():
                db.session.add(Endereco(codigo=codigo, descricao=descricao))
            
        for nome, email, password, perfil in USERS:
            get_or_create_user(nome, email, password, perfil)

        db.session.commit()

        if Contagem.query.count() >= 30:
            print("Seed ja possui pelo menos 30 contagens. Nada a fazer.")
            return

        produtos = Produto.query.order_by(Produto.codigo).all()
        enderecos = Endereco.query.order_by(Endereco.codigo).all()
        base_date = datetime.now(timezone.utc) - timedelta(days=10)

        for index in range(30):
            produto = produtos[index % len(produtos)]
            endereco = enderecos[index % len(enderecos)]
            usuario = gerente if index % 5 == 0 else operador
            db.session.add(
                Contagem(
                    produto_id=produto.id,
                    endereco_id=endereco.id,
                    usuario_id=usuario.id,
                    quantidade=(index * 3) % 50,
                    contado_em=base_date + timedelta(hours=index * 6),
                )
            )

        db.session.commit()
        print("Seed concluido: usuarios, produtos, enderecos e contagens criados.")


if __name__ == "__main__":
    seed()
