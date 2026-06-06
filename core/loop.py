"""
core/loop.py
============
Loop principal da SAKURÁ.
Responsabilidade: orquestrar escuta → roteamento → resposta.
"""

import asyncio
import pygame

from core.config import validar_config
from voice.listener import ouvir, warmup_reconhecedor
from voice.speaker import falar
from ai.groq_client import gerar_resposta
from github.router import processar_comando_github
from core.localizacao import buscar_localizacao, formatar_localizacao
import memory.repository as memoria

dados_localizacao: dict = {}
PALAVRAS_SAIDA = ["tchau", "desligar", "encerrar", "sair"]


async def loop_principal():
    global dados_localizacao

    validar_config()
    pygame.mixer.init()

    # ── Inicializa o banco de dados ───────────────────────────────────────────
    memoria.inicializar()

    print("🌸 Iniciando SAKURÁ...")

    dados_localizacao, _ = await asyncio.gather(
        buscar_localizacao(),
        asyncio.to_thread(warmup_reconhecedor)
    )

    loc_texto = formatar_localizacao(dados_localizacao)
    await falar("Olá, eu sou a SAKURÁ! Estou pronta para te ajudar.")

    while True:
        texto_usuario = await asyncio.to_thread(ouvir)

        if not texto_usuario:
            continue

        if any(p in texto_usuario.lower() for p in PALAVRAS_SAIDA):
            await falar("Foi um prazer ajudar! Até logo.")
            break

        # Comando especial: limpar memória
        if any(p in texto_usuario.lower() for p in ["limpar memória", "limpar memoria",
                                                      "apagar memória", "apagar memoria",
                                                      "esquecer tudo", "resetar memória"]):
            memoria.limpar_historico()
            await falar("Pronto, apaguei toda a minha memória. Podemos começar do zero!")
            continue

        resposta_github = await processar_comando_github(texto_usuario)
        if resposta_github:
            await falar(resposta_github)
            continue

        resposta = await asyncio.to_thread(gerar_resposta, texto_usuario, loc_texto)
        await falar(resposta)
