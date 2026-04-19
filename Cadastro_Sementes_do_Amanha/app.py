import os
from app import create_app
from app.routes.documents import bp as documents_bp

app = create_app()

# Registra a Blueprint de documentos ANTES de rodar o servidor
# Isso permite que as rotas /documents/<slug>/emitir fiquem ativas
app.register_blueprint(documents_bp)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    print(f"Servidor iniciado em http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)