import streamlit as st
from google import genai
import os
from fpdf import FPDF
from PIL import Image

# --- 1. CONFIGURATION & CALLBACKS ---
st.set_page_config(page_title="Kritikos Guard | Pro Developer Hub", layout="wide")

def reset_writing_ally():
    st.session_state['writing_input'] = ""
    if 'report_grammar' in st.session_state:
        st.session_state['report_grammar'] = ""

# --- 2. API SETUP ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    st.warning("Please provide an API key.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 3. MAIN INTERFACE ---
st.title("🛡️ Smart Developer Toolkit")
tab_security, tab_grammar = st.tabs(["🛡️ Security Scan", "✍️ Writing Ally"])

# --- TAB 1: SECURITY SCAN (RESTORED SCORE & PREVIEW) ---
with tab_security:
    st.markdown("### 🔍 Security Discerner")
    
    upload_type = st.radio("Audit Type:", ["Code/File", "UI Screenshot"], horizontal=True)
    
    if upload_type == "Code/File":
        u_file = st.file_uploader("Upload Script:", type=["py", "js", "txt", "pdf"])
        u_text = st.text_area("Or Paste Code Snippet:")
    else:
        u_img = st.file_uploader("Upload UI Screenshot:", type=["jpg", "png", "jpeg"])

    if st.button("🚀 RUN AUDIT"):
        with st.spinner("Calculating Security Health Score..."):
            try:
                # Prompt that forces the Score and Corrected Code block
                prompt_sec = (
                    "Analyze the following for security. "
                    "1. Give a 'Security Health Score' out of 100. "
                    "2. List vulnerabilities. "
                    "3. Provide the FULL CORRECTED CODE block at the end."
                )
                
                if upload_type == "Code/File":
                    content = u_text if u_text else "Check this file."
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=[content, prompt_sec])
                else:
                    img = Image.open(u_img)
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=[img, prompt_sec])
                
                st.session_state['report_security'] = resp.text
            except Exception as e:
                st.error(f"Audit Error: {e}")

    if st.session_state.get('report_security'):
        st.divider()
        # Displaying the Score and Audit
        st.markdown(st.session_state['report_security'])
        
        # RESTORED DOWNLOAD BUTTON
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=st.session_state['report_security'].encode('latin-1', 'replace').decode('latin-1'))
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Download Security Audit (PDF)", data=pdf_bytes, file_name="Security_Audit.pdf")

# --- TAB 2: WRITING ALLY (RESTORED CODE PREVIEW & DOWNLOAD) ---
with tab_grammar:
    st.markdown("### ✍️ Writing Ally")
    g_input = st.text_area("Input Text:", height=150, key="writing_input")
    
    col_t, col_a = st.columns(2)
    with col_t: tone = st.selectbox("Tone:", ["Formal", "Neutral", "Casual"], key="g_tone")
    with col_a: action = st.radio("Mode:", ["Standard Fix", "Zen Mode"], key="g_action", horizontal=True)

    if st.button("✨ REFINE TEXT"):
        with st.spinner("Refining..."):
            prompt = f"Task: {action}\nTone: {tone}\nInput: '{g_input}'\nOutput ONLY the result."
            resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            st.session_state['report_grammar'] = resp.text
            st.rerun()

    st.button("🗑️ Reset Writing Ally", on_click=reset_writing_ally)
    
    if st.session_state.get('report_grammar'):
        st.divider()
        st.markdown("#### ✅ Corrected Preview:")
        # RESTORED PREVIEW BOX
        st.code(st.session_state['report_grammar'], language=None)
        
        # RESTORED DOWNLOAD BUTTON FOR CORRECTED TEXT
        st.download_button(
            label="📥 Download Refined Text",
            data=st.session_state['report_grammar'],
            file_name="Refined_Text.txt",
            mime="text/plain"
        )
