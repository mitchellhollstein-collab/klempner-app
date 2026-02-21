import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import base64

# --- KONFIGURATION & DESIGN ---
st.set_page_config(page_title="Klempner Fachregeln Digital", layout="wide")

def apply_design():
    st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #d4af37; }
    /* Große Bronze Buttons */
    div.stButton > button {
        background-color: #8c7851; color: white;
        border: 2px solid #d4af37; border-radius: 12px;
        height: 3.5em; width: 100%; font-size: 16px; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #d4af37; color: black; border: 2px solid white; }
    .stTextInput > div > div > input { background-color: #2d2d2d; color: white; border: 1px solid #8c7851; }
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #262626; border-right: 1px solid #8c7851; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKTIONEN ---
@st.cache_resource
def load_pdf():
    return fitz.open("Gesamtordner.pdf")

def get_ocr_text(page):
    # Seite als Bild für OCR vorbereiten
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang='deu')

def display_pdf_frame(page_num):
    with open("Gesamtordner.pdf", "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_num}" width="100%" height="800"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- HAUPTPROGRAMM ---
def main():
    apply_design()
    doc = load_pdf()
    
    st.title("⚒️ Fachportal Klempnertechnik")

    # ECHTES INHALTSVERZEICHNIS (Kapitel & Seitenzahlen aus deiner PDF)
    toc = {
        "1. Geltungsbereich": 7,
        "2. Begriffe": 10,
        "3. Werkstoffe": 13,
        "4. Allg. Klempnerarbeiten": 28,
        "5. Metalldächer": 77,
        "6. Windlasten": 93,
        "7. Ausführung Metalldächer": 107,
        "8. Dachneigung / Überdeckung": 111,
        "9. Doppelstehfalzdeckung": 115,
        "10. Leistendeckung": 132,
        "11. Bauteile auf Metalldächern": 138,
        "12. Fassadenbekleidungen": 145,
        "13. Anhang / Tabellen": 168
    }

    # SIDEBAR: SUCHFUNKTION
    st.sidebar.header("🔍 Intelligente Suche")
  search_query = st.sidebar.text_input("Stichwort suchen...", placeholder="z.B. Kupfer, Dachrinne")

