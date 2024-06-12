# Stone Teste API

## Descrição

Este projeto é uma API de teste criada para demonstrar a implementação de serviços backend usando Python. Ele inclui exemplos de como configurar um ambiente Docker, implementar a aplicação e gerenciar a infraestrutura com Kubernetes.

## Estrutura do Repositório

- `app/`: Contém o código da aplicação Flask e os templates HTML.
- `environments/`: Contém as configurações específicas de cada ambiente (staging e produção).
    - `stgn/`: Configurações para o ambiente de staging.
    - `prod/`: Configurações para o ambiente de produção.
- `Dockerfile.prod`: Dockerfile para o ambiente de produção.
- `Dockerfile.staging`: Dockerfile para o ambiente de staging.
- `.github/workflows/`: Contém os workflows do GitHub Actions para CI/CD.

## Uso

Basta utilizar o github action
