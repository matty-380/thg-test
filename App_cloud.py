import os
import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAZIONE LINK E CONNESSIONE CLOUD
# ==========================================
# ⚠️ RICORDATI DI SOSTITUIRE QUESTO LINK CON QUELLO DEL TUO FOGLIO GOOGLE
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y-tABOUcIIwxD7W9zNcg22uKjr-bHxlKziJim3S-n1I/edit?usp=sharing"

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Prepariamo i percorsi locali per il tuo PC
cartella_script = os.path.dirname(os.path.abspath(__file__))
percorso_credenziali = os.path.join(cartella_script, "credentials.json")

if not os.path.exists(percorso_credenziali):
    percorso_credenziali = os.path.join(cartella_script, "credentials.json.txt")


# --- NUOVA LOGICA IBRIDA DI SICUREZZA BLINDATA ---
sheet = None

# Mossa 1: Controlliamo PRIMA se siamo sul tuo PC (se c'è il file credentials.json)
if os.path.exists(percorso_credenziali):
    creds = Credentials.from_service_account_file(percorso_credenziali, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEET_URL).sheet1
else:
    # Mossa 2: Se il file locale NON esiste, allora siamo online in Cloud.
    # Usiamo un "try" per evitare il crash nel caso in cui st.secrets sia vuoto
    try:
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_url(SHEET_URL).sheet1
    except Exception:
        sheet = None

# Se alla fine di tutti i controlli non siamo riusciti a collegarci, mostriamo l'errore
if sheet is None:
    st.error("Errore di Sicurezza: Credenziali non trovate! Controlla che il file 'credentials.json' sia sul Desktop accanto al file del codice.")
    st.stop()


# ==========================================
# 2. LOGICA DATI E RANGE DINAMICI
# ==========================================
anno_attuale = datetime.date.today().year
anno_inizio = anno_attuale - 40
anno_fine = anno_attuale - 10
lista_anni = list(range(anno_fine, anno_inizio - 1, -1))

lista_nazioni = [
    "Italia", "Albania", "Argentina", "Belgio", "Brasile", "Croazia", "Francia", 
    "Germania", "Inghilterra", "Marocco", "Olanda", "Portogallo", "Romania", 
    "Senegal", "Serbia", "Spagna", "Svizzera", "Ucraina", "Uruguay", "Altra"
]

lista_ruoli = ["POR", "TS", "ASA", "ES", "DC", "TD", "ADA", "ED", "MED", "CC", "COC", "AS", "AD", "SP", "P", "NESSUNA"]

lista_moduli = ["3-5-2", "3-4-1-2", "3-4-3", "4-3-2-1", "4-2-3-1", "4-1-4-1", "4-3-1-2", "4-4-2", "4-2-1-3", "4-3-3", "4-2-4"]

# ==========================================
# 3. INTERFACCIA GRAFICA STRUTTURATA
# ==========================================
st.set_page_config(page_title="Gestionale Calciatori", layout="wide")
st.title("⚽ Sistema Censimento Calciatori")

st.header("👤 Informazioni giocatore")
st.markdown("---")

st.subheader("📁 Anagrafica e Contesto Attuale")
col_anagrafica1, col_anagrafica2, col_anagrafica3 = st.columns(3)

with col_anagrafica1:
    nome_cognome = st.text_input("1. Nome e Cognome:")
with col_anagrafica2:
    anno_nascita = st.selectbox("2. Anno di nascita:", lista_anni)
with col_anagrafica3:
    nazionalita = st.selectbox("3. Nazionalità:", lista_nazioni)

st.markdown("---")

st.subheader("⚡ Caratteristiche")
col_caratt1, col_caratt2, col_caratt3 = st.columns(3)

with col_caratt1:
    posizione_naturale = st.selectbox("4. Posizione Naturale:", lista_ruoli)
    
    posizione_naturale2 = ""
    if posizione_naturale == "MED":
        posizione_naturale2 = st.selectbox("5. Posizione Naturale2:", ["MED a 1", "MED a 2", "Indifferente"])
    elif posizione_naturale == "CC":
        posizione_naturale2 = st.selectbox("5. Posizione Naturale2:", ["CS", "CD", "Indifferente"])
    elif posizione_naturale in ["AS", "AD"]:
        posizione_naturale2 = st.selectbox("5. Posizione Naturale2:", ["Piede Invertito", "Piede Naturale", "Indifferente"])
    elif posizione_naturale == "P":
        posizione_naturale2 = st.selectbox("5. Posizione Naturale2:", ["P a 1", "P a 2", "Indifferente"])
    else:
        st.text_input("5. Posizione Naturale2:", value="Nessuna specifica richiesta", disabled=True)

    posizione_secondaria = st.selectbox("6. Posizione secondaria:", lista_ruoli)
    modulo_attuale = st.selectbox("7. Modulo attuale d'impiego:", lista_moduli)

with col_caratt2:
    piede_preferito = st.radio("8. Piede preferito:", ["Dx", "Sx", "Entrambi"])
    st.write("") 
    st.write("**Status Squadra:**")
    chk_prima_squadra = st.checkbox("9. Prima squadra")
    chk_giovanili = st.checkbox("10. Giovanili")

with col_caratt3:
    campionato_attuale = st.text_input("11. Campionato attuale:")
    girone_attuale = st.text_input("12. Girone attuale:")
    club_attuale = st.text_input("13. Club attuale:")

# ==========================================
# 4. LOGICA DI SALVATAGGIO ORDINATA (1-13)
# ==========================================
st.markdown("---")
if st.button("💾 Salva Scheda Giocatore", type="primary", use_container_width=True):
    if nome_cognome.strip() == "":
        st.error("Il campo '1. Nome e Cognome' è obbligatorio per salvare la scheda.")
    else:
        valore_prima_squadra = "1a squadra" if chk_prima_squadra else ""
        valore_giovanili = "Giovanili" if chk_giovanili else ""
        
        nuova_riga = [
            nome_cognome,          # 1
            anno_nascita,          # 2
            nazionalita,           # 3
            posizione_naturale,    # 4
            posizione_naturale2,   # 5
            posizione_secondaria,  # 6
            modulo_attuale,        # 7
            piede_preferito,       # 8
            valore_prima_squadra,  # 9
            valore_giovanili,      # 10
            campionato_attuale,    # 11
            girone_attuale,        # 12
            club_attuale           # 13
        ]
        
        with st.spinner("Scrittura nel database cloud in corso..."):
            sheet.append_row(nuova_riga)
            st.success(f"✔️ Scheda di '{nome_cognome}' salvata correttamente in cloud!")

# ==========================================
# 5. ANTEPRIMA DEL DATABASE ONLINE
# ==========================================
st.markdown("---")
st.subheader("📊 Vista Tabella Cloud (Sincronizzata)")
dati_cloud = sheet.get_all_records()
if dati_cloud:
    df_visualizzazione = pd.DataFrame(dati_cloud)
    st.dataframe(df_visualizzazione, use_container_width=True)
else:
    st.info("Il database è vuoto. Inserisci il primo giocatore per vedere la tabella.")
