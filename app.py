# app.py
import streamlit as st
from resume_utils import extract_text_from_pdf, score_resume
import pandas as pd

st.set_page_config(page_title="RigReady Welding Resume Reviewer", layout="wide")
st.title("🧰 RigReady: Welding Resume Reviewer")
st.markdown("Built for Savannah Tank – Rapid Résumé Insights for Smarter Hiring")

# Upload multiple files
uploaded_files = st.file_uploader(
    "Upload Résumés (PDFs)", type="pdf", accept_multiple_files=True
)

if uploaded_files:
    score_list = []

    for file in uploaded_files:
        with st.spinner(f"Processing: {file.name}"):
            text = extract_text_from_pdf(file)
            results = score_resume(text)
            score_list.append((file.name, results))

    # Table summary
    st.subheader("📊 Summary Table")
    table_data = []
    for name, results in score_list:
        table_data.append(
            {
                "Name": name,
                "Score": results["Total Score"],
                "Experience": results["Experience Match"],
                "Process": results["Welding Process Match"],
                "Material": results["Material Experience"],
                "Tools/Fit-Up": results["Tools & Fit-Up Match"],
                "Safety": results["Safety & Inspection"],
                "Tank Work": results["Bonus - Tank Work"],
                "Certs": results["Bonus - Certifications"],
                "Local Shop": results["Bonus - Local Shop"],
                "Relocate": results["Bonus - Relocation"],
                "Flags": ", ".join(results["Flags"]),
            }
        )

    df = pd.DataFrame(table_data).sort_values("Score", ascending=False)
    st.dataframe(df, use_container_width=True)

    # Expand each detailed result
    for name, results in score_list:
        with st.expander(f"📄 {name} – Detailed Breakdown"):
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
