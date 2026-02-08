import streamlit as st
from google import genai
import os
import re
from fpdf import FPDF
from PIL import Image

# --- 1. CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="Kritikos | Pro Developer Hub", layout="wide")

# Initialize Session State
if 'reset_counter' not in st.session_state:
    st.session_state['reset_counter'] = 0
if 'report_security' not in st.session_state:
    st.session_state['report_security'] = None
if 'report_grammar' not in st.session_state:
    st.session_state['report_grammar'] = ""

def global_reset():
    # Clear all data except the counter
    for key in list(st.session_state.keys()):
        if key != 'reset_counter':
            del st.session_state[key]
    # Increment counter to force-refresh all widgets
    st.session_state['reset_counter'] += 1

def reset_writing_ally():
    st.session_state['report_grammar'] = ""
    # We use the counter here too to clear the specific text area
    st.session_state['reset_counter'] += 1

# Current 'Version' of widgets
v = st.session_state['reset_counter']

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Kritikos")
    st.markdown("---")
    
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key:", type="password", key=f"api_key_{v}")
    
    if api_key:
        st.success("✅ Connection Active")
        st.info("Engine: Gemini 3 Flash")
    else:
        st.error("❌ Key Required")
    
    st.markdown("---")
    st.markdown("### 🔒 Privacy First")
    st.caption("We do **not** store your code, images, or text. All processing is done in real-time.")
    st.divider()
    st.markdown("**Version 1.0** | Gemini 3 Edition")

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
    
    upload_type = st.radio("Audit Type:", ["Code/File", "UI Screenshot"], horizontal=True, key=f"type_{v}")
    
    if upload_type == "Code/File":
        u_file = st.file_uploader("Upload Script:", type=["py", "js", "txt", "pdf"], key=f"file_{v}")
        u_text = st.text_area("Or Paste Code Snippet:", key=f"text_sec_{v}")
    else:
        u_img = st.file_uploader("Upload UI Screenshot:", type=["jpg", "png", "jpeg"], key=f"img_{v}")

    if st.button("🚀 RUN AUDIT", key=f"run_btn_{v}"):
        with st.spinner("Gemini 3 Flash is auditing..."):
            try:
                prompt_sec = (
                    "Act as an advanced AI Security Auditor 'Kritikos Guard'. "
                    "Analyze the input and provide: 1. A 'Security Health Score' (0-100). "
                    "2. Breakdown of vulnerabilities. 3. A FULL corrected code fix wrapped in triple backticks."
                )
                
                if upload_type == "Code/File":
                    content = u_text if u_text else "Audit the uploaded file."
                    resp = client.models.generate_content(model="gemini-3-flash-preview", contents=[content, prompt_sec])
                else:
                    img = Image.open(u_img)
                    resp = client.models.generate_content(model="gemini-3-flash-preview", contents=[img, prompt_sec])
                
                st.session_state['report_security'] = resp.text
            except Exception as e:
                st.error(f"Audit Error: {e}")

    # Results Display
    if st.session_state.get('report_security'):
        st.divider()
        report = st.session_state['report_security']
        
        # VISUAL HEALTH METER
        score_match = re.search(r"Score.*?(\d+)", report, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            st.write(f"### 🛡️ Security Health Score: {score}/100")
            st.progress(score / 100)
            if score < 50: st.error("🔴 CRITICAL VULNERABILITIES DETECTED")
            elif score < 80: st.warning("🟡 Moderate Risks Identified")
            else: st.success("🟢 Strong Security Patterns Found")

        # THE FULL REPORT
        st.markdown(report)
        
        # THE COPY BUTTON (Extracting code blocks)
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", report, re.DOTALL)

        # PDF EXPORT
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=report.encode('latin-1', 'replace').decode('latin-1'))
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Download Audit (PDF)", data=pdf_bytes, file_name="Security_Audit.pdf", key=f"dl_pdf_{v}")

# --- TAB 2: WRITING ALLY ---
with tab_grammar:
    st.markdown("### ✍️ Writing Ally")
    g_input = st.text_area("Draft Text:", height=150, key=f"writing_input_{v}")
    
    col_t, col_a = st.columns(2)
    with col_t: 
        tone = st.selectbox("Tone:", ["Formal", "Neutral", "Casual"], key=f"tone_{v}")
    with col_a: 
        action = st.radio("Mode:", ["Standard Fix", "Zen Mode"], key=f"action_{v}", horizontal=True)

    if st.button("✨ REFINE TEXT", key=f"refine_btn_{v}"):
        with st.spinner("Polishing with Gemini 3.0..."):
            try:
                prompt = f"Tone: {tone}\nInput: '{g_input}'\nOutput ONLY the result."
                resp = client.models.generate_content(model="gemini-3.0-flash-preview", contents=prompt)
                st.session_state['report_grammar'] = resp.text
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Indent these lines exactly the same as the 'if st.button' above
    st.button("🗑️ Reset Writing Ally", on_click=reset_writing_ally, key=f"reset_writing_{v}")
    
    if st.session_state.get('report_grammar'):
        st.divider()
        st.markdown("#### ✅ Refined Output (Copyable)")
        
        # wrap_lines=True stops the horizontal scrolling issue
        st.code(st.session_state['report_grammar'], language=None, wrap_lines=True)
        
        st.download_button(
            label="📥 Download Text", 
            data=st.session_state['report_grammar'], 
            file_name="Refined.txt", 
            key=f"dl_txt_{v}"
        )

# --- 4. GLOBAL RESET ---
st.divider()

# ADD THIS LINE BACK: This creates the blue tip box above the button
st.info("💡 **Tip:** Use the Global Reset to clear all session data before a new audit.", icon=":material/lightbulb:")

# Ensure your button has the unique key to prevent duplicate ID errors
if st.button("🔄 GLOBAL SYSTEM RESET", on_click=global_reset, key="global_reset_final"):
    st.toast("System Wiped!", icon="🧹")
