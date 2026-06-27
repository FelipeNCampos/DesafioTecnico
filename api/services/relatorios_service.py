from pathlib import Path

from sqlalchemy import text

from api.database import db
from api.errors import NotFoundError
from api.models.endereco import Endereco
from api.services.helpers import iso_utc

SQL_FILE = Path(__file__).resolve().parents[2] / "sql" / "divergencia.sql"


def divergencia_por_endereco(codigo_endereco):
    endereco = Endereco.query.filter_by(codigo=codigo_endereco.strip().upper()).first()
    if not endereco:
        raise NotFoundError("Endereco nao encontrado.")

    sql = SQL_FILE.read_text(encoding="utf-8")
    rows = db.session.execute(text(sql), {"codigo_endereco": endereco.codigo}).mappings().all()

    items = []
    for row in rows:
        items.append(
            {
                "sku": row["sku"],
                "produto": row["produto"],
                "quantidade_atual": row["quantidade_atual"],
                "quantidade_anterior": row["quantidade_anterior"],
                "diferenca": row["diferenca"],
                "status": row["status"],
                "contado_em_atual": iso_utc(row["contado_em_atual"]),
                "contado_em_anterior": iso_utc(row["contado_em_anterior"]),
            }
        )

    return {
        "codigo_endereco": endereco.codigo,
        "items": items,
    }
