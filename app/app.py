from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api')
def index():
    logger.info("Requisição recebida na rota /api")
    logger.info(f"Headers: {request.headers}")
    return jsonify(message="It's working")

if __name__ == '__main__':
    logger.info("Inicializando a aplicação...")
    app.run(host='0.0.0.0', port=5000)
