# api/models/user.py
from api.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model): # ty : ignore
    __tablename__ = "users"
    __table_args__ = (
        db.UniqueConstraint("email", name="uq_users_email"),
        db.Index("ix_users_email", "email"),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(200), nullable=False)
    email: str = db.Column(db.String(200), nullable=False)
    password: str = db.Column(db.String(255), nullable=False)
    perfil: str = db.Column(db.String(50), nullable=False, default="operador")

    def __repr__(self) -> str:
        return f"<User {self.nome} ({self.perfil})>"

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def create_access_token(self) -> str:
        from flask_jwt_extended import create_access_token
        return create_access_token(
            identity=str(self.id),
            additional_claims={"perfil": self.perfil, "nome": self.nome}
        )
