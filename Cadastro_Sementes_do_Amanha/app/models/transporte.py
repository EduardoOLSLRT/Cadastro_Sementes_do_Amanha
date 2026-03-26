# app/models/transporte.py
# Transporte vinculado 1:1 ao Atendido. Enum para "utiliza_van".

from enum import StrEnum
from app.database import db
from sqlalchemy import Index

class UsaVan(StrEnum):
    SIM = "Sim"
    NAO = "Não"
    ESPERA = "Lista de espera"

class Transporte(db.Model):
    __tablename__ = "transportes"

    id = db.Column(db.Integer, primary_key=True)

    atendido_id = db.Column(
        db.Integer,
        db.ForeignKey("atendidos.id"),
        nullable=False,
        unique=True  # garante 1:1
    )

    utiliza_van = db.Column(
        db.Enum(
            UsaVan,
            name="utiliza_van_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True
        ),
        nullable=True
    )

    endereco_rota = db.Column(db.String(255))
    observacoes = db.Column(db.Text)

    __table_args__ = (
        Index("ix_transportes_utiliza_van", "utiliza_van"),
    )

    def __repr__(self) -> str:
        return f"<Transporte atendido_id={self.atendido_id} utiliza_van={self.utiliza_van}>"