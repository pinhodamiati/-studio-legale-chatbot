# list_models.py
# Lista i modelli effettivamente disponibili per la tua chiave API,
# e quelli che supportano generateContent (necessario per il chatbot)

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Modelli disponibili che supportano generateContent:\n")
for modello in client.models.list():
    azioni = getattr(modello, "supported_actions", None) or []
    if "generateContent" in azioni:
        print(f"- {modello.name}")