
"""
voice/listener.py
=================
Responsabilidade: capturar áudio do microfone e converter em texto.
"""

import speech_recognition as sr
from core.config import PAUSE_THRESHOLD, ENERGY_THRESHOLD

recognizer = sr.Recognizer()
recognizer.pause_threshold         = PAUSE_THRESHOLD
recognizer.energy_threshold        = ENERGY_THRESHOLD
recognizer.dynamic_energy_threshold = True


def warmup_reconhecedor():
    """Calibra o microfone uma vez na inicialização para reduzir latência inicial."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("✅ Microfone calibrado.")
    except Exception as e:
        print(f"⚠️  Calibração do microfone falhou: {e}")


def ouvir() -> str | None:
    """Escuta o microfone e retorna o texto reconhecido, ou None se não ouvir nada."""
    with sr.Microphone() as source:
        print("\n🎤 Ouvindo...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=30)
            print("⏳ Reconhecendo...")
            texto = recognizer.recognize_google(audio, language="pt-BR")
            print(f"👤 Você: {texto}")
            return texto
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"❌ Erro no microfone: {e}")
            return None


def monitorar_interrupcao(esta_falando_ref) -> bool:
    """
    Escuta por palavras de interrupção enquanto a SAKURÁ fala.
    Retorna True se o usuário pediu para parar.
    """
    palavras_chave = ["para", "chega", "cancela", "cala", "silêncio", "stop"]
    with sr.Microphone() as source:
        while esta_falando_ref():
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                texto = recognizer.recognize_google(audio, language="pt-BR").lower()
                if any(p in texto for p in palavras_chave):
                    return True
            except Exception:
                pass
    return False
