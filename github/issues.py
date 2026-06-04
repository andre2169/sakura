"""
github/issues.py
================
Responsabilidade: listar, criar e fechar issues.
"""

from github.client import get, post, patch, get_usuario


async def listar_issues(repo: str) -> str:
    """Lista as issues abertas de um repositório."""
    try:
        usuario = await get_usuario()
        issues = await get(f"/repos/{usuario}/{repo}/issues?state=open&per_page=5")
        if not issues:
            return f"Nenhuma issue aberta no repositório {repo}."
        lista = [f"número {i['number']}: {i['title']}" for i in issues]
        return f"Issues abertas em {repo}: {', '.join(lista)}."
    except Exception as e:
        return f"Não consegui buscar as issues. Erro: {e}"


async def criar_issue(repo: str, titulo: str, corpo: str = "") -> str:
    """Cria uma nova issue em um repositório."""
    try:
        usuario = await get_usuario()
        data = await post(f"/repos/{usuario}/{repo}/issues", {
            "title": titulo,
            "body": corpo,
        })
        return (
            f"Issue criada com sucesso no repositório {repo}! "
            f"É a número {data['number']}: {data['title']}."
        )
    except Exception as e:
        return f"Não consegui criar a issue. Erro: {e}"


async def fechar_issue(repo: str, numero: int) -> str:
    """Fecha uma issue pelo número."""
    try:
        usuario = await get_usuario()
        data = await patch(f"/repos/{usuario}/{repo}/issues/{numero}", {
            "state": "closed"
        })
        return f"Issue número {data['number']} fechada com sucesso no repositório {repo}."
    except Exception as e:
        return f"Não consegui fechar a issue. Erro: {e}"
