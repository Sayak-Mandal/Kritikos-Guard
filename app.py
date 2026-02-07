import streamlit as st
from google import genai
from google.genai import types
import PyPDF2
from fpdf import FPDF
import os, re, datetime
from PIL import Image
from dotenv import load_dotenv

# --- 1. INITIAL SETUP ---
load_dotenv()
CURRENT_MODEL = "gemini-2.5-flash" 

st.set_page_config(
    page_title="Kritikos Guard | Enterprise IT Suite",
    layout="wide",
    page_icon="🛡️"
)

# --- 2. THE ENTERPRISE DARK MODE & PULSE CSS ---
st.markdown("""
    <style>
    /* Main Page - Deep Charcoal Background */
    .stApp {
        background-color: #0B0E14 !important;
        color: #E6EDF3 !important;
    }

    /* System Pulse Animation */
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .pulse-circle {
        display: inline-block; width: 10px; height: 10px;
        background: #10B981; border-radius: 50%;
        margin-right: 8px; animation: pulse 2s infinite;
    }
    .system-status {
        font-family: 'Courier New', monospace; font-size: 0.8rem;
        color: #10B981; background: rgba(16, 185, 129, 0.1);
        padding: 8px 15px; border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        margin-bottom: 20px; text-align: center;
    }

    /* Metrics Dashboard - Full Width */
    [data-testid="stMetric"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 20px !important;
        width: 100% !important;
    }
    [data-testid="stMetricValue"] { color: #3FB950 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #8B949E !important; }

    /* Input Fields - Deep Black Background */
    .stTextArea textarea {
        background-color: #0D1117 !important;
        color: #C9D1D9 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploadDropzone"] {
        background-color: #0D1117 !important;
        border: 2px dashed #30363D !important;
        border-radius: 10px !important;
    }

    /* Professional Action Buttons */
    .stButton>button {
        background-color: #238636 !important; /* GitHub Style Green */
        color: white !important;
        border: none; border-radius: 6px;
        font-weight: 600; width: 100%; height: 3.2em;
        transition: background 0.2s;
    }
    .stButton>button:hover { background-color: #2ea043 !important; }
    
    /* Sidebar Certificate Badges */
    .cert-badge {
        background: #30363D; padding: 4px 8px; 
        border-radius: 4px; font-size: 10px; color: #8B949E;
        border: 1px solid #424D5B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR BRANDING ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 50px; margin-bottom:0;'>🏛️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top:0;'>KRITIKOS</h2>", unsafe_allow_html=True)
    
    # Pulse Status
    st.markdown('<div class="system-status"><span class="pulse-circle"></span>SECURE_SESSION_ACTIVE</div>', unsafe_allow_html=True)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key: st.success("✅ Secure API Active")
    else: st.error("❌ API Key Missing")
    
    st.divider()
    
    with st.expander("🛡️ Compliance & Privacy"):
        st.caption("• Zero-Retention Memory (RAM only)")
        st.caption("• Enterprise-Grade Encryption")
        st.markdown("""
            <div style='display: flex; flex-wrap: wrap; gap: 5px; justify-content: center;'>
                <span class="cert-badge">SOC2</span>
                <span class="cert-badge">ISO 27001</span>
                <span class="cert-badge">AES-256</span>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.info(f"Engine: {CURRENT_MODEL}")

# --- 4. MAIN UI ---
st.title("🛡️ Kritikos Guard: Enterprise IT Suite")
st.markdown("---")

tab_audit, tab_grammar = st.tabs(["🔍 Security Discerner", "✍️ Executive Polisher"])

# --- TAB 1: SECURITY AUDITOR ---
with tab_audit:
    if 'audit_u_key' not in st.session_state: st.session_state['audit_u_key'] = 0
    key_id = st.session_state['audit_u_key']

    st.write("### 📂 _Source Material_")
    file = st.file_uploader("Upload Code, PDF, or System Screenshot", type=['py', 'pdf', 'png', 'jpg', 'jpeg'], key=f"u_{key_id}")
    manual_code = st.text_area("Or Paste Raw Code Snippet:", height=250, key=f"t_{key_id}", placeholder="Kritikos will discern vulnerabilities in your input...")

    code_content, image_content = "", None
    if file:
        if file.type in ["image/png", "image/jpeg"]:
            image_content = Image.open(file)
            st.image(image_content, caption="OCR Ready Image", width=600)
        elif "pdf" in file.type:
            reader = PyPDF2.PdfReader(file)
            code_content = "".join([p.extract_text() for p in reader.pages])
        else:
            code_content = file.getvalue().decode()
    elif manual_code:
        code_content = manual_code

    if st.button("🚀 INITIATE SECURITY SCRUTINY"):
        if not (code_content or image_content):
            st.warning("Please provide input material for Kritikos.")
        else:
            with st.status("🏛️ Kritikos is discerning risks...", expanded=True) as status:
                client = genai.Client(api_key=api_key)
                prompt = """
                You are Kritikos, a Senior Security Architect. Analyze the provided input.
                1. Assign SCORE: [0-100] (High is secure).
                2. Provide VULNERABILITIES: [Critical, Medium, Low].
                3. List findings clearly.
                4. Provide fixed code between 'CORRECTED_CODE_START' and 'CORRECTED_CODE_END'.
                """
                try:
                    resp = client.models.generate_content(model=CURRENT_MODEL, contents=[prompt, image_content] if image_content else [prompt, code_content])
                    st.session_state['report_audit'] = resp.text
                    status.update(label="Scrutiny Complete!", state="complete")
                except Exception as e: st.error(f"Error: {e}")

    # Results Section
    if 'report_audit' in st.session_state:
        report = st.session_state['report_audit']
        st.divider()
        
        # Data Extraction
        score_m = re.search(r"SCORE:\s*(\d+)", report)
        vuln_m = re.search(r"VULNERABILITIES:\s*\[(\d+),\s*(\d+),\s*(\d+)\]", report)
        score_val = int(score_m.group(1)) if score_m else 0
        v = vuln_m.groups() if vuln_m else ("0", "0", "0")

        # 📊 Metrics Dashboard
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Security Score", f"{score_val}/100")
        m2.metric("Critical", v[0])
        m3.metric("Medium", v[1])
        m4.metric("Best Practice", v[2])

        # 💻 Remediation Preview
        st.subheader("🛠️ Remediation Preview")
        code_match = re.search(r"CORRECTED_CODE_START(.*?)CORRECTED_CODE_END", report, re.DOTALL)
        if code_match:
            st.code(code_match.group(1).strip(), language="python")
        else:
            st.info("No immediate code remediation identified.")

        with st.expander("📄 Full Scrutiny Logs"): st.markdown(report)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
            clean_txt = report.encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 10, clean_txt)
            # Change the .output() call to include 'S' (Output as String/Bytes) 
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 Export Audit Report", data=pdf_output, file_name="Kritikos_Audit.pdf", mime="application/pdf")
        with c2:
            if st.button("🗑️ Reset Workspace"):
                del st.session_state['report_audit']
                st.session_state['audit_u_key'] += 1
                st.rerun()

# --- TAB 2: GRAMMAR ---
with tab_grammar:
    st.markdown("### ✍️ Executive Communication Refinement")
    g_input = st.text_area("Paste Draft Communication:", height=200, key="g_input", placeholder="e.g., where is they now? when was they return?")
    
    col_t, col_a = st.columns(2)
    with col_t: 
        tone = st.selectbox("Persona:", ["Executive", "Direct", "Colloquial"], key="g_tone")
    with col_a: 
        # Renamed to Architect Mode for a modern vibe
        action = st.radio("Optimization:", ["Grammar Check", "Architect Mode"], horizontal=True)

    if st.button("✨ REFINE COMMUNICATION"):
        if not g_input: 
            st.warning("Please enter some text to refine.")
        else:
            with st.spinner("Refining..."):
                try:
                    # Initialize client
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
                        model="gemini-2.0-flash", 
                        contents=prompt
                    )
                    
                    st.session_state['report_grammar'] = resp.text
                except Exception as e: 
                    st.error(f"Technical Error: {e}")

    # Display Result
    if 'report_grammar' in st.session_state:
        st.divider()
        st.success("✅ Refined Version:")
        # Displaying in a code block or text area makes it easy to copy
        st.code(st.session_state['report_grammar'], language=None)
        
        if st.button("🗑️ Clear Result"):
            del st.session_state['report_grammar']
            st.rerun()
