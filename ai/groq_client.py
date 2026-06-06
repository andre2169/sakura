"""
ai/groq_client.py
=================
Responsabilidade: comunicação com a API da Groq.
Usa a camada memory/repository.py para memória persistente.
Envia para a Groq apenas: system prompt + últimas 10 mensagens (contexto seguro).
"""

from datetime import datetime
from groq import Groq
from core.config import GROQ_API_KEY
import memory.repository as memoria

client = Groq(api_key=GROQ_API_KEY)

MODELO        = "llama-3.1-8b-instant"
MAX_TOKENS    = 200
JANELA_CONTEXTO = 10  # Mensagens recentes enviadas para a Groq (user + assistant)


def gerar_resposta(texto_usuario: str, loc_texto: str = "Localização não disponível.") -> str:
    """
    Gera uma resposta da Groq com memória persistente.

    Fluxo:
      1. Se não há system prompt no banco, cria e salva um novo.
      2. Salva a mensagem do usuário no banco.
      3. Monta o contexto: system + últimas JANELA_CONTEXTO mensagens.
      4. Envia para a Groq e salva a resposta no banco.
    """

    # ── 1. System prompt ──────────────────────────────────────────────────────
    system_salvo = memoria.carregar_system_prompt()

    if not system_salvo:
        hora_atual = datetime.now().strftime("%H:%M")
        prompt_sistema = f"""
Você é SAKURÁ, uma assistente de voz inteligente e simpática, especializada em ajudar com estudos e tarefas do dia a dia.
Quando o usuário mencionar GitHub, repositórios, issues ou PRs, avise que pode ajudar com isso.

Contexto atual:
- Hora: {hora_atual}
- Localização do usuário: {loc_texto}

Use a localização para personalizar respostas quando relevante.
Dê respostas diretas e curtas (máximo 3 frases) pois serão lidas em voz alta.
NUNCA use asteriscos, hashtags, emojis ou formatação markdown.
""".strip()
        memoria.salvar_mensagem("system", prompt_sistema)
        system_prompt = {"role": "system", "content": prompt_sistema}
    else:
        system_prompt = system_salvo

    # ── 2. Salva a mensagem do usuário ────────────────────────────────────────
    memoria.salvar_mensagem("user", texto_usuario)

    # ── 3. Monta contexto seguro: system + últimas N mensagens ────────────────
    historico_recente = memoria.carregar_historico(limite=JANELA_CONTEXTO)
    mensagens_para_groq = [system_prompt] + historico_recente

    # ── 4. Chama a Groq ───────────────────────────────────────────────────────
    try:
        resposta = client.chat.completions.create(
            messages=mensagens_para_groq,
            model=MODELO,
            temperature=0.7,
            max_tokens=MAX_TOKENS,
        )
        texto_resposta = resposta.choices[0].message.content

        # Salva a resposta no banco
        memoria.salvar_mensagem("assistant", texto_resposta)

        return texto_resposta

    except Exception as e:
        print(f"❌ Erro na Groq: {e}")
        # Remove a mensagem do usuário que acabou de ser salva para não poluir o histórico
        return "Desculpe, tive um problema de conexão. Pode repetir?"
