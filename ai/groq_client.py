"""
ai/groq_client.py
=================
Responsabilidade: comunicação com a API da Groq.
Mantém histórico de conversa com memória deslizante.
"""

from datetime import datetime
from groq import Groq
from core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)
historico_conversa: list = []

MODELO          = "llama-3.1-8b-instant"
MAX_TOKENS      = 200
MAX_HISTORICO   = 21   # system + 10 trocas (20 mensagens)


def gerar_resposta(texto_usuario: str, loc_texto: str = "Localização não disponível.") -> str:
    """
    Envia o histórico completo para a Groq e retorna a resposta em texto.
    Injeta hora atual e localização no system prompt na primeira mensagem.
    """
    global historico_conversa

    if not historico_conversa:
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
        historico_conversa.append({"role": "system", "content": prompt_sistema})

    historico_conversa.append({"role": "user", "content": texto_usuario})

    try:
        resposta = client.chat.completions.create(
            messages=historico_conversa,
            model=MODELO,
            temperature=0.7,
            max_tokens=MAX_TOKENS,
        )
        texto_resposta = resposta.choices[0].message.content
        historico_conversa.append({"role": "assistant", "content": texto_resposta})

        # Memória deslizante: descarta trocas antigas mantendo o system prompt
        if len(historico_conversa) > MAX_HISTORICO:
            historico_conversa.pop(1)
            historico_conversa.pop(1)

        return texto_resposta

    except Exception as e:
        print(f"❌ Erro na Groq: {e}")
        historico_conversa.pop()
        return "Desculpe, tive um problema de conexão. Pode repetir?"
