import streamlit as st
from resume_utils import extract_text_from_pdf, score_resume
import pandas as pd

# ----------------- 🔧 Custom Styling & Logo ------------------
st.set_page_config(page_title="RigReady – Welding Résumé Tool", layout="wide")

# Logo (right-aligned) — make sure the path matches your project folder
st.markdown(
    """
    <div style="display: flex; justify-content: flex-end; margin-bottom: -35px;">
        <img src="RigReadyLogo.png" width="160">
    </div>
    """,
    unsafe_allow_html=True,
)


# Title, Tagline, Subtitle
st.markdown(
    """
<style>
.centered-title {
    text-align: center;
    font-family: 'Oswald', sans-serif;
    margin-top: -10px;
}
.app-name-tagline {
    font-size: 36px;
    font-weight: 900;
    color: #F26522;
    margin-bottom: 0px;
}
.tagline-inline {
    font-size: 20px;
    font-style: italic;
    color: #aaaaaa;
    font-weight: 500;
    margin-left: 8px;
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

# ------------------ 📤 Upload Section ---------------------
uploaded_files = st.file_uploader(
    "Upload Résumés (PDFs)", type="pdf", accept_multiple_files=True
)

# ------------------ 📊 Process Uploaded Resumes ---------------------
if uploaded_files:
    score_list = []

    for file in uploaded_files:
        with st.spinner(f"Processing: {file.name}"):
            text = extract_text_from_pdf(file)
            results = score_resume(text)
            verdict = results["Verdict"]
            flags = []
            if results.get("Tank Flag"):
                flags.append(results["Tank Flag"])
            results["Flags"] = flags
            score_list.append((file.name, results, verdict))

    # Summary Table
    st.subheader("📊 Summary Table")
    table_data = []
    for name, results, verdict in score_list:
        table_data.append(
            {
                "Name": name,
                "Score": results["Total Score"],
                "Experience": results["Experience Points"],
                "Process": results["Process Points"],
                "Material": results["Material Points"],
                "Tools/Fit-Up": results["Tools Points"],
                "Safety": results["Safety Points"],
                "Tank Work": 5 if results["Tank Flag"] else 0,
                "Local Bonus": results["Local Bonus"],
                "Certs": results["Cert Points"],
                "Verdict": verdict,
            }
        )

    df = pd.DataFrame(table_data).sort_values("Score", ascending=False)
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    # Individual Breakdown
    for name, results, _ in score_list:
        with st.expander(f"📄 {name} – Detailed Breakdown"):
            st.metric("Total Score", f"{results['Total Score']}%")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Core Categories")
                st.write("Experience Points:", results["Experience Points"])
                st.write("Process Points:", results["Process Points"])
                st.write("Material Points:", results["Material Points"])
                st.write("Tools & Fit-Up Points:", results["Tools Points"])
                st.write("Safety Points:", results["Safety Points"])
            with col2:
                st.markdown("### Bonus & Flags")
                st.write("Certifications Bonus:", results["Cert Points"])
                st.write("Tank Bonus:", 5 if results["Tank Flag"] else 0)
                st.write("Local Bonus:", results["Local Bonus"])
                if results["Flags"]:
                    st.markdown("### 🚩 Flags")
                    for flag in results["Flags"]:
                        st.write(flag)

# ------------------ 📘 Scoring Guide ---------------------
with st.expander("📘 Scoring Guide"):
    st.markdown(
        """
- **🎯 Prior Tank Experience**: Automatically assigned if tank work is mentioned
- **✅ Send to Weld Test**: Score ≥ 85%
- **🔍 TBV: Confirm Type of Experience**: 10+ years but score only 50–65
- **📞 Promising, call in to talk**: Score between 66 and 84
- **❌ Not Test-Ready**: Score < 66

**Scoring Breakdown**:
- Core: Experience, process, materials, tools, safety
- Bonus: Tank work, certs, local shop, MIG absence penalty
- Total score capped at 100

_“Weld-ready or walk — we grind through the fluff so you don’t have to.”_
"""
    )
