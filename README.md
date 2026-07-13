# Chatbot RAG — Studio Legale

Assistente conversazionale che risponde a domande sui documenti dello studio legale, usando la tecnica RAG (Retrieval-Augmented Generation) con Google Gemini.

## Cosa fa

Indicizza i documenti presenti nella cartella `documenti/` (file .txt e .pdf), e risponde alle domande dell'utente citando sempre la fonte. Se l'informazione non è presente nei documenti, lo dichiara esplicitamente. Non fornisce consulenza legale.

## Requisiti

- Docker e Docker Compose
- Una chiave API Gemini gratuita ([Google AI Studio](https://aistudio.google.com/apikey)), con billing collegato al progetto Google Cloud (obbligatorio per utenti nell'Unione Europea)

## Come avviarlo

1. Clona il repository:
```bash
   git clone <URL_DEL_TUO_REPO>
   cd studio-legale-chatbot
```

2. Crea un file `.env` con la tua chiave:

3. Avvia con Docker Compose:
```bash
   docker compose up
```

4. Apri [http://localhost:8080](http://localhost:8080)

## Esempio di domanda/risposta

**Domanda:** "Il consumatore ha diritto a un indennizzo per un disservizio nel volo?"

**Risposta:** L'assistente risponde citando i passaggi rilevanti trovati nei documenti di giurisprudenza indicizzati, specificando il file di origine (es. `jurisprudencia_decolar(3).pdf`), e segnala quando il documento non riporta l'esito finale di un caso.

## Architettura (pipeline RAG)

1. **Chunking** — i documenti vengono spezzati in blocchi di ~100 parole con sovrapposizione, per preservare il contesto alle giunzioni.
2. **Embedding** — ogni chunk viene trasformato in un vettore numerico (`gemini-embedding-001`).
3. **Retrieval** — data una domanda, si calcola il suo embedding e si recuperano i k chunk più simili tramite similarità del coseno.
4. **Generazione** — i chunk recuperati vengono inseriti nel prompt come contesto; Gemini (`gemini-3.1-flash-lite`) genera una risposta vincolata a quel contesto, citando le fonti.

## Note

- L'indice viene ricostruito ad ogni avvio dell'app (nessuna persistenza tra riavvii) — per una base di conoscenza più grande, si consiglia un database vettoriale dedicato (es. Chroma, FAISS).
- I PDF scansionati senza livello di testo non vengono indicizzati (richiederebbero OCR).
- Assistente didattico: non sostituisce una consulenza legale professionale.