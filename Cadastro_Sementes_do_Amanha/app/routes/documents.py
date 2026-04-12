from flask import Blueprint, jsonify, send_from_directory, abort
from pathlib import Path

bp = Blueprint("documents", __name__, url_prefix="/documents")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"

DOCUMENTS = {
    "ficha_acolhimento": {
        "filename": "FICHA_DE_ACOLHIMENTO.pdf",
        "label": "Ficha de Acolhimento"
    },
    "termo_autorizacao_saida": {
        "filename": "TERMO_DE_AUTORIZAÇÃO_SAIDA_DESACOMPANHADA.pdf",
        "label": "Termo de Autorização de Saída Desacompanhada"
    },
    "termo_responsabilidade": {
        "filename": "TERMO_DE_RESPONSABILIDADE.pdf",
        "label": "Termo de Responsabilidade"
    },
    "termo_uso_imagem": {
        "filename": "TERMO_USO_DE_IMAGEM.pdf",
        "label": "Termo de Uso de Imagem"
    },
}


@bp.route("", methods=["GET"])
def list_documents():
    return jsonify([
        {
            "slug": slug,
            "label": meta["label"],
            "filename": meta["filename"],
            "download_url": f"/documents/{slug}/download"
        }
        for slug, meta in DOCUMENTS.items()
    ])


@bp.route("/<slug>/download", methods=["GET"])
def download_document(slug):
    meta = DOCUMENTS.get(slug)
    if not meta:
        abort(404)

    file_path = DOCS_DIR / meta["filename"]
    if not file_path.exists():
        abort(404)

    return send_from_directory(
        DOCS_DIR,
        meta["filename"],
        as_attachment=True
    )