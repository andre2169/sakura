# 🌸 SAKURÁ — Assistente de Voz com IA

SAKURÁ é uma assistente de voz pessoal desenvolvida em Python, capaz de ouvir comandos, responder com voz natural e integrar com o GitHub via API.

## ✨ Funcionalidades

- 🎤 **Reconhecimento de voz** em português brasileiro
- 🔊 **Síntese de voz neural** com edge-tts (vozes Microsoft)
- 🧠 **Memória persistente** entre sessões via SQLite
- 📍 **Localização automática** por IP para respostas contextualizadas
- 🐙 **Integração com GitHub:**
  - Listar repositórios
  - Criar repositórios (público ou privado)
  - Listar, criar e fechar issues
  - Fazer commits de arquivos
  - Gerar README automático com IA

## 🗂️ Estrutura do Projeto

```
sakura/
├── main.py              # Entry point
├── core/
│   ├── config.py        # Variáveis de ambiente
│   ├── loop.py          # Loop principal
│   └── localizacao.py   # Detecção de localização por IP
├── voice/
│   ├── listener.py      # Captura e reconhecimento de voz
│   └── speaker.py       # Síntese e reprodução de áudio
├── ai/
│   └── groq_client.py   # Comunicação com a API da Groq
├── github/
│   ├── client.py        # Requisições base para a API do GitHub
│   ├── repos.py         # Listar e criar repositórios
│   ├── issues.py        # Gerenciar issues
│   ├── commits.py       # Commits de arquivos
│   ├── readme.py        # Geração de README com IA
│   └── router.py        # Roteamento de comandos de voz
└── memory/
    ├── repository.py    # Interface genérica de memória
    └── sqlite.py        # Implementação com SQLite
```

## 🚀 Como Instalar

```bash
# Clone o repositório
git clone https://github.com/andre2169/sakura.git
cd sakura

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Se o pyaudio falhar no Windows:
pip install pyaudio --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_aqui
GITHUB_TOKEN=seu_token_aqui
```

- **GROQ_API_KEY:** Obtenha em [console.groq.com](https://console.groq.com)
- **GITHUB_TOKEN:** Gere em GitHub → Settings → Developer settings → Personal access tokens (permissões: `repo` e `read:user`)

## ▶️ Como Usar

```bash
python main.py
```

### Exemplos de comandos de voz

| O que dizer | O que acontece |
|---|---|
| *"mostra meus repositórios"* | Lista todos os repos do GitHub |
| *"cria um repositório chamado meu-projeto"* | Cria novo repositório público |
| *"cria um repositório chamado segredo privado"* | Cria repositório privado |
| *"issues do repo meu-projeto"* | Lista issues abertas |
| *"criar issue no repo X com título Y"* | Abre nova issue |
| *"fechar issue número 3 no repo X"* | Fecha a issue |
| *"gerar readme do repo X"* | Gera README com IA e commita |
| *"limpar memória"* | Apaga o histórico de conversas |
| *"encerrar"* | Encerra a assistente |

## 🛠️ Tecnologias

- [Groq](https://groq.com) — LLM (llama-3.1-8b-instant)
- [edge-tts](https://github.com/rany2/edge-tts) — Síntese de voz neural
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) — Reconhecimento de voz
- [pygame](https://www.pygame.org) — Reprodução de áudio
- [httpx](https://www.python-httpx.org) — Requisições HTTP assíncronas
- [SQLite](https://www.sqlite.org) — Banco de dados local para memória persistente

## 📄 Licença

MIT
