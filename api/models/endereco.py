from api.database import db

class Endereco(db.Model): # ty: ignore
    __tablename__ = 'enderecos'
    __table_args__ = (
        db.UniqueConstraint("codigo", name="uq_enderecos_codigo"),
        db.Index("ix_enderecos_codigo", "codigo"),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    codigo: str = db.Column(db.String(100), nullable=False)
    descricao: str = db.Column(db.String(255), nullable=True)

    contagens = db.relationship(
        "Contagem",
        back_populates="endereco",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f'<Endereco {self.codigo}>'
