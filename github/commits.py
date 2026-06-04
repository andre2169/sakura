"""
github/commits.py
=================
Responsabilidade: criar ou atualizar arquivos via commit direto na API do GitHub.

Como funciona:
  A API do GitHub permite criar/atualizar um arquivo num repo via PUT em
  /repos/{user}/{repo}/contents/{path}. O conteúdo precisa estar em base64.
  Se o arquivo já existir, é obrigatório passar o SHA do arquivo atual.
"""

import base64
from github.client import get, put, get_usuario


async def commit_arquivo(
    repo: str,
    caminho_arquivo: str,
    conteudo: str,
    mensagem_commit: str,
    branch: str = "main",
) -> str:
    """
    Cria ou atualiza um arquivo num repositório via commit.

    Args:
        repo:             Nome do repositório (ex: "sakura-assistente")
        caminho_arquivo:  Caminho do arquivo no repo (ex: "src/utils.py")
        conteudo:         Conteúdo do arquivo em texto puro
        mensagem_commit:  Mensagem do commit
        branch:           Branch de destino (padrão: main)
    """
    try:
        usuario = await get_usuario()
        endpoint = f"/repos/{usuario}/{repo}/contents/{caminho_arquivo}"

        # Converte conteúdo para base64 (exigido pela API)
        conteudo_b64 = base64.b64encode(conteudo.encode("utf-8")).decode("utf-8")

        payload: dict = {
            "message": mensagem_commit,
            "content": conteudo_b64,
            "branch": branch,
        }

        # Se o arquivo já existir, precisa do SHA para atualizar
        try:
            arquivo_atual = await get(endpoint)
            payload["sha"] = arquivo_atual["sha"]
            acao = "atualizado"
        except Exception:
            acao = "criado"   # Arquivo não existe ainda — cria do zero

        data = await put(endpoint, payload)
        nome_arquivo = data["content"]["name"]
        return (
            f"Arquivo {nome_arquivo} {acao} com sucesso no repositório {repo}. "
            f"Commit: {mensagem_commit}."
        )
    except Exception as e:
        return f"Não consegui fazer o commit. Erro: {e}"
