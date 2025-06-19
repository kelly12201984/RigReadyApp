import streamlit as st
import os
import fitz  # PyMuPDF
import re
from resume_utils import score_resume  # ✅ Use the correct scoring logic


# === Streamlit UI ===
st.title("🛠️ RigReady: Welding Résumé Reviewer")
st.write("Upload a PDF résumé to evaluate candidate readiness for Savannah Tank.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    # Extract text from PDF
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        full_text = ""
        for page in doc:
            full_text += page.get_text()

    st.text_area("Résumé Text", full_text, height=300)

    # Run scoring logic
    result = score_resume(full_text)

    # Debug view (optional, helpful for troubleshooting)
    st.write("🔍 DEBUG OUTPUT:", result)

    # Display Score Breakdown
    st.markdown(f"## 🧮 Final Score: `{result['Total Score']}`")
    st.markdown("### 📊 Category Breakdown:")
    st.write(f"- **Experience Match**: {result['Experience Match']}")
    st.write(f"- **Welding Process Match**: {result['Welding Process Match']}")
    st.write(f"- **Tools & Fit-Up Match**: {result['Tools & Fit-Up Match']}")

    # Display Flags
    if result["Flags"]:
        st.markdown("### 📌 Flags:")
        for flag in result["Flags"]:
            st.write(f"- {flag}")
