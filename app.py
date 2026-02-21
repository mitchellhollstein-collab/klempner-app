import streamlit as st
import fitz  # PyMuPDF
import base64

# --- SEITENKONFIGURATION ---
st.set_page_config(page_title="Klempner Fachregeln", layout="wide")

# --- DESIGN (Anthrazit & Bronze) ---
st.markdown("""
<style>
    .stApp { background-color: #2b2b2b; color: #e0e0e0; }
    div.stButton > button {
        background-color: #8c7851; color: white;
        border: 2px solid #d4af37; border-radius: 10px;
        height: 3.5em; width: 100%; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #d4af37; color: #1e1e1e; }
    .stTextInput > div > div > input { background-color: #3d3d3d; color: white; border: 1px solid #8c7851; }
</style>
""", unsafe_allow_html=True)

# --- PDF FUNKTIONEN ---
@st.cache_resource
def open_pdf():
    return fitz.open("Gesamtordner.pdf")

def display_pdf(file_path, page):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- APP LOGIK ---
doc = open_pdf()

st.title("⚒️ Digitales Regelwerk Klempnertechnik")

# Sidebar Suche
st.sidebar.header("🔍 Suche")
search_term = st.sidebar.text_input("Begriff suchen...")

# Navigation (Beispiel-Struktur nach deinem Dokument)
menu = {
    "Werkstoffe": 12,
    "Dachentwässerung": 28,
    "Metalldächer": 45,
    "Fassaden": 70
}

col_nav, col_main = st.columns([1, 2])

with col_nav:
    st.subheader("Kapitel")
    for label, page in menu.items():
        if st.button(label):
            st.session_state.page = page
            st.session_state.title = label

with col_main:
    if search_term:
        st.subheader("Suchergebnisse")
        for i in range(len(doc)):
            if search_term.lower() in doc[i].get_text().lower():
                if st.button(f"Gefunden auf Seite {i+1}", key=f"res_{i}"):
                    st.session_state.page = i + 1
                    st.session_state.title = f"Suchtreffer: {search_term}"

    if "page" in st.session_state:
        st.header(st.session_state.title)
        # Klartext-Extraktion
        with st.expander("Klartext anzeigen", expanded=True):
            text = doc[st.session_state.page - 1].get_text()
            st.write(text if text.strip() else "Diese Seite enthält hauptsächlich Grafiken.")
        
        # Original PDF
        st.subheader("Original Beleg")

        display_pdf("Gesamtordner.pdf", st.session_state.page)
        # Funktion zum sicheren Auslesen
def get_clean_text(doc, page_num):
    try:
        # Seite laden (Index beginnt bei 0)
        page = doc.load_page(page_num - 1)
        
        # Verschiedene Extraktionsmethoden probieren
        text = page.get_text("text")
        
        if not text.strip():
            # Falls kein Text kommt, versuchen wir es über Blöcke
            blocks = page.get_text("blocks")
            text = "\n".join([b[4] for b in blocks if isinstance(b[4], str)])
            
        return text if text.strip() else "Kein lesbarer Text auf dieser Seite gefunden."
    except Exception as e:
        return f"Fehler beim Lesen der Seite: {e}"

# In der App-Ansicht dann:
if "current_page" in st.session_state:
    st.subheader("📖 Klartext der Seite")
    inhalt = get_clean_text(doc, st.session_state.current_page)
    
    # Text in einem schöneren Feld mit Scrollbalken anzeigen
    st.text_area(label="Inhalt:", value=inhalt, height=300)
    search_term = st.sidebar.text_input("🔍 Suchbegriff eingeben")
if search_term:
    found_pages = []
    # Wir suchen in allen Seiten
    for i in range(len(doc)):
        if search_term.lower() in doc[i].get_text().lower():
            found_pages.append(i + 1)
    
    if found_pages:
        st.sidebar.success(f"{len(found_pages)} Treffer gefunden:")
        for p in found_pages[:15]: # Zeige die ersten 15 Treffer
            if st.sidebar.button(f"Seite {p} öffnen", key=f"p_{p}"):
                st.session_state.current_page = p
    else:
        st.sidebar.warning("Keine Treffer.")
