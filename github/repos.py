"""
github/repos.py
===============
Responsabilidade: listar e criar repositórios.
"""

from github.client import get, post, get_usuario


async def listar_repos() -> str:
    """Lista os repositórios mais recentes do usuário autenticado."""
    try:
        repos = await get("/user/repos?sort=updated&per_page=10")
        if not repos:
            return "Você não tem nenhum repositório ainda."
        nomes = [
            f"{r['name']} ({'privado' if r['private'] else 'público'})"
            for r in repos
        ]
        return f"Você tem {len(nomes)} repositórios: {', '.join(nomes)}."
    except Exception as e:
        return f"Não consegui listar os repositórios. Erro: {e}"


async def criar_repo(nome: str, privado: bool = False, descricao: str = "") -> str:
    """Cria um repositório novo com README inicial."""
    try:
        data = await post("/user/repos", {
            "name": nome,
            "private": privado,
            "description": descricao,
            "auto_init": True,   # cria com README para o repo não ficar vazio
        })
        visibilidade = "privado" if privado else "público"
        return (
            f"Repositório {data['name']} criado com sucesso! "
            f"Ele é {visibilidade}. "
            f"Acesse em: {data['html_url']}"
        )
    except Exception as e:
        return f"Não consegui criar o repositório. Erro: {e}"
