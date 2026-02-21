import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import base64

# --- KONFIGURATION ---
st.set_page_config(page_title="Klempner-Regelwerk OCR", layout="wide")

# (Dein bisheriges Design bleibt gleich...)
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: #d4af37; }
    div.stButton > button { background-color: #8c7851; color: white; border: 2px solid #d4af37; border-radius: 10px; height: 3em; width: 100%; }
    div.stButton > button:hover { background-color: #d4af37; color: black; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_pdf():
    return fitz.open("Gesamtordner.pdf")

# NEU: Diese Funktion "liest" das Bild der Seite
def get_text_via_ocr(page):
    # Seite als Bild (Pixmap) rendern
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Höhere Auflösung für bessere Erkennung
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    # OCR ausführen
    text = pytesseract.image_to_string(img, lang='deu')
    return text

doc = load_pdf()

st.title("⚒️ Fachregeln Klempnertechnik (OCR-Modus)")

if doc:
    col_nav, col_view = st.columns([1, 2])
    
    with col_nav:
        st.subheader("Kapitel")
        # Hier deine Kapitel-Buttons...
        if st.button("3. Werkstoffe"): st.session_state.page = 13
        if st.button("4. Klempnerarbeiten"): st.session_state.page = 28
        
        st.info("Hinweis: Da die PDF geschützt ist, nutzt die App Texterkennung (OCR). Das Laden einer Seite kann 1-2 Sekunden dauern.")

    with col_view:
        if "page" in st.session_state:
            p_num = st.session_state.page
            page = doc[p_num-1]
            
            with st.spinner('Lese Seite fachmännisch ein...'):
                # Hier erzwingen wir das "Lesen" des Bildes
                extracted_text = get_text_via_ocr(page)
            
            st.subheader(f"📖 Ausgelesener Text (Seite {p_num})")
            st.text_area("Inhalt:", extracted_text, height=300)
            
            # PDF Anzeige
            with open("Gesamtordner.pdf", "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={p_num}" width="100%" height="600"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
