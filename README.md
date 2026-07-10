# Chatbot Studio Legale

Assistente virtuale di pre-consulto per uno studio legale, basato su FastAPI e Google Gemini API.

## Cosa fa

Raccoglie in modo cortese le informazioni preliminari di un potenziale cliente (dati di contatto, area del diritto, breve descrizione dei fatti, eventuali scadenze urgenti) prima di un consulto con un avvocato. Non fornisce mai pareri legali.

## Requisiti

- Docker e Docker Compose
- Una chiave API Gemini (gratuita su [Google AI Studio](https://aistudio.google.com/apikey)), con billing collegato al progetto Google Cloud (obbligatorio per utenti nell'Unione Europea)

## Come avviarlo

1. Clona il repository:
```bash
   git clone <URL_DEL_TUO_REPO>
   cd studio-legale-chatbot
```

2. Crea un file `.env` nella cartella principale con la tua chiave:

3. Avvia tutto con un solo comando:
```bash
   docker compose up
```

4. Apri il browser su [http://localhost:8000/docs](http://localhost:8000/docs) per provare l'API tramite l'interfaccia Swagger.

## Endpoint disponibili

- `GET /` — stato del servizio
- `POST /chat` — invia un messaggio al chatbot

  Corpo della richiesta:
```json
  {
    "testo": "Buongiorno, vorrei un consulto per una questione di eredità",
    "id_conversazione": null
  }
```

  La `id_conversazione` è opzionale al primo messaggio: il server ne genera una e la restituisce nella risposta. Va poi riutilizzata nei messaggi successivi per mantenere il contesto della conversazione.

## Modello utilizzato

`gemini-3.1-flash-lite` — scelto per il buon equilibrio tra costo e qualità per conversazioni semplici di raccolta dati.

## Note

- La cronologia delle conversazioni è mantenuta in memoria: si perde se il container viene riavviato. Per un uso in produzione andrebbe sostituita con un database.
- Il chatbot non sostituisce una consulenza legale reale.