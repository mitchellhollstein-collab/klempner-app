import streamlit as st
import fitz  # PyMuPDF
import base64

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Klempner Fachregeln", layout="wide")

# --- MODERNES DESIGN (ANTHRAZIT & BRONZE) ---
st.markdown("""
<style>
    .stApp { background-color: #2b2b2b; color: #d4af37; }
    div.stButton > button {
        background-color: #8c7851; color: white;
        border: 2px solid #d4af37; border-radius: 12px;
        height: 3.5em; width: 100%; font-weight: bold; font-size: 16px;
    }
    div.stButton > button:hover { background-color: #d4af37; color: black; border: 2px solid white; }
    .stTextInput > div > div > input { background-color: #3d3d3d; color: white; border: 1px solid #8c7851; }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- PDF LADE-FUNKTION ---
@st.cache_resource
def load_pdf():
    try:
        # WICHTIG: Dateiname muss EXAKT stimmen (Groß/Kleinschreibung)
        return fitz.open("Gesamtordner.pdf")
    except Exception as e:
        return f"Fehler: Datei 'Gesamtordner.pdf' nicht gefunden. ({e})"

doc = load_pdf()

# --- APP STRUKTUR ---
st.title("⚒️ Digitales Regelwerk Klempnertechnik")

if isinstance(doc, str):
    st.error(doc)
    st.info("💡 Tipp: Prüfe, ob die PDF auf GitHub wirklich 'Gesamtordner.pdf' heißt.")
else:
    # Inhaltsverzeichnis basierend auf deiner PDF
    toc = {
        "1. Geltungsbereich": 7,
        "2. Begriffe": 10,
        "3. Werkstoffe": 13,
        "4. Allg. Klempnerarbeiten": 28,
        "5. Metalldächer": 77,
        "6. Windlasten": 93,
        "12. Fassadenbekleidungen": 145,
        "13. Anhang / Tabellen": 168
    }

    col_nav, col_view = st.columns([1, 2])

    with col_nav:
        st.subheader("Navigation")
        search_query = st.text_input("🔍 PDF durchsuchen...")
        
        # Suchfunktion
        if search_query:
            st.write("Suchergebnisse:")
            count = 0
            for i in range(len(doc)):
                if search_query.lower() in doc[i].get_text().lower():
                    if st.button(f"Seite {i+1}", key=f"search_{i}"):
                        st.session_state.page = i + 1
                    count += 1
                    if count > 10: break # Max 10 Ergebnisse anzeigen
            if count == 0: st.warning("Nichts gefunden.")
        
        st.markdown("---")
        for title, pg in toc.items():
            if st.button(title):
                st.session_state.page = pg

    with col_view:
        if "page" in st.session_state:
            p_num = st.session_state.page
            
            # Klartext auslesen
            st.subheader("📖 Text-Ansicht")
            page_content = doc[p_num-1].get_text("text")
            if page_content.strip():
                st.text_area("Inhalt:", page_content, height=250)
            else:
                st.warning("Kein direkter Text auf dieser Seite (evtl. Grafik). Siehe PDF unten.")
            
            # PDF Einbetten
            st.subheader("📄 Original PDF")
            with open("Gesamtordner.pdf", "rb") as f:
                base_64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base_64_pdf}#page={p_num}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info("Wähle links ein Kapitel aus, um den Text und das Original zu sehen.")
