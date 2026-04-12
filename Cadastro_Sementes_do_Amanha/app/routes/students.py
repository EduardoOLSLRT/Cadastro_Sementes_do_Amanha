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
from app.models.transport import StudentTransporte
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
        item = dict(item)
        if item.get("data_nascimento"):
            item["data_nascimento"] = parser.parse(item["data_nascimento"]).date()
        db.session.add(StudentResponsavelLegal(student_id=student_id, **item))

    for item in payload.get("membros_familiares", []):
        db.session.add(StudentMembroFamiliar(student_id=student_id, **item))

    for item in payload.get("pessoas_autorizadas", []):
        db.session.add(StudentPessoaAutorizada(student_id=student_id, **item))

    for beneficio in set(payload.get("beneficios", [])):
        db.session.add(StudentBeneficio(student_id=student_id, beneficio=beneficio))

    for item in set(payload.get("interacao_social", [])):
        db.session.add(StudentInteracaoSocial(student_id=student_id, item=item))

    for item in set(payload.get("locais_lazer", [])):
        db.session.add(StudentLocalLazer(student_id=student_id, item=item))

    for item in set(payload.get("servicos_utilizados", [])):
        db.session.add(StudentServicoUtilizado(student_id=student_id, item=item))


def _serialize_student_summary(s):
    return {
        "id": s.id,
        "nome_completo": s.nome_completo,
        "data_nascimento": s.data_nascimento.isoformat() if s.data_nascimento else None,
        "cpf": s.cpf,
        "escola_nome": s.escola_nome,
        "endereco_bairro": s.endereco_bairro,
    }


def _serialize_student_full(
    s,
    responsaveis,
    membros,
    autorizadas,
    beneficios,
    interacao,
    lazer,
    servicos,
    transporte,
):
    return {
        "id": s.id,
        "nome_completo": s.nome_completo,
        "data_nascimento": s.data_nascimento.isoformat() if s.data_nascimento else None,
        "idade": s.idade,
        "naturalidade": s.naturalidade,
        "raca_cor": s.raca_cor,
        "sexo": s.sexo,
        "rg": s.rg,
        "cpf": s.cpf,
        "nis": s.nis,
        "certidao_termo": s.certidao_termo,
        "certidao_folha": s.certidao_folha,
        "certidao_livro": s.certidao_livro,
        "endereco_cep": s.endereco_cep,
        "endereco_logradouro": s.endereco_logradouro,
        "endereco_numero": s.endereco_numero,
        "endereco_complemento": s.endereco_complemento,
        "endereco_bairro": s.endereco_bairro,
        "endereco_cidade": s.endereco_cidade,
        "endereco_uf": s.endereco_uf,
        "nome_pai": s.nome_pai,
        "nome_mae": s.nome_mae,
        "cras_referencia": s.cras_referencia,
        "estado_civil_pais": s.estado_civil_pais,
        "contato_conjuge_nome": s.contato_conjuge_nome,
        "contato_conjuge_telefone": s.contato_conjuge_telefone,
        "tipo_domicilio": s.tipo_domicilio,
        "renda_familiar": s.renda_familiar,
        "escola_nome": s.escola_nome,
        "escola_serie": s.escola_serie,
        "escola_ano": s.escola_ano,
        "escola_professor": s.escola_professor,
        "escola_periodo": s.escola_periodo,
        "historico_escolar": s.historico_escolar,
        "ubs_referencia": s.ubs_referencia,
        "tem_problema_saude": s.tem_problema_saude,
        "problema_saude_descricao": s.problema_saude_descricao,
        "tem_restricoes": s.tem_restricoes,
        "restricoes_descricao": s.restricoes_descricao,
        "usa_medicamentos": s.usa_medicamentos,
        "medicamentos_descricao": s.medicamentos_descricao,
        "tem_alergias": s.tem_alergias,
        "alergias_descricao": s.alergias_descricao,
        "acompanhamentos": s.acompanhamentos,
        "tem_deficiencia": s.tem_deficiencia,
        "deficiencia_descricao": s.deficiencia_descricao,
        "tem_supervisao": s.tem_supervisao,
        "supervisao_descricao": s.supervisao_descricao,
        "atividades_extras": s.atividades_extras,
        "termo_responsabilidade": s.termo_responsabilidade,
        "autorizacao_imagem": s.autorizacao_imagem,
        "autorizacao_saida": s.autorizacao_saida,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "created_by_user_id": s.created_by_user_id,
        "created_by_email": s.created_by_email,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        "updated_by_user_id": s.updated_by_user_id,
        "updated_by_email": s.updated_by_email,

        "responsaveis_legais": [
            {
                "id": r.id,
                "posicao": r.posicao,
                "nome": r.nome,
                "data_nascimento": r.data_nascimento.isoformat() if r.data_nascimento else None,
                "rg": r.rg,
                "cpf": r.cpf,
                "celular": r.celular,
                "operadora": r.operadora,
                "whatsapp": r.whatsapp,
                "fixo": r.fixo,
                "parentesco": r.parentesco,
            }
            for r in responsaveis
        ],

        "membros_familiares": [
            {
                "id": m.id,
                "nome": m.nome,
                "parentesco": m.parentesco,
                "profissao": m.profissao,
                "renda": m.renda,
            }
            for m in membros
        ],

        "pessoas_autorizadas": [
            {
                "id": p.id,
                "nome": p.nome,
                "documento": p.documento,
                "parentesco": p.parentesco,
                "telefone": p.telefone,
            }
            for p in autorizadas
        ],

        "beneficios": [b.beneficio for b in beneficios],
        "interacao_social": [i.item for i in interacao],
        "locais_lazer": [l.item for l in lazer],
        "servicos_utilizados": [sv.item for sv in servicos],

        "transporte": {
            "utiliza_van": transporte.utiliza_van,
            "endereco_rota": transporte.endereco_rota,
            "observacoes": transporte.observacoes,
        } if transporte else None,
    }


@bp.route("", methods=["POST"])
def create_student():
    data = request.get_json() or {}

    if not data.get("nome_completo"):
        return jsonify({"error": "nome_completo é obrigatório"}), 400

    normalized = _normalize_student_payload(data)
    normalized.update(_actor_headers())

    try:
        s = Student(**normalized)
        db.session.add(s)
        db.session.flush()

        _insert_related(s.id, data)

        db.session.commit()
        return jsonify({"id": s.id, "message": "Student criado"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"erro ao criar aluno: {str(e)}"}), 500


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

    return jsonify([_serialize_student_summary(s) for s in rows])


@bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id):
    s = Student.query.get_or_404(student_id)

    responsaveis = StudentResponsavelLegal.query.filter_by(student_id=student_id).order_by(
        StudentResponsavelLegal.posicao.asc()
    ).all()
    membros = StudentMembroFamiliar.query.filter_by(student_id=student_id).all()
    autorizadas = StudentPessoaAutorizada.query.filter_by(student_id=student_id).all()
    beneficios = StudentBeneficio.query.filter_by(student_id=student_id).all()
    interacao = StudentInteracaoSocial.query.filter_by(student_id=student_id).all()
    lazer = StudentLocalLazer.query.filter_by(student_id=student_id).all()
    servicos = StudentServicoUtilizado.query.filter_by(student_id=student_id).all()
    transporte = StudentTransporte.query.filter_by(student_id=student_id).first()

    return jsonify(
        _serialize_student_full(
            s,
            responsaveis,
            membros,
            autorizadas,
            beneficios,
            interacao,
            lazer,
            servicos,
            transporte,
        )
    )


@bp.route("/<int:student_id>", methods=["PATCH", "PUT"])
def update_student(student_id):
    s = Student.query.get_or_404(student_id)
    data = request.get_json() or {}

    normalized = _normalize_student_payload(data)

    try:
        for k, v in normalized.items():
            if hasattr(s, k):
                setattr(s, k, v)

        s.updated_by_user_id = request.headers.get("X-User-Id", type=int)
        s.updated_by_email = request.headers.get("X-User-Email", type=str) or "api@local"

        db.session.commit()
        return jsonify({"message": "Student atualizado"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"erro ao atualizar aluno: {str(e)}"}), 500