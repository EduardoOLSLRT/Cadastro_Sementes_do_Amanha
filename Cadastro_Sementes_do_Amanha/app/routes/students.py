from flask import Blueprint, jsonify, request
from app.database import db
from app.models.students import Student
from dateutil import parser

bp = Blueprint("students", __name__, url_prefix="/students")

def _actor_headers():
    return {
        "created_by_user_id": request.headers.get("X-User-Id", type=int),
        "created_by_email": request.headers.get("X-User-Email", type=str) or "api@local",
        "updated_by_user_id": request.headers.get("X-User-Id", type=int),
        "updated_by_email": request.headers.get("X-User-Email", type=str) or "api@local",
    }

@bp.route("", methods=["POST"])
def create_student():
    data = request.get_json() or {}

    if not data.get("nome_completo"):
        return jsonify({"error": "nome_completo é obrigatório"}), 400

    # converter data_nascimento string -> date
    if data.get("data_nascimento"):
        data["data_nascimento"] = parser.parse(data["data_nascimento"]).date()

    data.update(_actor_headers())

    s = Student(**data)
    db.session.add(s)
    db.session.commit()

    return jsonify({"id": s.id, "message": "Student criado"}), 201


@bp.route("", methods=["GET"])
def list_students():
    q = Student.query
    if n := request.args.get("nome"):
        q = q.filter(Student.nome_completo.ilike(f"%{n}%"))
    if cpf := request.args.get("cpf"):
        q = q.filter(Student.cpf == cpf)
    if escola := request.args.get("escola_nome"):
        q = q.filter(Student.escola_nome == escola)
    if bairro := request.args.get("endereco_bairro"):
        q = q.filter(Student.endereco_bairro == bairro)

    rows = q.order_by(Student.nome_completo.asc()).limit(200).all()

    return jsonify([
        {
            "id": s.id,
            "nome_completo": s.nome_completo,
            "data_nascimento": s.data_nascimento.isoformat() if s.data_nascimento else None,
            "cpf": s.cpf,
            "escola_nome": s.escola_nome,
            "endereco_bairro": s.endereco_bairro
        }
        for s in rows
    ])


@bp.route("/<int:student_id>", methods=["PATCH", "PUT"])
def update_student(student_id):
    s = Student.query.get_or_404(student_id)
    data = request.get_json() or {}

    if data.get("data_nascimento"):
        data["data_nascimento"] = parser.parse(data["data_nascimento"]).date()

    for k, v in data.items():
        if hasattr(s, k):
            setattr(s, k, v)

    s.updated_by_user_id = request.headers.get("X-User-Id", type=int)
    s.updated_by_email = request.headers.get("X-User-Email", type=str) or "api@local"

    db.session.commit()
    return jsonify({"message": "Student atualizado"})
