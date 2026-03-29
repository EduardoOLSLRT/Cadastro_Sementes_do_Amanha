from app.database import db
from sqlalchemy import func

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.Text, nullable=False, index=True)
    data_nascimento = db.Column(db.Date)
    endereco_bairro = db.Column(db.Text, index=True)
    escola_nome = db.Column(db.Text, index=True)
    escola_periodo = db.Column(db.Text)
    cpf = db.Column(db.Text, index=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by_email = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by_email = db.Column(db.Text, nullable=False)
