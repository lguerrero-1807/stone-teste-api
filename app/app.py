from flask import Flask, jsonify, request
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar a configuração do Kubernetes
config.load_incluster_config()
v1 = client.CoreV1Api()

@app.route('/api', methods=['GET'])
def get_info():
    try:
        # Obter o nome do namespace atual
        namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()

        # Obter lista de namespaces
        namespaces = [ns.metadata.name for ns in v1.list_namespace().items]

        cluster_info = {
            "namespace": namespace,
            "namespaces": namespaces
        }
        logger.info("Informações do cluster e namespace obtidas")
        return jsonify(cluster_info)
    except Exception as e:
        logger.error(f"Erro ao obter informações: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/namespace', methods=['POST'])
def create_namespace():
    try:
        data = request.get_json()
        namespace_name = data.get("namespace")
        if not namespace_name:
            return jsonify({"error": "O nome do namespace é obrigatório"}), 400

        # Criar o namespace
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
        v1.create_namespace(body=body)
        logger.info(f"Namespace '{namespace_name}' criado com sucesso")
        return jsonify({"message": f"Namespace '{namespace_name}' criado com sucesso"}), 201
    except ApiException as e:
        logger.error(f"Erro ao criar namespace: {e}")
        return jsonify({"error": e.reason}), e.status
    except Exception as e:
        logger.error(f"Erro ao criar namespace: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Inicializando a aplicação...")
    app.run(host='0.0.0.0', port=5000)
