from api.database import db

class Produto(db.Model): # ty: ignore
    __tablename__ = 'produtos'
    __table_args__ = (
        db.UniqueConstraint("codigo", name="uq_produtos_codigo"),
        db.Index("ix_produtos_codigo", "codigo"),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    codigo: str = db.Column(db.String(100), nullable=False)
    descricao: str = db.Column(db.String(255), nullable=False)
    unidade: str = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Produto {self.codigo}>'
