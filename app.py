import streamlit as st
import fitz  # PyMuPDF
import base64

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Klempner Profi-App", layout="wide")

# --- DESIGN (Anthrazit & Bronze) ---
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: #d4af37; }
    div.stButton > button {
        background-color: #8c7851; color: white;
        border: 2px solid #d4af37; border-radius: 10px;
        height: 3.5em; width: 100%; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #d4af37; color: black; }
    .stTextInput > div > div > input { background-color: #2d2d2d; color: white; border: 1px solid #8c7851; }
    /* Textbereich besser lesbar machen */
    textarea { color: #ffffff !important; background-color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_pdf():
    try:
        return fitz.open("Gesamtordner.pdf")
    except Exception as e:
        st.error(f"Datei nicht gefunden: {e}")
        return None

doc = load_pdf()

# --- HILFSFUNKTION FÜR TEXT-EXTRAKTION ---
def get_text_robust(page):
    # Methode 1: Standard Text
    text = page.get_text("text")
    # Methode 2: Falls Methode 1 leer, versuche Blöcke (hilft bei spezieller Kodierung)
    if not text.strip():
        blocks = page.get_text("blocks")
        text = "\n".join([b[4] for b in blocks if len(b) > 4])
    return text

st.title("⚒️ Fachregeln Klempnertechnik")

if doc:
    # Inhaltsverzeichnis
    toc = {
        "1. Geltungsbereich": 7,
        "2. Begriffe": 10,
        "3. Werkstoffe": 13,
        "4. Allg. Klempnerarbeiten": 28,
        "5. Metalldächer": 77,
        "12. Fassaden": 145
    }

    col_nav, col_view = st.columns([1, 2])

    with col_nav:
        st.subheader("Suche")
        query = st.text_input("Stichwort eingeben...")
        
        if query:
            st.write("Ergebnisse:")
            found = False
            for i in range(len(doc)):
                # Wir nutzen hier die robuste Textsuche
                page_text = get_text_robust(doc[i])
                if query.lower() in page_text.lower():
                    if st.button(f"Gefunden auf Seite {i+1}", key=f"s_{i}"):
                        st.session_state.page = i + 1
                    found = True
                    if i > 50: # Begrenzung damit App schnell bleibt
                        break
            if not found:
                st.warning("Kein Text gefunden. Versuchen Sie ein anderes Wort.")

        st.markdown("---")
        st.subheader("Kapitel")
        for title, pg in toc.items():
            if st.button(title):
                st.session_state.page = pg

    with col_view:
        if "page" in st.session_state:
            p_idx = st.session_state.page - 1
            page = doc[p_idx]
            
            # TEXT ANZEIGEN
            st.subheader(f"📖 Textinhalt Seite {st.session_state.page}")
            extracted_text = get_text_robust(page)
            
            if extracted_text.strip():
                st.text_area("Klartext:", extracted_text, height=300)
            else:
                st.error("Klartext-Extraktion fehlgeschlagen. Die PDF ist intern möglicherweise als Grafik geschützt.")
            
            # PDF ANZEIGEN
            st.subheader("📄 Original Beleg")
            with open("Gesamtordner.pdf", "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={st.session_state.page}" width="100%" height="800"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
