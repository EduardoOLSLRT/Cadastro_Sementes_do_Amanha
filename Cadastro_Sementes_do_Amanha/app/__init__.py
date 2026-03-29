# app/__init__.py
from flask import Flask
from app.database import db
from pathlib import Path
from sqlalchemy import inspect

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Caminho absoluto para sementes.db na raiz do projeto
    BASE_DIR = Path(__file__).resolve().parent.parent  # .../Cadastro_Sementes_do_Amanha
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{(BASE_DIR / 'sementes.db').as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Importa e registra as rotas
    from app.routes import main_bp, atendidos_bp, frequencia_bp, relatorios_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(atendidos_bp)
    app.register_blueprint(frequencia_bp)
    app.register_blueprint(relatorios_bp)

    # Cria as tabelas (DEV) e faz um log do que foi criado
    with app.app_context():
        # IMPORTANTE: importar os models ANTES do create_all
        from app.models.atendidos import Atendido
        from app.models.transporte import Transporte
        from app.models.frequencia import Frequencia
        from app.models.user import User

        db.create_all()

        # Log de verificação
        insp = inspect(db.engine)
        print(">> DB URL:", db.engine.url)
        print(">> Tabelas existentes:", insp.get_table_names())

    return app