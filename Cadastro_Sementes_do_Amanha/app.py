import os
from dotenv import load_dotenv
from flask import render_template
from app import create_app

load_dotenv()

app = create_app()
app.template_folder = os.path.join(os.getcwd(), 'templates')

@app.route('/emitir-uso-imagem')
def pagina_uso_imagem():
    return render_template('termo_uso_de_imagem.html')

@app.route('/emitir-ficha-acolhimento')
def pagina_ficha():
    return render_template('ficha_de_acolhimento.html')

@app.route('/emitir-responsabilidade')
def pagina_responsabilidade():
    return render_template('termo_de_responsabilidade.html')

@app.route('/emitir-saida')
def pagina_saida():
    return render_template('termo_de_autorizacao_saida.html')

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    
    print(f"Servidor iniciado em http://{host}:{port}/emitir-docs")
    app.run(host=host, port=port, debug=debug)