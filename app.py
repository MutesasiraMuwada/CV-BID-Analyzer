import streamlit as st
import pdfplumber
import docx2txt
import io
import requests

# Set page configuration
st.set_page_config(page_title="CV-Bid Analyzer", layout="centered")

# Hugging Face Inference API token from Streamlit secrets
HUGGINGFACE_TOKEN = st.secrets["huggingface"]["token"]

def query_llm(prompt):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1024}
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()
        return result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "No response.")
    except requests.exceptions.JSONDecodeError:
        st.error("Error decoding model response. Please check your Hugging Face model/token.")
        st.stop()

def extract_text(file, filename):
    if filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif filename.endswith(".docx"):
        return docx2txt.process(io.BytesIO(file.read()))
    return ""

# UI layout
st.title("📄 CV-Bid Analyzer")
st.markdown("Upload your CV and a Bid Description to get an AI-powered analysis.")

cv_file = st.file_uploader("1. Upload Your CV (PDF or DOCX)", type=["pdf", "docx"])
bid_file = st.file_uploader("2. Upload Bid Document (PDF or DOCX)", type=["pdf", "docx"])

if st.button("🔍 Analyze CV vs Bid"):
    if not cv_file or not bid_file:
        st.warning("Please upload both files.")
    else:
        cv_text = extract_text(cv_file, cv_file.name)
        bid_text = extract_text(bid_file, bid_file.name)

        if not cv_text.strip() or not bid_text.strip():
            st.error("One or both documents seem empty. Please try again.")
        else:
            with st.spinner("Analyzing with Mistral-7B..."):
                prompt = f"""
                [INST]Analyze this CV against the job requirements:

                JOB DESCRIPTION:
                {bid_text[:2000]}

                CANDIDATE CV:
                {cv_text[:2000]}

                Provide:
                1. Match percentage (0-100%)
                2. Top 3 strengths
                3. Top 3 missing qualifications
                4. Improvement suggestions

                Format as markdown.[/INST]
                """
                result = query_llm(prompt)
                st.success("✅ Analysis Complete")
                st.markdown(result)
