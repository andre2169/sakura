"""
core/localizacao.py
===================
Detecta cidade/estado/país pelo IP público.
API: ip-api.com — gratuita, sem chave, 45 req/min.
"""

import httpx


async def buscar_localizacao() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5) as http:
            r = await http.get(
                "http://ip-api.com/json/?lang=pt-BR&fields=status,city,regionName,country,lat,lon"
            )
            data = r.json()
            if data.get("status") == "success":
                print(f"📍 Localização: {data['city']}, {data['regionName']}, {data['country']}")
                return data
    except Exception as e:
        print(f"⚠️  Localização indisponível: {e}")
    return {}


def formatar_localizacao(loc: dict) -> str:
    if not loc:
        return "Localização não disponível."
    return (
        f"Cidade: {loc.get('city', '?')}, "
        f"Estado: {loc.get('regionName', '?')}, "
        f"País: {loc.get('country', '?')}."
    )
