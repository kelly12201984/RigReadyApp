# app.py
import streamlit as st
from utils import extract_text_from_pdf, score_resume
import pandas as pd

st.set_page_config(page_title="RigReady Welding Resume Reviewer", layout="wide")
st.title("🧰 RigReady: Welding Resume Reviewer")
st.markdown("Built for Savannah Tank – Rapid Résumé Insights for Smarter Hiring")

uploaded_file = st.file_uploader("Upload a Résumé (PDF Only)", type="pdf")

if uploaded_file:
    with st.spinner("Analyzing résumé..."):
        text = extract_text_from_pdf(uploaded_file)
        results = score_resume(text)

        st.subheader("🔍 Results Breakdown")
        st.metric("Total Score", f"{results['Total Score']}%")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Core Categories")
            st.write("Experience Match:", results["Experience Match"])
            st.write("Welding Process Match:", results["Welding Process Match"])
            st.write("Material Experience:", results["Material Experience"])
            st.write("Tools & Fit-Up Match:", results["Tools & Fit-Up Match"])
            st.write("Safety & Inspection:", results["Safety & Inspection"])

        with col2:
            st.markdown("### Bonus Points")
            st.write("Tank/Pressure Vessel Work:", results["Bonus - Tank Work"])
            st.write("Certifications:", results["Bonus - Certifications"])
            st.write("Local Shop Bonus:", results["Bonus - Local Shop"])
            st.write("Willing to Relocate:", results["Bonus - Relocation"])

            if results["Flags"]:
                st.markdown("### 🚩 Flags")
                for flag in results["Flags"]:
                    st.write(flag)

        # Display raw scorecard as a dataframe
        with st.expander("View Full Scorecard"):
            display_dict = results.copy()
            del display_dict["Flags"]  # omit from table, shown above
            st.dataframe(
                pd.DataFrame.from_dict(display_dict, orient="index", columns=["Score"])
            )

        # Optional: Visual status label
        st.markdown("### 🔧 Summary Recommendation")
        if results["Total Score"] >= 90:
            st.success("🔥 Test Immediately")
        elif results["Total Score"] >= 70:
            st.info("✅ Promising – Needs Clarification")
        elif results["Total Score"] >= 50:
            st.warning("⚠️ Entry-Level or Unclear")
        else:
            st.error("❌ Not Qualified")
