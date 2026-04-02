from app import create_app
import os

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1","true","True")
    app.run(host=host, port=port, debug=debug)