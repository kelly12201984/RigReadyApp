# app.py
import streamlit as st
from resume_utils import extract_text_from_pdf, score_resume
import pandas as pd
from PIL import Image

# Load and display logo on the right
logo = Image.open("RigReadyLogo.png")
col1, col2 = st.columns([4, 1])
with col2:
    st.image(logo, width=120)

# Title and styling
st.markdown(
    """
<style>
.centered-title {
    text-align: center;
    font-family: 'Oswald', sans-serif;
    margin-top: -20px;
}
.app-name-tagline {
    font-size: 36px;
    font-weight: 900;
    color: #F26522;
    margin-bottom: 0px;
}
.tagline-inline {
    font-size: 22px;
    font-style: italic;
    font-weight: 600;
    color: #bbbbbb;
    margin-left: 12px;
}
.subtitle {
    font-size: 18px;
    color: #CCCCCC;
    margin-top: -10px;
    margin-bottom: 4px;
}
.footerline {
    font-size: 14px;
    color: #888888;
    font-style: italic;
    margin-top: -8px;
}
</style>
<div class="centered-title">
    <div class="app-name-tagline">
        RigReady <span class="tagline-inline">I cut through more BS than a grinder.</span>
    </div>
    <div class="subtitle">Welding Résumé Scoring Tool</div>
    <div class="footerline">Built for Savannah Tank • Crafted by Kelly</div>
</div>
""",
    unsafe_allow_html=True,
)

# Upload section
uploaded_files = st.file_uploader(
    "Upload Résumés (PDFs)", type="pdf", accept_multiple_files=True
)


def extract_verdict(flags):
    if any("Send to Weld Test" in f for f in flags):
        return "✅ Test"
    if any("Promising" in f for f in flags):
        return "⚠️ Clarify"
    return "❌ No"


if uploaded_files:
    score_list = []

    for file in uploaded_files:
        with st.spinner(f"Processing: {file.name}"):
            text = extract_text_from_pdf(file)
            results = score_resume(text)
            verdict = extract_verdict(results["Flags"])
            score_list.append((file.name, results, verdict))

    st.subheader("📊 Summary Table")
    table_data = []
    for name, results, verdict in score_list:
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
                "Verdict": verdict,
            }
        )

    df = pd.DataFrame(table_data).sort_values("Score", ascending=False)
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    for name, results, _ in score_list:
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

    with st.expander("📘 Scoring Guide"):
        st.markdown(
            """
- **✅ Send to Weld Test**: 85%+
- **⚠️ Promising – Needs Clarification**: 65–84%
- **❌ Not Test-Ready**: Under 65%

**Scoring Weights**:
- Experience, processes, materials, tools, and safety form the base.
- Bonus points for tank work, certs, local shop history, or relocation.
- Denny-style shop hands get inferred skills boosts when clear.

_“When in doubt, give ‘em the hood.”_
"""
        )
