import streamlit as st
from resume_utils import extract_text_from_docx, evaluate_resume

st.set_page_config(page_title="RigReady", layout="centered")
st.title("🛠️ RigReady — Welders Welcome. Slackers Not.")

uploaded_files = st.file_uploader(
    "Upload one or more resumes (.docx)", type="docx", accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        st.subheader(f"📄 {file.name}")
        text = extract_text_from_docx(file)
        evaluation = evaluate_resume(text)
        st.markdown(f"**Score:** {evaluation['score']} / 100")
        st.markdown(f"**Feedback:** {evaluation['feedback']}")
