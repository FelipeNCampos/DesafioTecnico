from api.database import db


class Contagem(db.Model):  # ty: ignore
    __tablename__ = "contagens"
    __table_args__ = (
        db.Index(
            "ix_contagens_endereco_produto_data",
            "endereco_id",
            "produto_id",
            "contado_em",
        ),
        db.Index("ix_contagens_produto_data", "produto_id", "contado_em"),
        db.Index("ix_contagens_endereco_data", "endereco_id", "contado_em"),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    produto_id: int = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantidade: int = db.Column(db.Integer, nullable=False)
    endereco_id: int = db.Column(
        db.Integer, db.ForeignKey("enderecos.id", ondelete="CASCADE"), nullable=False
    )
    contado_em = db.Column(db.DateTime(timezone=True), nullable=False)
    usuario_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    produto = db.relationship("Produto", back_populates="contagens")
    endereco = db.relationship("Endereco", back_populates="contagens")
    usuario = db.relationship("User", backref=db.backref("contagens", lazy=True))

    def __repr__(self):
        return f"<Contagem {self.id}>"
