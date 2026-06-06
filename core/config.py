"""
core/config.py
==============
Carrega todas as variáveis de ambiente e expõe constantes globais.
Importado por todos os outros módulos — NUNCA importa de outros módulos do projeto.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# ── GitHub ────────────────────────────────────────────────────────────────────
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
GITHUB_HEADERS: dict = (
    {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN else {}
)
GITHUB_API = "https://api.github.com"

# ── Voz ───────────────────────────────────────────────────────────────────────
VOZ_BRASILEIRA   = "pt-BR-FranciscaNeural"   # Alternativa: pt-BR-AntonioNeural
VOZ_VELOCIDADE   = "+10%"                    # Taxa de fala do edge-tts

# ── Reconhecimento ────────────────────────────────────────────────────────────
PAUSE_THRESHOLD  = 1.5
ENERGY_THRESHOLD = 300

# ── Validação na inicialização ────────────────────────────────────────────────
def validar_config():
    erros = []
    if not GROQ_API_KEY:
        erros.append("GROQ_API_KEY não encontrada no .env")
    if not GITHUB_TOKEN:
        print("⚠️  GITHUB_TOKEN não encontrado — funções do GitHub desativadas.")
    if erros:
        for e in erros:
            print(f"❌ {e}")
        raise SystemExit(1)
