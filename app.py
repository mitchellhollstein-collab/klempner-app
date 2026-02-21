import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import base64

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Klempner-Regelwerk Profi", layout="wide")

# --- DESIGN (Anthrazit & Bronze) ---
def apply_style():
    st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #d4af37; }
    div.stButton > button {
        background-color: #8c7851; color: white;
        border: 2px solid #d4af37; border-radius: 12px;
        height: 3.5em; width: 100%; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #d4af37; color: black; border: 2px solid white; }
    .stTextInput > div > div > input { background-color: #2d2d2d; color: white; border: 1px solid #8c7851; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKTIONEN ---
@st.cache_resource
def load_pdf():
    try:
        return fitz.open("Gesamtordner.pdf")
    except Exception as e:
        return None

def get_ocr_text(page):
    # Erhöht die Auflösung für bessere Texterkennung
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang='deu')

# --- HAUPT-APP ---
def main():
    apply_style()
    doc = load_pdf()
    
    if doc is None:
        st.error("Datei 'Gesamtordner.pdf' nicht gefunden. Bitte auf GitHub hochladen!")
        return

    st.title("⚒️ Regelwerk Klempnertechnik")

    # Inhaltsverzeichnis nach der PDF-Struktur
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

    # SIDEBAR: SUCHE
    st.sidebar.header("🔍 Suche")
    search_query = st.sidebar.text_input("Begriff eingeben...", placeholder="z.B. Kupfer")
    
    if search_query:
        if st.sidebar.button("Suche in PDF starten"):
            st.sidebar.write("Suche läuft...")
            # Suche in den ersten 150 Seiten (Performance-Schutz)
            found_pages = []
            for i in range(len(doc)):
                # Schnelle Suche in Textebene
                text = doc[i].get_text().lower()
                if search_query.lower() in text:
                    found_pages.append(i + 1)
                if len(found_pages) >= 5: break
            
            if found_pages:
                for p in found_pages:
                    if st.sidebar.button(f"Gefunden auf Seite {p}", key=f"s_{p}"):
                        st.session_state.page = p
            else:
                st.sidebar.warning("Kein Treffer in der Textebene.")

    # NAVIGATION & ANZEIGE
    col_nav, col_view = st.columns([1, 2.5])

    with col_nav:
        st.subheader("Kapitel")
        for title, pg in toc.items():
            if st.button(title):
                st.session_state.page = pg
                st.session_state.title = title

    with col_view:
        if "page" in st.session_state:
            p_num = st.session_state.page
            st.header(st.session_state.get("title", f"Seite {p_num}"))
            
            # Klartext via OCR
            with st.expander("📖 KLARTEXT LESEN", expanded=True):
                with st.spinner("Analysiere Seite..."):
                    inhalt = get_ocr_text(doc[p_num-1])
                st.text_area("Inhalt:", inhalt, height=300)
            
            # Original PDF
            st.subheader("📄 ORIGINAL BELEG")
            with open("Gesamtordner.pdf", "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={p_num}" width="100%" height="800"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info("Wählen Sie links ein Kapitel aus.")

if __name__ == "__main__":
    main()
