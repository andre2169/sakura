# SAKURÁ - Assistente de Voz
===========================

## Descrição do Projeto

SAKURÁ é um assistente de voz que utiliza tecnologias de processamento de linguagem natural e inteligência artificial para realizar tarefas e fornecer informações. O projeto é dividido em módulos responsáveis por captura e reconhecimento de voz, síntese e reprodução de áudio, comunicação com APIs e autenticação em plataformas como o GitHub.

## Funcionalidades Principais

- Captura e reconhecimento de voz
- Síntese e reprodução de áudio
- Comunicação com a API da Groq
- Autenticação e requisições no GitHub
- Gerenciamento de repositórios e issues

## Tecnologias Usadas

- Python
- Pygame
- Edge-TTS
- Groq API
- GitHub API

## Como Instalar e Rodar

1. Clone o repositório utilizando o comando `git clone https://github.com/usuario/sakura.git`
2. Acesse a pasta do projeto e instale as dependências com `pip install -r requirements.txt`
3. Execute o comando `python main.py` para iniciar o assistente de voz

## Como Usar

1. Inicie o assistente de voz com o comando `python main.py`
2. Use comandos de voz para realizar tarefas, como:
 * `abrir repositório` para criar um novo repositório no GitHub
 * `listar issues` para listar as issues de um repositório
 * `fazer commit` para fazer um commit de arquivos
3. O assistente de voz responderá com a ação realizada ou fornecerá informações solicitadas

## Estrutura do Projeto

O projeto é dividido em módulos responsáveis por diferentes funções:

* `core/`: contém a lógica do assistente de voz, incluindo o loop principal e o roteamento de comandos
* `voice/`: contém a lógica de captura e reconhecimento de voz, síntese e reprodução de áudio
* `ai/`: contém a lógica de comunicação com a API da Groq e autenticação no GitHub
* `github/`: contém a lógica de autenticação e requisições no GitHub