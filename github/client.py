"""
github/client.py
================
Responsabilidade: autenticação e requisições base para a API do GitHub.
Todos os outros módulos github/ importam daqui — nunca de core/config diretamente.
"""

import httpx
from core.config import GITHUB_HEADERS, GITHUB_API

# Cache do username para não buscar a cada chamada
_username_cache: str = ""


async def get(endpoint: str, **kwargs) -> dict | list:
    """GET autenticado na API do GitHub."""
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{GITHUB_API}{endpoint}", headers=GITHUB_HEADERS, **kwargs)
        r.raise_for_status()
        return r.json()


async def post(endpoint: str, json: dict) -> dict:
    """POST autenticado na API do GitHub."""
    async with httpx.AsyncClient() as http:
        r = await http.post(f"{GITHUB_API}{endpoint}", headers=GITHUB_HEADERS, json=json)
        r.raise_for_status()
        return r.json()


async def patch(endpoint: str, json: dict) -> dict:
    """PATCH autenticado na API do GitHub (usado para fechar issues, etc.)."""
    async with httpx.AsyncClient() as http:
        r = await http.patch(f"{GITHUB_API}{endpoint}", headers=GITHUB_HEADERS, json=json)
        r.raise_for_status()
        return r.json()


async def put(endpoint: str, json: dict) -> dict:
    """PUT autenticado na API do GitHub (usado para commits)."""
    async with httpx.AsyncClient() as http:
        r = await http.put(f"{GITHUB_API}{endpoint}", headers=GITHUB_HEADERS, json=json)
        r.raise_for_status()
        return r.json()


async def get_usuario() -> str:
    """Retorna o username autenticado (com cache para não repetir a requisição)."""
    global _username_cache
    if not _username_cache:
        data = await get("/user")
        _username_cache = data["login"]
    return _username_cache
