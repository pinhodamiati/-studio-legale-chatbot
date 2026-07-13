# Dockerfile
# Immagine per il chatbot RAG dello studio legale (Streamlit + Gemini API)

FROM python:3.12-slim

WORKDIR /app

# Copiamo prima requirements.txt per sfruttare la cache di Docker:
# se cambia solo il codice, questo layer non viene ricostruito
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ora copiamo il resto: codice sorgente E la cartella documenti/
# (la base di conoscenza deve essere dentro l'immagine per funzionare online)
COPY . .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/_stcore/health')" || exit 1

# Avvia Streamlit sulla porta 8080, accessibile da fuori il container
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]