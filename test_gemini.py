# test_gemini.py
# Script di verifica: controlla che la chiave API di Gemini funzioni correttamente
# Usa il nuovo SDK unificato google-genai (google.generativeai è deprecato)

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Il client legge automaticamente GEMINI_API_KEY dall'ambiente,
# ma la passiamo esplicitamente per chiarezza
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

risposta = client.models.generate_content(
    model="gemini-3.1-flash-lite"
    contents="Rispondi in italiano: sei pronto ad aiutare i clienti di uno studio legale?"
)

print(risposta.text)