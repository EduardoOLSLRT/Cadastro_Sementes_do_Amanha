from flask import Blueprint, jsonify, request
from app.database import db
from app.models.students import (
    Student,
    StudentResponsavelLegal,
    StudentMembroFamiliar,
    StudentPessoaAutorizada,
    StudentBeneficio,
    StudentInteracaoSocial,
    StudentLocalLazer,
    StudentServicoUtilizado,
)
from dateutil import parser

bp = Blueprint("students", __name__, url_prefix="/students")

DATE_FIELDS = {
    "data_nascimento",
}

BOOL_FIELDS = {
    "tem_problema_saude",
    "tem_restricoes",
    "usa_medicamentos",
    "tem_alergias",
    "tem_deficiencia",
    "tem_supervisao",
    "termo_responsabilidade",
    "autorizacao_imagem",
}

INT_FIELDS = {
    "idade",
}

ALLOWED_FIELDS = {
    "nome_completo",
    "data_nascimento",
    "idade",
    "naturalidade",
    "raca_cor",
    "sexo",
    "rg",
    "cpf",
    "nis",
    "certidao_termo",
    "certidao_folha",
    "certidao_livro",
    "endereco_cep",
    "endereco_logradouro",
    "endereco_numero",
    "endereco_complemento",
    "endereco_bairro",
    "endereco_cidade",
    "endereco_uf",
    "nome_pai",
    "nome_mae",
    "cras_referencia",
    "estado_civil_pais",
    "contato_conjuge_nome",
    "contato_conjuge_telefone",
    "tipo_domicilio",
    "renda_familiar",
    "escola_nome",
    "escola_serie",
    "escola_ano",
    "escola_professor",
    "escola_periodo",
    "historico_escolar",
    "ubs_referencia",
    "tem_problema_saude",
    "problema_saude_descricao",
    "tem_restricoes",
    "restricoes_descricao",
    "usa_medicamentos",
    "medicamentos_descricao",
    "tem_alergias",
    "alergias_descricao",
    "acompanhamentos",
    "tem_deficiencia",
    "deficiencia_descricao",
    "tem_supervisao",
    "supervisao_descricao",
    "atividades_extras",
    "termo_responsabilidade",
    "autorizacao_imagem",
    "autorizacao_saida",
}


def _actor_headers():
    return {
        "created_by_user_id": request.headers.get("X-User-Id", type=int),
        "created_by_email": request.headers.get("X-User-Email", type=str) or "api@local",
        "updated_by_user_id": request.headers.get("X-User-Id", type=int),
        "updated_by_email": request.headers.get("X-User-Email", type=str) or "api@local",
    }


def _parse_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "1", "sim", "yes"}:
            return True
        if v in {"false", "0", "nao", "não", "no"}:
            return False
    return value


def _normalize_student_payload(data):
    normalized = {}

    for key, value in data.items():
        if key not in ALLOWED_FIELDS:
            continue

        if value == "":
            value = None

        if key in DATE_FIELDS and value:
            value = parser.parse(value).date()
        elif key in BOOL_FIELDS:
            value = _parse_bool(value)
        elif key in INT_FIELDS and value is not None:
            value = int(value)

        normalized[key] = value

    return normalized


def _insert_related(student_id, payload):
    for item in payload.get("responsaveis_legais", []):
        if item.get("data_nascimento"):
            item["data_nascimento"] = parser.parse(item["data_nascimento"]).date()
        db.session.add(StudentResponsavelLegal(student_id=student_id, **item))

    for item in payload.get("membros_familiares", []):
        db.session.add(StudentMembroFamiliar(student_id=student_id, **item))

    for item in payload.get("pessoas_autorizadas", []):
        db.session.add(StudentPessoaAutorizada(student_id=student_id, **item))

    for beneficio in payload.get("beneficios", []):
        db.session.add(StudentBeneficio(student_id=student_id, beneficio=beneficio))

    for item in payload.get("interacao_social", []):
        db.session.add(StudentInteracaoSocial(student_id=student_id, item=item))

    for item in payload.get("locais_lazer", []):
        db.session.add(StudentLocalLazer(student_id=student_id, item=item))

    for item in payload.get("servicos_utilizados", []):
        db.session.add(StudentServicoUtilizado(student_id=student_id, item=item))


@bp.route("", methods=["POST"])
def create_student():
    data = request.get_json() or {}

    if not data.get("nome_completo"):
        return jsonify({"error": "nome_completo é obrigatório"}), 400

    normalized = _normalize_student_payload(data)
    normalized.update(_actor_headers())

    s = Student(**normalized)
    db.session.add(s)
    db.session.flush()

    _insert_related(s.id, data)

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

    normalized = _normalize_student_payload(data)

    for k, v in normalized.items():
        if hasattr(s, k):
            setattr(s, k, v)

    s.updated_by_user_id = request.headers.get("X-User-Id", type=int)
    s.updated_by_email = request.headers.get("X-User-Email", type=str) or "api@local"

    db.session.commit()
    return jsonify({"message": "Student atualizado"})
