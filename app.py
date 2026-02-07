import streamlit as st
from google import genai
from google.genai import types # Needed for image processing
import os
from fpdf import FPDF
from PIL import Image

# --- 1. CONFIGURATION & CALLBACKS ---
st.set_page_config(page_title="Kritikos Guard | Pro Developer Hub", layout="wide")

def reset_writing_ally():
    st.session_state['writing_input'] = ""
    if 'report_grammar' in st.session_state:
        st.session_state['report_grammar'] = ""

# --- 2. API KEY SETUP (Restoring your automatic setup) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    st.warning("Please provide an API key to continue.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 3. MAIN INTERFACE ---
st.title("🛡️ Smart Developer Toolkit")
tab_security, tab_grammar = st.tabs(["🛡️ Security Scan", "✍️ Writing Ally"])

# --- TAB 1: SECURITY SCAN (RESTORED TEXT & IMAGE) ---
with tab_security:
    st.markdown("### 🔍 Security Discerner")
    
    # Restoring the choice between Code/Text and Image
    upload_type = st.radio("Upload Type:", ["Code/File", "UI Screenshot/Image"], horizontal=True)
    
    if upload_type == "Code/File":
        uploaded_file = st.file_uploader("Upload Code (py, js, txt, pdf):", type=["py", "js", "txt", "pdf"])
        user_text = st.text_area("Or paste code here:")
    else:
        uploaded_image = st.file_uploader("Upload UI Screenshot:", type=["jpg", "jpeg", "png"])

    if st.button("🚀 RUN AUDIT"):
        with st.spinner("Analyzing..."):
            try:
                if upload_type == "Code/File":
                    # Logic for text/file audit
                    content = user_text if user_text else "Check this file for bugs."
                    resp = client.models.generate_content(model="gemini-2.5-flash", contents=content)
                else:
                    # Logic for Image/Multimodal audit
                    img = Image.open(uploaded_image)
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=[img, "Identify security flaws in this UI."])
                
                st.session_state['report_security'] = resp.text
            except Exception as e:
                st.error(f"Audit Error: {e}")

    if st.session_state.get('report_security'):
        st.markdown(st.session_state['report_security'])

# --- TAB 2: WRITING ALLY (STAYS CLEAN) ---
with tab_grammar:
    st.markdown("### ✍️ Writing Ally")
    g_input = st.text_area("Paste text here:", height=150, key="writing_input")
    
    col_t, col_a = st.columns(2)
    with col_t: 
        tone = st.selectbox("Tone:", ["Formal", "Direct", "Casual"], key="g_tone")
    with col_a: 
        action = st.radio("Mode:", ["Standard Fix", "Zen Mode"], key="g_action", horizontal=True)

    if st.button("✨ REFINE TEXT"):
        # ... (Clean prompt logic we built earlier)
        prompt = f"Task: {action}\nTone: {tone}\nInput: '{g_input}'\nOutput ONLY the result."
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        st.session_state['report_grammar'] = resp.text
        st.rerun()

    st.button("🗑️ Reset Writing Ally", on_click=reset_writing_ally)
    
    if st.session_state.get('report_grammar'):
        st.divider()
        st.code(st.session_state['report_grammar'], language=None)
