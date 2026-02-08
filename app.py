import streamlit as st
from google import genai
import os
import re
from fpdf import FPDF
from PIL import Image

# --- 1. CONFIGURATION & GLOBAL CALLBACKS ---
st.set_page_config(page_title="Kritikos Guard | Pro Developer Hub", layout="wide")

# The function that clears EVERYTHING
def global_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Callback for just the Writing Ally
def reset_writing_ally():
    st.session_state['writing_input'] = ""
    if 'report_grammar' in st.session_state:
        st.session_state['report_grammar'] = ""

# Initialize Session State
if 'report_security' not in st.session_state:
    st.session_state['report_security'] = None
if 'report_grammar' not in st.session_state:
    st.session_state['report_grammar'] = ""

# --- 2. SIDEBAR (Status & Privacy) ---
with st.sidebar:
    st.title("🛡️ Kritikos Guard")
    st.markdown("---")
    
    # API Key Logic (Secrets + Manual Backup)
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    if api_key:
        st.success("✅ Connection Active")
        st.info("Engine: gemini-3-flash")
    else:
        st.error("❌ Key Required")
    
    st.markdown("---")
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

# --- TAB 1: SECURITY SCAN ---
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
                # Prompt ensuring the AI identifies correctly
                prompt_sec = (
                    "Act as an advanced AI Security Auditor. Identify yourself as Kritikos Guard AI. "
                    "Provide: 1. A 'Security Health Score' (0-100). "
                    "2. Breakdown of vulnerabilities. 3. FULL corrected code block at the end."
                )
                if upload_type == "Code/File":
                    content = u_text if u_text else "Audit this file."
                    resp = client.models.generate_content(model="gemini-3-flash-preview", contents=[content, prompt_sec])
                else:
                    img = Image.open(u_img)
                    resp = client.models.generate_content(model="gemini-3-flash-preview", contents=[img, prompt_sec])
                
                st.session_state['report_security'] = resp.text
            except Exception as e:
                st.error(f"Audit Error: {e}")

    if st.session_state.get('report_security'):
        st.divider()
        # ... (Health Meter logic stays here) ...

        # Display the full report
        st.markdown(st.session_state['report_security'])
        
        # ADD THIS: A dedicated "Copy Fix" area
        st.info("📋 **Quick Copy:** Use the button in the top-right of the box below to copy the corrected code.")
        st.code(st.session_state['report_security'], language="python")
        
        # VISUAL HEALTH METER LOGIC
        # This version looks for the number anywhere near the word 'Score'
        score_match = re.search(r"Score.*?\b(\d{1,3})\b", st.session_state['report_security'], re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            st.write(f"### 🛡️ Security Health Score: {score}/100")
            if score >= 80:
                st.progress(score / 100)
                st.success("🟢 Code follows strong security patterns.")
            elif score >= 50:
                st.progress(score / 100)
                st.warning("🟡 Moderate risks identified.")
            else:
                st.progress(score / 100)
                st.error("🔴 Critical vulnerabilities detected.")

        st.markdown(st.session_state['report_security'])
        
        # PDF Export
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=st.session_state['report_security'].encode('latin-1', 'replace').decode('latin-1'))
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Download Audit (PDF)", data=pdf_bytes, file_name="Security_Audit.pdf")

# --- TAB 2: WRITING ALLY ---
with tab_grammar:
    st.markdown("### ✍️ Writing Ally")
    g_input = st.text_area("Draft Text:", height=150, key="writing_input")
    
    col_t, col_a = st.columns(2)
    with col_t: 
        tone = st.selectbox("Tone:", ["Formal", "Neutral", "Casual"], key="g_tone")
    with col_a: 
        action = st.radio("Mode:", ["Standard Fix", "Zen Mode"], key="g_action", horizontal=True)

    if st.button("✨ REFINE TEXT"):
        with st.spinner("Polishing with Gemini 3 Flash..."):
            try:
                # Prompt ensuring no chatter
                prompt = f"Task: {action}\nTone: {tone}\nInput: '{g_input}'\nOutput ONLY the result."
                resp = client.models.generate_content(model="gemini-3-flash", contents=prompt)
                st.session_state['report_grammar'] = resp.text
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Specific reset for this tab
    st.button("🗑️ Reset Writing Ally", on_click=reset_writing_ally)
    
    # This is the section that was causing your Indentation Error
    if st.session_state.get('report_grammar'):
        st.divider()
        st.markdown("#### ✅ Refined Output (Copyable)")
        
        # st.code provides the built-in COPY BUTTON in the top right
        st.code(st.session_state['report_grammar'], language=None)
        
        st.download_button(
            label="📥 Download as Text File", 
            data=st.session_state['report_grammar'], 
            file_name="Refined_Text.txt"
        )

# --- 4. GLOBAL RESET (At the very bottom, outside of any tabs) ---
st.divider()
st.button("🔄 GLOBAL SYSTEM RESET", on_click=global_reset)

# --- 4. GLOBAL RESET ---
st.divider()
st.button("🔄 GLOBAL SYSTEM RESET", on_click=global_reset)
