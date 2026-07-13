# app.py
# Interfaccia chat Streamlit per il chatbot RAG dello studio legale Braga & Damiati

import streamlit as st
from dotenv import load_dotenv
from rag import costruisci_indice, genera_risposta

load_dotenv()

# --- Colori del brand Braga & Damiati ---
BLU_SCURO = "#142145"
ARANCIONE = "#EA650B"
SFONDO = "#F5ECE9"

st.set_page_config(
    page_title="Braga & Damiati Advogados",
    page_icon="assets/logo.png",
    layout="centered",
)

# --- CSS personalizzato con i colori del brand ---
st.markdown(f"""
<style>
    /* Bolha do usuário: fundo azul-marinho, texto branco */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: {BLU_SCURO};
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {{
        color: white !important;
    }}

    /* Bolha do assistente: fundo branco, texto azul-marinho */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        background-color: white;
        border: 1px solid {ARANCIONE}55;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {{
        color: {BLU_SCURO} !important;
    }}

    /* Fontes citadas, em laranja e negrito */
    [data-testid="stCaptionContainer"] {{
        color: {ARANCIONE} !important;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

# --- Intestazione con logo ---
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo.png", width="stretch")
with col2:
    st.markdown(f"""
        <div style="display: flex; align-items: center; height: 100%;">
            <p style="color: {BLU_SCURO}; font-size: 0.95rem; margin: 0;">
                Assistente virtuale per la raccolta di informazioni preliminari.
                Non fornisce consulenza legale.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.divider()


@st.cache_resource
def carica_indice():
    """Costruisce l'indice RAG una sola volta e lo mantiene in cache
    per tutta la durata della sessione dell'app."""
    with st.spinner("Indicizzazione dei documenti in corso..."):
        return costruisci_indice()


indice = carica_indice()

if "messaggi" not in st.session_state:
    st.session_state.messaggi = []

for msg in st.session_state.messaggi:
    with st.chat_message(msg["ruolo"]):
        st.markdown(msg["testo"])

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