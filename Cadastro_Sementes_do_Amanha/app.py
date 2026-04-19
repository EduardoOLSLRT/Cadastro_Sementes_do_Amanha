import os
from dotenv import load_dotenv
from flask import render_template
from app import create_app

load_dotenv()

# Aqui está o segredo: dizemos ao Flask exatamente onde a pasta templates está
app = create_app()
app.template_folder = os.path.join(os.getcwd(), 'templates')

@app.route('/emitir-docs')
def pagina_emissao():
    # O nome aqui deve ser igual ao arquivo na sua pasta templates
    return render_template('termo_uso_de_imagem.html')

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    
    print(f"Servidor iniciado em http://{host}:{port}/emitir-docs")
    app.run(host=host, port=port, debug=debug)