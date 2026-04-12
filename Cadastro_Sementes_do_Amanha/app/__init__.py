from flask import Flask
from app.database import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from app.config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)

    from app.routes.main import bp as main_bp
    from app.routes.users import bp as users_bp
    from app.routes.students import bp as students_bp
    from app.routes.attendance import bp as attendance_bp
    from app.routes.transport import bp as transport_bp
    from app.routes.documents import bp as documents_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(transport_bp)
    app.register_blueprint(documents_bp)
    return app