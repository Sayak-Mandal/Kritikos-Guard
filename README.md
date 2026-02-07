# Kritikos Guard: Enterprise IT Suite
**Multimodal Security Scrutiny & Strategic Communication Powered by Gemini 3**

Kritikos Guard is a high-performance "Digital Sentinel" built to bridge the gap between technical security audits and executive-level reporting. By leveraging the multimodal capabilities of **Google Gemini 3.0 Flash**, it doesn't just scan text—it **discerns** vulnerabilities in raw code, system screenshots, and PDF reports.

---

## Key Features
* **Multimodal Scrutiny:** Audits code snippets and images (screenshots) for leaks like hardcoded API keys.
* **Health Dashboard:** Instant visual score using a weighted risk algorithm.
* **Remediation Preview:** Generates and previews secure, corrected code blocks.
* **Executive Polisher:** Translates technical findings into professional reports.

## Tech Stack
* **AI Engine:** Google Gemini 2.0 Flash (Multimodal)
* **Frontend:** Streamlit with Custom CSS
* **Language:** Python 3.12
* **Libraries:** `google-genai`, `PyPDF2`, `fpdf`, `Pillow`

## Security Scoring Formula
$$Security Score = 100 - (C \times 40 + M \times 15 + L \times 5)$$
*Where C=Critical, M=Medium, L=Low risks.*

## How to Run
1. **Clone Repo:** `git clone https://github.com/Sayak-Mandal/Kritikos-Guard.git`
2. **Install:** `pip install -r requirements.txt`
3. **Key:** Add your `GEMINI_API_KEY` to a `.env` file.
4. **Launch:** `streamlit run app.py`
