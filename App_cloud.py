import os
import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAZIONE LINK E CONNESSIONE CLOUD
# ==========================================
# ⚠️ SOSTITUISCI QUESTO LINK CON IL TUO LINK REALE DEL FOGLIO GOOGLE
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y-tABOUcIIwxD7W9zNcg22uKjr-bHxlKziJim3S-n1I/edit?usp=sharing"

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

cartella_script = os.path.dirname(os.path.abspath(__file__))
percorso_credenziali = os.path.join(cartella_script, "credentials.json")

if not os.path.exists(percorso_credenziali):
    percorso_credenziali = os.path.join(cartella_script, "credentials.json.txt")

sheet = None

# --- METODO DI CONNESSIONE NATIVO E PROTETTO ---
client = None

# 1. Tentativo in Cloud (Metodo ufficiale Streamlit)
if "gcp_service_account" in st.secrets:
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Errore nella lettura dei Secrets Cloud: {e}")

# 2. Tentativo in Locale (Sul tuo PC)
elif os.path.exists(percorso_credenziali):
    creds = Credentials.from_service_account_file(percorso_credenziali, scopes=scope)
    client = gspread.authorize(creds)

# Se entrambi falliscono, blocca l'app con istruzioni chiare
if client is None:
    st.error("❌ Errore di Connessione: Credenziali non configurate correttamente.")
    st.info("Se sei online, assicurati che il box 'Secrets' sia compilato esattamente come mostrato nella guida.")
    st.stop()

# --- DEFINIZIONE ESPLICITA DELLE SCHEDE ---
try:
    spreadsheet = client.open_by_url(SHEET_URL)
    sheet_players = spreadsheet.worksheet("Players") # Scheda principale
    sheet_TGH_db = spreadsheet.worksheet("TGH_db") # Scheda secondaria
except Exception as e:
    st.error(f"Impossibile accedere alle schede del foglio: {e}")
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

lista_position = ["GK", "LB", "CB", "RB", "LM", "CM", "CDM", "RM", "LW", "CAM", "RW", "CF", "ST"]

lista_formation = ["3-5-2", "3-4-1-2", "3-4-3", "4-3-2-1", "4-2-3-1", "4-1-4-1", "4-3-1-2", "4-4-2", "4-2-1-3", "4-3-3", "4-2-4"]

lista_scout = ["Lattuada Giacomo"]

lista_competition_grezza = sheet_TGH_db.col_values(1)
clean_competition = [v.strip() for v in lista_competition_grezza[1:] if v.strip() != ""]
lista_competition = sorted(list(set(clean_competition)))

lista_team_grezza = sheet_TGH_db.col_values(3)
clean_team = [v.strip() for v in lista_team_grezza[1:] if v.strip() != ""]
lista_team = sorted(list(set(clean_team)))

lista_loan_grezza = sheet_TGH_db.col_values(4)
clean_loan = [v.strip() for v in lista_loan_grezza[1:] if v.strip() != ""]
lista_loan = sorted(list(set(clean_loan)))

# ==========================================
# 3. INTERFACCIA GRAFICA STRUTTURATA
# ==========================================
st.set_page_config(page_title="Gestionale Calciatori", layout="wide")
st.title("👤 Player Report")

st.markdown("---")

st.subheader("📁 Player information")
col_anagrafica1, col_anagrafica2, col_anagrafica3 = st.columns(3)

with col_anagrafica1:
    name = st.text_input("1. Name:")
    surname = st.text_input("2. Surname:")
with col_anagrafica2:
    year_birth = st.selectbox("3. Birth:", lista_anni)
with col_anagrafica3:
    nation = st.selectbox("4. Nation:", lista_nazioni)

st.markdown("---")

st.subheader("⚡ Characteristic")
col_caratt1, col_caratt2, col_caratt3 = st.columns(3)

with col_caratt1:
    position = st.selectbox("5. Position:", lista_position)
    alt_position = st.selectbox("6. Alt. Position:", lista_position)
    formation = st.selectbox("7. Formation:", lista_formation)

with col_caratt2:
    foot = st.radio("8. Foot:", ["L", "R", "L/R"])
    
    st.write("")
    st.write("**8. Competition:**")
    new_competition = st.checkbox("Inserisci un nuovo valore non in elenco",key="chk_competition")  # 2. Checkbox per decidere se inserire un nuovo valore o sceglierlo dalla lista
    if new_competition:
        competition = st.text_input("Digita il nuovo valore:",key="txt_competition")    # Campo di testo libero per digitare un dato inedito
    else:
        competition = st.selectbox("Seleziona dai suggerimenti:", lista_competition,key="sel_competition")    # Menu a tendina che filtra e suggerisce i valori già presenti nel foglio Google
    group = st.text_input("9. Group:")
    
    st.write("")
with col_caratt3:
    st.write("**10. Team:**")
    new_team = st.checkbox("Inserisci un nuovo valore non in elenco",key="chk_team")    # 2. Checkbox per decidere se inserire un nuovo valore o sceglierlo dalla lista
    if new_team:
        team = st.text_input("Digita il nuovo valore:",key="txt_team")    # Campo di testo libero per digitare un dato inedito
    else:
        team = st.selectbox("Seleziona dai suggerimenti:", lista_team,key="sel_team")    # Menu a tendina che filtra e suggerisce i valori già presenti nel foglio Google

    st.write("")
    st.write("**11. On loan from:**")
    new_loan = st.checkbox("Inserisci un nuovo valore non in elenco",key="chk_loan")    # 2. Checkbox per decidere se inserire un nuovo valore o sceglierlo dalla lista
    if new_loan:
        loan = st.text_input("Digita il nuovo valore:",key="txt_loan")    # Campo di testo libero per digitare un dato inedito
    else:
        loan = st.selectbox("Seleziona dai suggerimenti:", lista_loan,key="sel_loan")    # Menu a tendina che filtra e suggerisce i valori già presenti nel foglio Google

    # SONO ARRIVATO QUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    
st.markdown("---")

st.subheader("🔭 Scounting Context")
col_caratt1, col_caratt2, col_caratt3 = st.columns(3)

with col_caratt1:
		partita_osservata = st.text_input("14. Partita osservata:")
		minuti_giocati = st.radio("15. Minuti giocati:", ["<45'", ">45'", "Match completo"])

with col_caratt2:
		data_report = st.date_input("16. Data compilazione:", value=datetime.date.today())
		tipologia_scouting = st.radio("17. Tipologia scounting:", ["Live", "Video"])

with col_caratt3:
		nome_scout = st.selectbox("18. Nome Scout:", lista_scout, index = 0)

st.markdown("---")

st.subheader("🤸 Phisical Profile")
col_caratt1, col_caratt2, col_caratt3 = st.columns(3)
with col_caratt1:
    height = st.radio("19. Height:", ["≤170cm'", "≥171cm, ≤177cm", "≥178cm, ≤183cm", "≥184cm, ≤188cm", "≥189"])
    muscolature = st.radio("20. Muscolature:", ["Lean", "Athletic", "Massive"])
    matrice_physical_build = {
    "≤170cm": {
        "Lean": "Short, lean build",
        "Athletic": "Short, well-balanced build",
        "Massive": "Short, powerful build"
    },
    "≥171cm, ≤177cm": {
        "Lean": "Short, lean build",
        "Athletic": "Short, well-balanced build",
        "Massive": "Short, powerful build"
    },
    "≥178cm, ≤183cm": {
        "Lean": "Medium-height, lean build",
        "Athletic": "Medium-height, well-balanced build",
        "Massive": "Medium-height, powerful build"
    },
    "≥184cm, ≤188cm": {
        "Lean": "Average-height, lean build",
        "Athletic": "Average-height, well-balanced build",
        "Massive": "Average-height, powerful build"
    },
    "≥189": {
        "Lean": "Tall, lean build",
        "Athletic": "Tall, well-balanced build",
        "Massive": "Tall, powerful build"
    }
}
    physical_build = matrice_physical_build.get(height, {}).get(muscolature, "Non definito")
    st.info(f"🧬 Physical build: **{physical_build}**")



# DA AGGIUNGERE IN SEZOINE (SALVATAGGIO) - DA AGGIUNGERE IN GOOGLESHEET

# ==========================================
# 4. LOGICA DI SALVATAGGIO MATEMATICA E ID
# ==========================================
st.markdown("---")
if st.button("💾 Salva Scheda Giocatore", type="primary", use_container_width=True):
    if name.strip() == "" or surname.strip() == "":
        st.error("I campi '1. Nome' e '2. Cognome' sono entrambi obbligatori per salvare la scheda.")
    else:
        valore_prima_squadra = "1a squadra" if chk_prima_squadra else ""
        valore_giovanili = "Giovanili" if chk_giovanili else ""
        if new_competition and competition.strip() != "":
            if competition.strip() not in lista_competition:
                sheet_TGH_db.append_row([competition.strip()])
        if new_team and team.strip() != "":
            if team.strip() not in lista_team:
                sheet_TGH_db.append_row(["", "", team.strip()])
        if new_loan and loan.strip() != "":
            if loan.strip() not in lista_loan:
                sheet_TGH_db.append_row(["", "", loan.strip()])

        with st.spinner("Calcolo riga libera e generazione ID..."):
            valori_esistenti = sheet_players.get_all_values()
            prossima_riga = len(valori_esistenti) + 1
            data_reportITA = data_report.strftime("%d/%m/%Y")
            if prossima_riga == 2:
                nuovo_id = 1
            else:
                try:
                    nuovo_id = int(valori_esistenti[-1][0]) + 1
                except ValueError:
                    nuovo_id = prossima_riga - 1


            # Costruzione riga (Variabili corrette al 100%)
            nuova_riga = [
                nuovo_id,
                name.strip(),
                surname.strip(),
                year_birth,
                nation,
                position,
                alt_position,
                formation,
                foot,
                competition,
                group,
                team,
                loan,

                
                partita_osservata,
                minuti_giocati,
                tipologia_scouting,
                data_reportITA,
                tipologia_scouting,
                nome_scout
            ]

            sheet_players.insert_row(nuova_riga, index=prossima_riga, value_input_option='RAW')
            st.success(f"✔️ Assegnato ID {nuovo_id}: Scheda di '{nome_cognome}' salvata con successo!")

# ==========================================
# 5. ANTEPRIMA DEL DATABASE ONLINE
# ==========================================
st.markdown("---")
st.subheader("📊 Vista Tabella Cloud (Sincronizzata)")
try:
    dati_cloud = sheet_players.get_all_records()
    if dati_cloud:
        df_visualizzazione = pd.DataFrame(dati_cloud)
        st.dataframe(df_visualizzazione, use_container_width=True)
    else:
        st.info("Il database è vuoto. Inserisci il primo giocatore per vedere la tabella.")
except Exception:
    st.info("Inserisci il primo record per inizializzare la visualizzazione della tabella.")
