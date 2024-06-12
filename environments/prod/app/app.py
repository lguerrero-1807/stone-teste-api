from flask import Flask, jsonify, request, render_template, redirect, url_for
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
        return render_template('index.html', cluster_info=cluster_info)
    except Exception as e:
        logger.error(f"Erro ao obter informações: {e}")
        return render_template('index.html', error=str(e))

@app.route('/api/namespaces', methods=['GET', 'POST'])
def create_namespace():
    if request.method == 'POST':
        try:
            namespace_name = request.form['namespace']
            if not namespace_name:
                return render_template('namespace.html', error="O nome do namespace é obrigatório")

            # Criar o namespace
            body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
            v1.create_namespace(body=body)
            logger.info(f"Namespace '{namespace_name}' criado com sucesso")
            return redirect(url_for('get_info'))
        except ApiException as e:
            logger.error(f"Erro ao criar namespace: {e}")
            return render_template('namespace.html', error=e.reason)
        except Exception as e:
            logger.error(f"Erro ao criar namespace: {e}")
            return render_template('namespace.html', error=str(e))
    else:
        return render_template('namespace.html')

if __name__ == '__main__':
    logger.info("Inicializando a aplicação...")
    app.run(host='0.0.0.0', port=5000)
