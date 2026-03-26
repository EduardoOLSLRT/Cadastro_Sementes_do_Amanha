# app/models/frequencia.py
# Marcações de presença/falta por data. Enum para "status" e UniqueConstraint.

from enum import StrEnum
from app.database import db
from sqlalchemy import Index

class StatusFrequencia(StrEnum):
    PRESENCA = "Presença"
    FALTA = "Falta"

class Frequencia(db.Model):
    __tablename__ = "frequencias"

    id = db.Column(db.Integer, primary_key=True)

    atendido_id = db.Column(
        db.Integer,
        db.ForeignKey("atendidos.id"),
        nullable=False
    )

    data = db.Column(db.Date, nullable=False)

    status = db.Column(
        db.Enum(
            StatusFrequencia,
            name="frequencia_status_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True
        ),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("atendido_id", "data", name="uq_freq_atendido_data"),
        Index("ix_frequencias_data", "data"),
    )

    def __repr__(self) -> str:
        return f"<Frequencia atendido_id={self.atendido_id} data={self.data} status={self.status}>"