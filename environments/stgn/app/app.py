from flask import Flask, jsonify, request, render_template, redirect, url_for
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

app = Flask(__name__)
app.config['DEBUG'] = True  # Ativar modo debug

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar a configuração do Kubernetes
try:
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    logger.info("Configuração do Kubernetes carregada com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar a configuração do Kubernetes: {e}")

@app.route('/test', methods=['GET'])
def test():
    logger.info("Rota de teste acessada")
    return "Test route is working!"

@app.route('/api-stgn', methods=['GET'])
def get_info_stgn():
    logger.info("Rota /api-stgn acessada")
    try:
        # Obter o nome do namespace atual
        namespace_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
        if not os.path.exists(namespace_path):
            logger.error(f"Arquivo não encontrado: {namespace_path}")
            return f"Arquivo não encontrado: {namespace_path}", 500

        with open(namespace_path, 'r') as file:
            namespace = file.read().strip()
        logger.info(f"Namespace atual: {namespace}")

        # Obter lista de namespaces
        namespaces = [ns.metadata.name for ns in v1.list_namespace().items]
        logger.info(f"Namespaces obtidos: {namespaces}")

        cluster_info = {
            "namespace": namespace,
            "namespaces": namespaces
        }
        logger.info("Informações do cluster e namespace obtidas")
        return render_template('index-stgn.html', cluster_info=cluster_info)
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {e}")
        return f"Arquivo não encontrado: {e}", 500
    except ApiException as e:
        logger.error(f"Erro da API do Kubernetes: {e}")
        return f"Erro da API do Kubernetes: {e}", 500
    except Exception as e:
        logger.error(f"Erro ao obter informações: {e}")
        return f"Erro ao obter informações: {e}", 500

@app.route('/api-stgn/namespaces', methods=['GET', 'POST'])
def create_namespace_stgn():
    logger.info("Rota /api-stgn/namespaces acessada")
    if request.method == 'POST':
        try:
            namespace_name = request.form['namespace']
            if not namespace_name:
                logger.error("O nome do namespace é obrigatório")
                return render_template('namespace-stgn.html', error="O nome do namespace é obrigatório")

            # Criar o namespace
            body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
            v1.create_namespace(body=body)
            logger.info(f"Namespace '{namespace_name}' criado com sucesso")
            return redirect(url_for('get_info_stgn'))
        except ApiException as e:
            logger.error(f"Erro ao criar namespace: {e}")
            return render_template('namespace-stgn.html', error=e.reason)
        except Exception as e:
            logger.error(f"Erro ao criar namespace: {e}")
            return render_template('namespace-stgn.html', error=str(e))
    else:
        return render_template('namespace-stgn.html')

# Manipulador de erro 404
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"Erro 404 - Página não encontrada: {request.url}")
    return jsonify(error="Página não encontrada", url=request.url), 404

if __name__ == '__main__':
    logger.info("Inicializando a aplicação...")
    app.run(host='0.0.0.0', port=5000, debug=True)  # Iniciar com debug=True