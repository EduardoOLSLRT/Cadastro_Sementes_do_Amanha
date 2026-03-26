# app/routes.py
from flask import Blueprint, jsonify, request
from dateutil import parser
from sqlalchemy import func, case

from app.database import db
from app.models.atendidos import Atendido, Genero, Periodo, Situacao
from app.models.frequencia import Frequencia, StatusFrequencia
from app.models.transporte import Transporte, UsaVan
from app.services.turma import calcular_turma

# ---- helper: converter string -> Enum com erro amigável ----
def parse_enum(value, enum_cls, field_name):
    if value is None:
        return None
    try:
        return enum_cls(value)
    except ValueError:
        aceitos = ", ".join(e.value for e in enum_cls)
        raise ValueError(f"Valor inválido para '{field_name}': '{value}'. Aceitos: {aceitos}.")

# ---------- HEALTH ----------
main_bp = Blueprint("main", __name__)

@main_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Sementes do Amanhã API"}), 200

# ---------- ATENDIDOS ----------
atendidos_bp = Blueprint("atendidos", __name__, url_prefix="/atendidos")

@atendidos_bp.route("", methods=["POST"])
def cadastrar_atendido():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON obrigatório"}), 400

    obrigatorios = ["nome", "data_nascimento", "unidade", "periodo"]
    faltando = [c for c in obrigatorios if c not in data]
    if faltando:
        return jsonify({"error": f"Campos faltando: {faltando}"}), 400

    data_nasc = parser.parse(data["data_nascimento"]).date()

    # parse de enums
    try:
        genero   = parse_enum(data.get("genero"), Genero, "genero")
        periodo  = parse_enum(data["periodo"], Periodo, "periodo")
        situacao = parse_enum(data.get("situacao", Situacao.ATIVO.value), Situacao, "situacao")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    a = Atendido(
        nome=data["nome"],
        data_nascimento=data_nasc,
        genero=genero,
        unidade=data["unidade"],
        periodo=periodo,
        escola=data.get("escola"),
        bairro=data.get("bairro"),
        situacao=situacao,
    )
    a.turma = calcular_turma(a.data_nascimento)

    db.session.add(a)
    db.session.flush()  # pega a.id

    # Transporte (opcional)
    t = data.get("transporte")
    if t:
        try:
            utiliza_van = parse_enum(t.get("utiliza_van"), UsaVan, "utiliza_van")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        db.session.add(Transporte(
            atendido_id=a.id,
            utiliza_van=utiliza_van,
            endereco_rota=t.get("endereco_rota"),
            observacoes=t.get("observacoes"),
        ))

    db.session.commit()
    return jsonify({"id": a.id, "message": "Atendido cadastrado"}), 201


@atendidos_bp.route("", methods=["GET"])
def listar_atendidos():
    q = Atendido.query
    args = request.args

    # Filtros (convertemos strings em Enum quando aplicável)
    gen = args.get("genero")
    if gen:
        try:
            gen = parse_enum(gen, Genero, "genero")
            q = q.filter(Atendido.genero == gen)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    turma = args.get("turma")
    if turma:
        q = q.filter(Atendido.turma == turma)

    sit = args.get("situacao")
    if sit:
        try:
            sit = parse_enum(sit, Situacao, "situacao")
            q = q.filter(Atendido.situacao == sit)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    unidade = args.get("unidade")
    if unidade:
        q = q.filter(Atendido.unidade == unidade)

    per = args.get("periodo")
    if per:
        try:
            per = parse_enum(per, Periodo, "periodo")
            q = q.filter(Atendido.periodo == per)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    escola = args.get("escola")
    if escola:
        q = q.filter(Atendido.escola == escola)

    bairro = args.get("bairro")
    if bairro:
        q = q.filter(Atendido.bairro == bairro)

    utiliza_van = args.get("utiliza_van")
    if utiliza_van:
        try:
            utiliza_van = parse_enum(utiliza_van, UsaVan, "utiliza_van")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        q = q.join(Transporte, Transporte.atendido_id == Atendido.id)\
             .filter(Transporte.utiliza_van == utiliza_van)

    rows = q.order_by(Atendido.nome.asc()).all()
    res = [{
        "id": a.id,
        "nome": a.nome,
        "genero": a.genero.value if a.genero else None,
        "unidade": a.unidade,
        "periodo": a.periodo.value if a.periodo else None,
        "turma": a.turma,
        "escola": a.escola,
        "bairro": a.bairro,
        "situacao": a.situacao.value if a.situacao else None,
        "data_matricula": a.data_matricula.isoformat(),
    } for a in rows]

    return jsonify(res)


@atendidos_bp.route("/<int:atendido_id>", methods=["PUT", "PATCH"])
def atualizar_atendido(atendido_id):
    data = request.get_json() or {}
    a = Atendido.query.get_or_404(atendido_id)

    # regra: ao desativar, motivo é obrigatório
    if data.get("situacao") == Situacao.DESATIVADO.value and not data.get("motivo_desligamento"):
        return jsonify({"error": "Informe 'motivo_desligamento' para situacao 'Desativado'."}), 400

    # parse de enums se presentes
    try:
        if "genero"   in data: data["genero"]   = parse_enum(data["genero"],   Genero,   "genero")
        if "periodo"  in data: data["periodo"]  = parse_enum(data["periodo"],  Periodo,  "periodo")
        if "situacao" in data: data["situacao"] = parse_enum(data["situacao"], Situacao, "situacao")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # aplica campos
    for campo in ["nome", "genero", "unidade", "periodo", "escola", "bairro", "situacao", "motivo_desligamento"]:
        if campo in data:
            setattr(a, campo, data[campo])

    if "data_nascimento" in data:
        a.data_nascimento = parser.parse(data["data_nascimento"]).date()
        a.turma = calcular_turma(a.data_nascimento)

    db.session.commit()
    return jsonify({"message": "Atualizado"}), 200

# ---------- FREQUÊNCIA ----------
frequencia_bp = Blueprint("frequencia", __name__, url_prefix="/frequencia")

@frequencia_bp.route("/turma", methods=["GET"])
def lista_por_turma():
    turma = request.args.get("turma")
    data_str = request.args.get("data")
    unidade = request.args.get("unidade")
    periodo = request.args.get("periodo")

    if not turma or not data_str:
        return jsonify({"error": "turma e data são obrigatórios"}), 400

    data = parser.parse(data_str).date()

    q = Atendido.query.filter(Atendido.turma == turma, Atendido.situacao == Situacao.ATIVO)
    if unidade: q = q.filter(Atendido.unidade == unidade)
    if periodo:
        try:
            periodo = parse_enum(periodo, Periodo, "periodo")
            q = q.filter(Atendido.periodo == periodo)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    alunos = q.order_by(Atendido.nome.asc()).all()
    ids = [a.id for a in alunos] or [-1]

    marcacoes = {
        f.atendido_id: (f.status.value if f.status else None)
        for f in Frequencia.query.filter(
            Frequencia.data == data,
            Frequencia.atendido_id.in_(ids)
        )
    }

    return jsonify([
        {"id": a.id, "nome": a.nome, "status": marcacoes.get(a.id)}
        for a in alunos
    ])

@frequencia_bp.route("", methods=["POST"])
def marcar_frequencia():
    payload = request.get_json() or {}
    if "data" not in payload or "marcacoes" not in payload:
        return jsonify({"error": "data e marcacoes são obrigatórios"}), 400

    data = parser.parse(payload["data"]).date()

    for m in payload["marcacoes"]:
        aid = m["atendido_id"]
        try:
            status = parse_enum(m["status"], StatusFrequencia, "status")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        freq = Frequencia.query.filter_by(atendido_id=aid, data=data).first()
        if freq:
            freq.status = status
        else:
            db.session.add(Frequencia(atendido_id=aid, data=data, status=status))

    db.session.commit()
    return jsonify({"message": "Frequência registrada"}), 201

@frequencia_bp.route("/mensal", methods=["GET"])
def relatorio_mensal():
    try:
        mes = int(request.args.get("mes"))
        ano = int(request.args.get("ano"))
    except (TypeError, ValueError):
        return jsonify({"error": "mes e ano são obrigatórios (inteiros)"}), 400

    unidade = request.args.get("unidade")
    turma = request.args.get("turma")
    periodo = request.args.get("periodo")

    q_alunos = Atendido.query.filter(Atendido.situacao == Situacao.ATIVO)
    if unidade: q_alunos = q_alunos.filter(Atendido.unidade == unidade)
    if turma:   q_alunos = q_alunos.filter(Atendido.turma == turma)
    if periodo:
        try:
            periodo = parse_enum(periodo, Periodo, "periodo")
            q_alunos = q_alunos.filter(Atendido.periodo == periodo)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    alunos = q_alunos.all()
    ids = [a.id for a in alunos] or [-1]

    mm = f"{mes:02d}"
    yy = str(ano)

    agreg = db.session.query(
        Frequencia.atendido_id,
        func.count(Frequencia.id).label("total"),
        func.sum(case((Frequencia.status == StatusFrequencia.PRESENCA, 1), else_=0)).label("presencas")
    ).filter(
        Frequencia.atendido_id.in_(ids),
        func.strftime('%m', Frequencia.data) == mm,
        func.strftime('%Y', Frequencia.data) == yy
    ).group_by(Frequencia.atendido_id).all()

    mapa = {r.atendido_id: {"total": r.total, "presencas": int(r.presencas or 0)} for r in agreg}

    res = []
    for a in alunos:
        tot = mapa.get(a.id, {}).get("total", 0)
        pres = mapa.get(a.id, {}).get("presencas", 0)
        perc = round((pres / tot) * 100, 2) if tot else 0.0
        res.append({
            "id": a.id,
            "nome": a.nome,
            "turma": a.turma,
            "unidade": a.unidade,
            "total_aulas": tot,
            "presencas": pres,
            "percentual_presenca": perc
        })

    res.sort(key=lambda x: x["nome"])
    return jsonify(res)

# ---------- RELATÓRIOS ----------
relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

@relatorios_bp.route("/resumo", methods=["GET"])
def resumo():
    total_ativos = Atendido.query.filter_by(situacao=Situacao.ATIVO).count()

    # total por turma (string)
    total_por_turma = dict(
        db.session.query(Atendido.turma, func.count(Atendido.id)).group_by(Atendido.turma).all()
    )

    # total por gênero (Enum -> serialize value)
    raw_genero = db.session.query(Atendido.genero, func.count(Atendido.id))\
                           .group_by(Atendido.genero).all()
    total_por_genero = { (g.value if g is not None else None): c for g, c in raw_genero }

    lista_espera = Atendido.query.filter_by(situacao=Situacao.LISTA).count()

    return jsonify({
        "total_ativos": total_ativos,
        "total_por_turma": total_por_turma,
        "total_por_genero": total_por_genero,
        "lista_espera": lista_espera
    })

__all__ = ["main_bp", "atendidos_bp", "frequencia_bp", "relatorios_bp"]