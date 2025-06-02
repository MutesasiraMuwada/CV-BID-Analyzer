import streamlit as st
import pdfplumber
import docx2txt
import io
import requests

# App title
st.title("📄 CV-BID ANALYSER)")

# Hugging Face inference API setup
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
headers = {
    "Authorization": f"Bearer {st.secrets['huggingface']['token']}"  # Safely loads from secrets.toml
}

# Upload CV
st.header("1. Upload Your CV (PDF or DOCX)")
uploaded_cv = st.file_uploader("Upload CV", type=["pdf", "docx"])

# Upload Bid
st.header("2. Upload Bid Document (PDF or DOCX)")
uploaded_bid = st.file_uploader("Upload Bid", type=["pdf", "docx"])

# Extract text from uploaded files
def extract_text(file, filename):
    if filename.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif filename.endswith(".docx"):
        return docx2txt.process(file)
    else:
        return ""

# Send prompt to Hugging Face model
def query_llm(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        return response.json()[0]["generated_text"]
    except Exception as e:
        st.error("Error decoding model response. Please check Hugging Face token or try another model.")
        return None

# Trigger analysis
if st.button("🔍 Analyze"):
    if uploaded_cv and uploaded_bid:
        with st.spinner("Reading documents..."):
            cv_text = extract_text(uploaded_cv, uploaded_cv.name)
            bid_text = extract_text(uploaded_bid, uploaded_bid.name)

        if not cv_text.strip() or not bid_text.strip():
            st.error("One or both documents appear to be empty.")
        else:
            prompt = f"""
Compare this candidate CV against the job description.

JOB DESCRIPTION:
{bid_text[:1500]}

CANDIDATE CV:
{cv_text[:1500]}

Provide:
1. Match percentage (0–100%)
2. Top 3 strengths
3. Top 3 missing qualifications
4. Suggestions for improvement
"""

            with st.spinner("Analyzing with Hugging Face FLAN-T5..."):
                result = query_llm(prompt)

            if result:
                st.success("✅ Analysis Complete")
                st.markdown(f"### Result\n{result}")
    else:
        st.warning("Please upload both a CV and a Bid document.")
