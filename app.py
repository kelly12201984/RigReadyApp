# app.py
import streamlit as st
from resume_utils import extract_text_from_pdf, score_resume
import pandas as pd
import datetime

# Page config
st.set_page_config(page_title="RigReady Welding Resume Reviewer", layout="wide")
st.title("🧰 RigReady: Welding Resume Reviewer")
st.markdown("Built for Savannah Tank – Rapid Résumé Insights for Smarter Hiring")

# Sidebar info
with st.sidebar:
    st.markdown("## 📋 About RigReady")
    st.info(
        "This tool helps Savannah Tank screen welding résumés using scoring logic tailored for ASME/API fabrication roles. "
        "Upload a PDF resume and get an instant readiness score."
    )
    st.markdown("---")
    st.caption("Built with 💥 by [Your Name] using Python & Streamlit.")

# File upload
uploaded_file = st.file_uploader("Upload a Résumé (PDF Only)", type="pdf")

if uploaded_file:
    with st.spinner("Analyzing résumé..."):
        text = extract_text_from_pdf(uploaded_file)
        results = score_resume(text)

        st.subheader("🔍 Results Breakdown")
        st.metric("Total Score", f"{results['Total Score']}%")

        # Columns for detailed output
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

        # Final recommendation flag (from resume_utils)
        st.markdown("### 🔧 Summary Recommendation")
        for flag in results["Flags"]:
            if flag.startswith("✅"):
                st.success(flag)
            elif flag.startswith("⚠️"):
                st.warning(flag)
            elif flag.startswith("❌"):
                st.error(flag)

        # Optional full scorecard view
        with st.expander("📊 View Full Scorecard Table"):
            display_dict = results.copy()
            del display_dict["Flags"]  # omit flags from table
            st.dataframe(
                pd.DataFrame.from_dict(display_dict, orient="index", columns=["Score"])
            )

        # Optional raw text view (for debugging resume content)
        with st.expander("📝 View Raw Resume Text"):
            st.code(text[:5000])  # limit to avoid overload

        # Optional: Save to CSV log
        if st.button("📁 Save Score to CSV"):
            data = {
                "timestamp": datetime.datetime.now(),
                "score": results["Total Score"],
                **{k: v for k, v in results.items() if k != "Flags"},
            }
            df = pd.DataFrame([data])
            df.to_csv("resume_scores_log.csv", mode="a", header=False, index=False)
            st.success("Result saved.")
