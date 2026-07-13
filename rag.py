# rag.py
# Modulo RAG: caricamento documenti, chunking, embedding, retrieval, generazione

import os
from pathlib import Path
from pypdf import PdfReader
from google import genai
from google.genai import types
import numpy as np
from dotenv import load_dotenv
load_dotenv()

CARTELLA_DOCUMENTI = "documenti"
DIMENSIONE_CHUNK = 100  # numero di parole per chunk
SOVRAPPOSIZIONE = 20    # parole condivise tra un chunk e il successivo


def carica_documenti(cartella: str = CARTELLA_DOCUMENTI) -> list[dict]:
    """Carica tutti i file .txt e .pdf dalla cartella, restituendo una
    lista di dizionari con il nome del file (fonte) e il testo completo."""
    documenti = []
    for percorso in Path(cartella).glob("*"):
        if percorso.suffix == ".txt":
            testo = percorso.read_text(encoding="utf-8")
            documenti.append({"fonte": percorso.name, "testo": testo})

        elif percorso.suffix == ".pdf":
            lettore = PdfReader(percorso)
            testo = "\n".join(pagina.extract_text() or "" for pagina in lettore.pages)
            if testo.strip():
                documenti.append({"fonte": percorso.name, "testo": testo})
            else:
                print(f"Attenzione: nessun testo estraibile da {percorso.name} "
                      f"(probabilmente un PDF scansionato/immagine, senza OCR)")

    return documenti


def spezza_in_chunk(testo: str, dimensione: int = DIMENSIONE_CHUNK,
                     sovrapposizione: int = SOVRAPPOSIZIONE) -> list[str]:
    """Divide un testo in chunk di 'dimensione' parole, con una
    sovrapposizione tra chunk consecutivi per non perdere contesto
    alle giunzioni."""
    parole = testo.split()
    chunk = []
    inizio = 0
    while inizio < len(parole):
        fine = inizio + dimensione
        chunk.append(" ".join(parole[inizio:fine]))
        inizio += dimensione - sovrapposizione
    return chunk


def prepara_chunk_con_fonte() -> list[dict]:
    """Carica tutti i documenti e li spezza in chunk, mantenendo
    traccia della fonte di ciascun chunk."""
    documenti = carica_documenti()
    tutti_i_chunk = []
    for doc in documenti:
        for pezzo in spezza_in_chunk(doc["testo"]):
            tutti_i_chunk.append({"testo": pezzo, "fonte": doc["fonte"]})
    return tutti_i_chunk

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELLO_EMBEDDING = "gemini-embedding-001"


def calcola_embedding(testo: str) -> list[float]:
    """Trasforma un testo in un vettore numerico (embedding) tramite Gemini."""
    risposta = client.models.embed_content(
        model=MODELLO_EMBEDDING,
        contents=testo,
    )
    return risposta.embeddings[0].values


def costruisci_indice() -> list[dict]:
    """Costruisce l'indice completo: per ogni chunk, calcola il suo
    embedding e lo memorizza insieme al testo e alla fonte."""
    chunk = prepara_chunk_con_fonte()
    indice = []
    for c in chunk:
        vettore = calcola_embedding(c["testo"])
        indice.append({
            "testo": c["testo"],
            "fonte": c["fonte"],
            "vettore": np.array(vettore),
        })
    return indice

def similarita_coseno(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calcola la similarità del coseno tra due vettori: un valore tra
    -1 e 1, dove 1 significa 'stesso significato', 0 significa
    'nessuna relazione'."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def recupera_passaggi_rilevanti(domanda: str, indice: list[dict], k: int = 3) -> list[dict]:
    """Data una domanda, restituisce i k chunk dell'indice più simili
    per significato, ordinati dal più al meno rilevante."""
    vettore_domanda = np.array(calcola_embedding(domanda))

    risultati = []
    for elemento in indice:
        punteggio = similarita_coseno(vettore_domanda, elemento["vettore"])
        risultati.append({
            "testo": elemento["testo"],
            "fonte": elemento["fonte"],
            "punteggio": punteggio,
        })

    risultati.sort(key=lambda r: r["punteggio"], reverse=True)
    return risultati[:k]

NOME_MODELLO_CHAT = "gemini-3.1-flash-lite"

ISTRUZIONI_RAG = """
Sei un assistente che risponde a domande basandosi ESCLUSIVAMENTE sui
passaggi di contesto forniti qui sotto, estratti da documenti reali.

Regole obbligatorie:
1. Rispondi solo con informazioni presenti nel contesto. Non inventare
   nulla e non usare conoscenze esterne.
2. Cita sempre la fonte (il nome del file) da cui hai preso l'informazione.
3. Se il contesto non contiene la risposta alla domanda, dillo chiaramente:
   "Non ho trovato questa informazione nei documenti disponibili."
4. Non fornire consulenza legale: presenta i fatti contenuti nei
   documenti, non un parere personale.
"""


def costruisci_prompt(domanda: str, passaggi: list[dict]) -> str:
    """Costruisce il prompt aumentato unendo i passaggi recuperati e
    la domanda dell'utente."""
    contesto = "\n\n".join(
        f"[Fonte: {p['fonte']}]\n{p['testo']}"
        for p in passaggi
    )
    return f"""Contesto:
{contesto}

Domanda: {domanda}

Rispondi seguendo rigorosamente le istruzioni di sistema."""


def genera_risposta(domanda: str, indice: list[dict], k: int = 3) -> dict:
    """Esegue l'intero flusso RAG: recupera i passaggi rilevanti,
    costruisce il prompt e genera la risposta con Gemini."""
    passaggi = recupera_passaggi_rilevanti(domanda, indice, k=k)
    prompt = costruisci_prompt(domanda, passaggi)

    risposta = client.models.generate_content(
        model=NOME_MODELLO_CHAT,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=ISTRUZIONI_RAG),
    )

    return {
        "risposta": risposta.text,
        "fonti": list({p["fonte"] for p in passaggi}),  # fonti uniche
        "passaggi_usati": passaggi,
    }

if __name__ == "__main__":
    indice = costruisci_indice()
    print(f"Indice costruito con {len(indice)} elementi.\n")

    domanda_test = "O consumidor tem direito a indenização por falha na prestação do serviço da Decolar?"
    risultato = genera_risposta(domanda_test, indice, k=3)

    print(f"Domanda: {domanda_test}\n")
    print(f"Risposta:\n{risultato['risposta']}\n")
    print(f"Fonti citate: {risultato['fonti']}")
