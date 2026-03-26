# app/models/atendidos.py
# Modelo principal (Atendido) com Enums e índices p/ filtros.

from enum import StrEnum
from datetime import date
from app.database import db
from sqlalchemy import Index

# -------------------- ENUNS DE DOMÍNIO --------------------
class Genero(StrEnum):
    MENINA = "Menina"
    MENINO = "Menino"

class Periodo(StrEnum):
    MANHA = "Manhã"
    TARDE = "Tarde"

class Situacao(StrEnum):
    ATIVO = "Ativo"
    DESATIVADO = "Desativado"
    LISTA = "Lista de espera"

# -------------------- MODELO --------------------
class Atendido(db.Model):
    __tablename__ = "atendidos"

    id = db.Column(db.Integer, primary_key=True)

    # Dados pessoais
    nome = db.Column(db.String(120), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)

    genero = db.Column(
        db.Enum(
            Genero,
            name="genero_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True
        ),
        nullable=True
    )

    # Dados institucionais
    unidade = db.Column(db.String(100), nullable=False)

    periodo = db.Column(
        db.Enum(
            Periodo,
            name="periodo_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True
        ),
        nullable=False
    )

    turma = db.Column(db.String(20))  # calculada automaticamente

    # Dados escolares / localização
    escola = db.Column(db.String(120))
    bairro = db.Column(db.String(120))

    # Gestão do cadastro
    data_matricula = db.Column(db.Date, default=date.today, nullable=False)

    situacao = db.Column(
        db.Enum(
            Situacao,
            name="situacao_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True
        ),
        default=Situacao.ATIVO,
        nullable=False
    )

    motivo_desligamento = db.Column(db.String(255))

    # -------------------- RELACIONAMENTOS --------------------
    transporte = db.relationship(
        "Transporte",
        backref="atendido",
        uselist=False,
        cascade="all, delete-orphan"
    )

    frequencias = db.relationship(
        "Frequencia",
        backref="atendido",
        cascade="all, delete-orphan"
    )

    # -------------------- ÍNDICES ÚTEIS --------------------
    __table_args__ = (
        Index("ix_atendidos_turma", "turma"),
        Index("ix_atendidos_situacao", "situacao"),
        Index("ix_atendidos_unidade", "unidade"),
        Index("ix_atendidos_periodo", "periodo"),
        Index("ix_atendidos_genero", "genero"),
    )

    # -------------------- HELPERS --------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "data_nascimento": self.data_nascimento.isoformat() if self.data_nascimento else None,
            "genero": self.genero.value if self.genero else None,
            "unidade": self.unidade,
            "periodo": self.periodo.value if self.periodo else None,
            "turma": self.turma,
            "escola": self.escola,
            "bairro": self.bairro,
            "data_matricula": self.data_matricula.isoformat() if self.data_matricula else None,
            "situacao": self.situacao.value if self.situacao else None,
            "motivo_desligamento": self.motivo_desligamento
        }

    def __repr__(self) -> str:
        return f"<Atendido id={self.id} nome={self.nome!r} turma={self.turma!r} situacao={self.situacao}>"