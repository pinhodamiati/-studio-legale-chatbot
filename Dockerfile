# Dockerfile
# Immagine per il chatbot dello studio legale (FastAPI + Gemini API)

# Partiamo da un'immagine "slim": più leggera della versione completa,
# perché non ci servono compilatori o librerie grafiche per questo progetto
FROM python:3.12-slim

# Cartella di lavoro dentro il container
WORKDIR /app

# Copiamo PRIMA solo requirements.txt: se il codice cambia ma le
# dipendenze no, Docker riusa la cache di questo layer ed evita
# di reinstallare tutto ad ogni build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ora copiamo il resto del codice
COPY . .

# Documenta la porta usata dall'app (non la pubblica da sola,
# serve solo come informazione)
EXPOSE 8000

# Verifica periodicamente se il servizio risponde correttamente
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Avvia il server all'avvio del container
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]