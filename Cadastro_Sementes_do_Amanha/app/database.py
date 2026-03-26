# app/database.py
# Mantém UMA instância do SQLAlchemy (ORM) para toda a aplicação.
# Todos os models importam 'db' daqui.

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()