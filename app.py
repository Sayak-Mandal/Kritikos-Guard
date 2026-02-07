import streamlit as st
from google import genai
import os
from fpdf import FPDF

# --- 1. CONFIGURATION & CALLBACKS ---
st.set_page_config(page_title="Kritikos Guard | Pro Developer Hub", layout="wide")

# Callback function to reset the Writing Ally tab properly
def reset_writing_ally():
    st.session_state['writing_input'] = ""
    if 'report_grammar' in st.session_state:
        st.session_state['report_grammar'] = ""

# Initialize Session State for results
if 'report_security' not in st.session_state:
    st.session_state['report_security'] = None
if 'report_grammar' not in st.session_state:
    st.session_state['report_grammar'] = ""

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.title("🛡️ Kritikos Guard")
    st.subheader("Pro Developer Hub")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.info("Engine: gemini-2.5-flash")
    st.divider()
    st.markdown("### About\nA polite, modern security auditor and writing companion for the next generation of IT professionals.")

# Try to get the key from secrets first (Your existing setup)
api_key = st.secrets.get("GEMINI_API_KEY")

# If it's still missing, show the input box as a backup
if not api_key:
    api_key = st.text_input("Enter Gemini API Key:", type="password")

# --- 3. MAIN INTERFACE ---
st.title("🛡️ Smart Developer Toolkit")
tab_security, tab_grammar = st.tabs(["🛡️ Security Scan", "✍️ Writing Ally"])

# --- TAB 1: SECURITY SCAN ---
with tab_security:
    st.markdown("### 🔍 Security Discerner")
    uploaded_file = st.file_uploader("Upload Code File (PDF/Text):", type=["pdf", "txt", "py", "js"])
    
    if st.button("🚀 RUN AUDIT"):
        with st.spinner("Analyzing vulnerabilities..."):
            try:
                client = genai.Client(api_key=api_key)
                # (Assuming file processing logic is here)
                prompt_sec = "Audit this code for security vulnerabilities and provide a health score."
                resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt_sec)
                st.session_state['report_security'] = resp.text
            except Exception as e:
                st.error(f"Audit Error: {e}")

    if st.session_state['report_security']:
        st.markdown(st.session_state['report_security'])
        
        # PDF EXPORT FIX
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=st.session_state['report_security'].encode('latin-1', 'replace').decode('latin-1'))
        
        # Encoding fix for download button
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Export Audit Report", data=pdf_bytes, file_name="Kritikos_Audit.pdf", mime="application/pdf")

# --- TAB 2: WRITING ALLY ---
with tab_grammar:
    st.markdown("### ✍️ Writing Ally")
    
    # Text area with 'key' for the reset callback
    g_input = st.text_area(
        "Paste your text here:", 
        height=150, 
        key="writing_input", 
        placeholder="e.g., Enter your text here."
    )
    
    col_t, col_a = st.columns(2)
    with col_t: 
        tone = st.selectbox("Select Tone:", ["Formal", "Direct", "Casual"], key="g_tone")
    with col_a: 
        action = st.radio("Correction Level:", ["Standard Fix", "Zen Mode"], key="g_action", horizontal=True)

    if st.button("✨ REFINE TEXT"):
        if not g_input: 
            st.warning("Please enter some text to refine.")
        else:
            with st.spinner("Refining..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # Modern Sentinel Prompt to prevent chatter
                    prompt = (
                        f"Task: {action}\n"
                        f"Tone: {tone}\n"
                        f"Input: '{g_input}'\n"
                        "CRITICAL: Output ONLY the corrected text. Do NOT explain, "
                        "do NOT use quotes, and do NOT add intro/outro text."
                    )

                    # KEYWORD FIX: Added model= and contents=
                    resp = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=prompt
                    )
                    
                    st.session_state['report_grammar'] = resp.text
                    st.rerun() 
                except Exception as e: 
                    st.error(f"Technical Error: {e}")

    # Use 'on_click' to trigger the reset function correctly
    st.button("🗑️ Reset Writing Ally", on_click=reset_writing_ally)

    # Display Result
    if st.session_state['report_grammar']:
        st.divider()
        st.success("✅ Refined Version:")
        st.code(st.session_state['report_grammar'], language=None)
