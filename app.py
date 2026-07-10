# app.py
# API del chatbot di pre-consulto per lo studio legale
# Usa il nuovo SDK unificato google-genai (google.generativeai è deprecato)

import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
NOME_MODELLO = "gemini-3.1-flash-lite"

# Istruzioni di sistema: definiscono il comportamento del chatbot
ISTRUZIONI_SISTEMA = """
Sei l'assistente virtuale di pre-consulto dello Studio Legale [NOME STUDIO].
Il tuo compito è raccogliere in modo cortese e professionale le informazioni
necessarie prima di un consulto con un avvocato reale. Devi:

1. Chiedere il nome e un recapito (email o telefono) del visitatore.
2. Chiedere l'area del diritto interessata (es. civile, penale, lavoro, famiglia,
   condominio, tributario).
3. Chiedere una breve descrizione dei fatti, senza entrare in valutazioni tecniche.
4. Chiedere se ci sono scadenze urgenti (es. termini legali imminenti).
5. NON fornire MAI pareri legali, previsioni sull'esito di una causa o consigli
   su cosa fare. Se il visitatore chiede un parere, rispondi che solo un
   avvocato del team può valutare il caso in un consulto dedicato.
6. Mantieni un tono professionale, empatico e rassicurante.
7. Alla fine, riepiloga le informazioni raccolte e invita a fissare un consulto.
"""

CONFIG = types.GenerateContentConfig(system_instruction=ISTRUZIONI_SISTEMA)

app = FastAPI(title="Chatbot Studio Legale")

# Memoria delle conversazioni in corso (solo per demo: in produzione usare un DB)
conversazioni: dict[str, list] = {}


class MessaggioInput(BaseModel):
    testo: str
    id_conversazione: str | None = None


class MessaggioOutput(BaseModel):
    risposta: str
    id_conversazione: str


@app.get("/")
def stato():
    """Endpoint di verifica dello stato del servizio."""
    return {"stato": "attivo", "servizio": "chatbot-studio-legale"}


@app.post("/chat", response_model=MessaggioOutput)
def chatta(msg: MessaggioInput):
    """Riceve un messaggio dell'utente e restituisce la risposta del chatbot,
    mantenendo la cronologia della conversazione."""

    id_conv = msg.id_conversazione or str(uuid.uuid4())

    # Recupera o crea la cronologia della conversazione (lista di Content)
    cronologia = conversazioni.setdefault(id_conv, [])

    # Aggiunge il messaggio dell'utente alla cronologia
    cronologia.append(types.Content(role="user", parts=[types.Part(text=msg.testo)]))

    risposta = client.models.generate_content(
        model=NOME_MODELLO,
        contents=cronologia,
        config=CONFIG,
    )

    # Aggiunge la risposta del modello alla cronologia, per mantenere il contesto
    cronologia.append(types.Content(role="model", parts=[types.Part(text=risposta.text)]))

    return MessaggioOutput(risposta=risposta.text, id_conversazione=id_conv)