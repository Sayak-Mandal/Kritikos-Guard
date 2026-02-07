import streamlit as st
from google import genai
import os
from fpdf import FPDF
from PIL import Image

# --- 1. CONFIGURATION & GLOBAL CALLBACKS ---
st.set_page_config(page_title="Kritikos Guard | Pro Developer Hub", layout="wide")

# The function that clears EVERYTHING
def global_reset():
    # Clear the session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # REMOVED st.rerun() - Streamlit does this automatically on button click

# Callback for just the Writing Ally
def reset_writing_ally():
    st.session_state['writing_input'] = ""
    if 'report_grammar' in st.session_state:
        st.session_state['report_grammar'] = ""
    # REMOVED st.rerun()

# --- 2. SIDEBAR (Restored Status & Privacy) ---
with st.sidebar:
    st.title("🛡️ Kritikos Guard")
    st.markdown("---")
    
    # API Key Logic (Secrets + Manual Backup)
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    # Restored Status Indicators
    if api_key:
        st.success("✅ Connection Active")
        st.info("Engine: gemini-2.5-flash")
    else:
        st.error("❌ Key Required")
    
    st.markdown("---")
    # Restored Privacy Assurance
    st.markdown("### 🔒 Privacy First")
    st.caption("We do **not** store your code, images, or text. All processing is done in real-time via the Gemini API.")
    
    st.divider()
    st.markdown("**Version 2.0** | Pro Developer Hub")

if not api_key:
    st.warning("Please provide an API key in the sidebar to begin.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 3. MAIN INTERFACE ---
st.title("🛡️ Smart Developer Toolkit")
tab_security, tab_grammar = st.tabs(["🛡️ Security Scan", "✍️ Writing Ally"])

# --- TAB 1: SECURITY SCAN (Restored Score & Multimodal) ---
with tab_security:
    st.markdown("### 🔍 Security Discerner")
    
    upload_type = st.radio("Audit Type:", ["Code/File", "UI Screenshot"], horizontal=True)
    
    if upload_type == "Code/File":
        u_file = st.file_uploader("Upload Script:", type=["py", "js", "txt", "pdf"])
        u_text = st.text_area("Or Paste Code Snippet:")
    else:
        u_img = st.file_uploader("Upload UI Screenshot:", type=["jpg", "png", "jpeg"])

    if st.button("🚀 RUN AUDIT"):
        with st.spinner("Analyzing and calculating health score..."):
            try:
                prompt_sec = (
                  "Act as an advanced AI Security Auditor. "
                  "Identify yourself as the Kritikos Guard AI engine. "
                  "Provide: "
                  "1. A 'Security Health Score' (0-100). "
                  "2. A detailed breakdown of vulnerabilities. "
                  "3. The FULL corrected code block at the end. "
                  "CRITICAL: Be objective, transparent, and do not claim to be a human researcher."
                  )
                )
                if upload_type == "Code/File":
                    content = u_text if u_text else "Audit this file."
                    resp = client.models.generate_content(model="gemini-2.5-flash", contents=[content, prompt_sec])
                else:
                    img = Image.open(u_img)
                    resp = client.models.generate_content(model="gemini-2.5-flash", contents=[img, prompt_sec])
                
                st.session_state['report_security'] = resp.text
            except Exception as e:
                st.error(f"Audit Error: {e}")

    if st.session_state.get('report_security'):
        st.divider()
        st.markdown(st.session_state['report_security'])
        
        # PDF Download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=st.session_state['report_security'].encode('latin-1', 'replace').decode('latin-1'))
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Download Audit (PDF)", data=pdf_bytes, file_name="Security_Audit.pdf")

# --- TAB 2: WRITING ALLY (Restored Preview & Clear) ---
with tab_grammar:
    st.markdown("### ✍️ Writing Ally")
    g_input = st.text_area("Draft Text:", height=150, key="writing_input")
    
    col_t, col_a = st.columns(2)
    with col_t: tone = st.selectbox("Tone:", ["Formal", "Neutral", "Casual"], key="g_tone")
    with col_a: action = st.radio("Mode:", ["Standard Fix", "Zen Mode"], key="g_action", horizontal=True)

    if st.button("✨ REFINE TEXT"):
        with st.spinner("Polishing..."):
            prompt = f"Task: {action}\nTone: {tone}\nInput: '{g_input}'\nOutput ONLY the result."
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            st.session_state['report_grammar'] = resp.text
            st.rerun()

    # Specific reset for this tab
    st.button("🗑️ Reset Writing Ally", on_click=reset_writing_ally)
    
    if st.session_state.get('report_grammar'):
        st.divider()
        st.code(st.session_state['report_grammar'], language=None)
        st.download_button("📥 Download Text", data=st.session_state['report_grammar'], file_name="Refined.txt")

# --- 4. GLOBAL RESET (Bottom of Page) ---
st.divider()
st.button("🔄 GLOBAL SYSTEM RESET", on_click=global_reset, help="Clear all files, text, and reports to start fresh.")
