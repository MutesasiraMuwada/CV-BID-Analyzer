import streamlit as st
import requests
import pdfplumber
import docx2txt
import io

st.title("📄 CV-Bid Analyzer")

HUGGINGFACE_TOKEN = st.secrets["huggingface"]["token"]
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def query_llm(prompt):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def read_file(file, filename):
    if filename.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            return "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())
    elif filename.endswith(".docx"):
        return docx2txt.process(file)
    return ""

st.subheader("1. Upload Your CV (PDF or DOCX)")
cv_file = st.file_uploader("Upload CV", type=["pdf", "docx"])

st.subheader("2. Upload Bid Document (PDF or DOCX)")
bid_file = st.file_uploader("Upload Bid", type=["pdf", "docx"])

if st.button("🔍 Analyze") and cv_file and bid_file:
    with st.spinner("Processing..."):
        cv_text = read_file(cv_file, cv_file.name)
        bid_text = read_file(bid_file, bid_file.name)

        prompt = f"""[INST]Analyze this CV against the job requirements:

        JOB DESCRIPTION:
        {bid_text[:2000]}

        CANDIDATE CV:
        {cv_text[:2000]}

        Provide:
        1. Match percentage (0–100%)
        2. Top 3 strengths
        3. Top 3 missing qualifications
        4. Improvement suggestions
        Format in markdown.[/INST]"""

        result = query_llm(prompt)
        st.subheader("📝 CV Analysis Result")
        if isinstance(result, list):
            st.markdown(result[0]["generated_text"])
        else:
            st.error("Something went wrong.")
