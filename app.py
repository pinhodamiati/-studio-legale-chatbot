# app.py
# Interfaccia chat Streamlit per il chatbot RAG dello studio legale

import streamlit as st
from dotenv import load_dotenv
from rag import costruisci_indice, genera_risposta

load_dotenv()

st.set_page_config(page_title="Assistente Studio Legale", page_icon="⚖️")
st.title("⚖️ Assistente Studio Legale")
st.caption("Assistente didattico basato sui documenti dello studio. Non fornisce consulenza legale.")


@st.cache_resource
def carica_indice():
    """Costruisce l'indice RAG una sola volta e lo mantiene in cache
    per tutta la durata della sessione dell'app."""
    with st.spinner("Indicizzazione dei documenti in corso..."):
        return costruisci_indice()


indice = carica_indice()

# La cronologia dei messaggi vive nello stato di sessione di Streamlit,
# così sopravvive tra un messaggio e l'altro nella stessa sessione utente
if "messaggi" not in st.session_state:
    st.session_state.messaggi = []

# Mostra i messaggi precedenti
for msg in st.session_state.messaggi:
    with st.chat_message(msg["ruolo"]):
        st.markdown(msg["testo"])

# Campo di input per la domanda dell'utente
domanda = st.chat_input("Fai una domanda sui documenti dello studio...")

if domanda:
    st.session_state.messaggi.append({"ruolo": "user", "testo": domanda})
    with st.chat_message("user"):
        st.markdown(domanda)

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando nei documenti..."):
            risultato = genera_risposta(domanda, indice, k=3)
            st.markdown(risultato["risposta"])
            if risultato["fonti"]:
                st.caption(f"Fonti: {', '.join(risultato['fonti'])}")

    st.session_state.messaggi.append({"ruolo": "assistant", "testo": risultato["risposta"]})