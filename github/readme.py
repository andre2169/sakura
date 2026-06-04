"""
github/readme.py
================
Responsabilidade: gerar um README.md com IA baseado no código do repositório.

Fluxo:
  1. Busca a lista de arquivos do repo via API
  2. Baixa o conteúdo dos arquivos de código principais (até um limite de tokens)
  3. Envia para a Groq gerar um README profissional
  4. Faz commit do README.md gerado no repositório
"""

import base64
from groq import Groq
from core.config import GROQ_API_KEY
from github.client import get, get_usuario
from github.commits import commit_arquivo

client_groq = Groq(api_key=GROQ_API_KEY)

# Extensões de código que valem a pena ler para gerar o README
EXTENSOES_CODIGO = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".cpp", ".c"}
MAX_CHARS_POR_ARQUIVO = 2000   # Limite por arquivo para não estourar o contexto
MAX_ARQUIVOS          = 8      # Máximo de arquivos lidos


async def _listar_arquivos_repo(usuario: str, repo: str) -> list[dict]:
    """Retorna a árvore de arquivos do repositório (nível raiz)."""
    try:
        return await get(f"/repos/{usuario}/{repo}/contents")
    except Exception:
        return []


async def _ler_arquivo(usuario: str, repo: str, caminho: str) -> str:
    """Lê e decodifica o conteúdo de um arquivo do repo."""
    try:
        data = await get(f"/repos/{usuario}/{repo}/contents/{caminho}")
        conteudo_b64 = data.get("content", "")
        # A API retorna com quebras de linha no base64
        return base64.b64decode(conteudo_b64.replace("\n", "")).decode("utf-8", errors="ignore")
    except Exception:
        return ""


async def gerar_readme(repo: str) -> str:
    """
    Gera e commita um README.md para o repositório baseado no código encontrado.
    """
    try:
        usuario = await get_usuario()
        arquivos = await _listar_arquivos_repo(usuario, repo)

        if not arquivos:
            return f"Não consegui acessar os arquivos do repositório {repo}."

        # Filtra apenas arquivos de código
        arquivos_codigo = [
            f for f in arquivos
            if f.get("type") == "file"
            and any(f["name"].endswith(ext) for ext in EXTENSOES_CODIGO)
        ][:MAX_ARQUIVOS]

        if not arquivos_codigo:
            return f"Não encontrei arquivos de código no repositório {repo} para gerar o README."

        # Monta o contexto com o código
        contexto = ""
        for arq in arquivos_codigo:
            conteudo = await _ler_arquivo(usuario, repo, arq["path"])
            if conteudo:
                trecho = conteudo[:MAX_CHARS_POR_ARQUIVO]
                contexto += f"\n\n### Arquivo: {arq['name']}\n```\n{trecho}\n```"

        # Pede para a Groq gerar o README
        prompt = f"""
Analise o código abaixo do repositório "{repo}" e gere um README.md profissional em português.

O README deve conter:
- Nome e descrição do projeto
- Funcionalidades principais
- Tecnologias usadas
- Como instalar e rodar
- Como usar
- Estrutura do projeto (se relevante)

Responda APENAS com o conteúdo do README em Markdown, sem explicações adicionais.

{contexto}
""".strip()

        resposta = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.4,
            max_tokens=1500,
        )

        readme_conteudo = resposta.choices[0].message.content

        # Commita o README no repositório
        resultado_commit = await commit_arquivo(
            repo=repo,
            caminho_arquivo="README.md",
            conteudo=readme_conteudo,
            mensagem_commit="docs: README gerado automaticamente pela SAKURÁ",
        )

        return (
            f"README gerado com sucesso para o repositório {repo}! "
            f"Analisei {len(arquivos_codigo)} arquivos de código. "
            f"{resultado_commit}"
        )

    except Exception as e:
        return f"Não consegui gerar o README. Erro: {e}"
