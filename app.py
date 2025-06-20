import streamlit as st
import pandas as pd
from resume_utils import extract_text_from_pdf, score_resume

# ------------------ 🎨 Logo + Header ---------------------
st.markdown(
    """
<div style="display: flex; justify-content: flex-end; margin-bottom: -40px;">
    <img src='RigReadyLogo.png' width='160'>
</div>
""",
    unsafe_allow_html=True,
)

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
    font-size: 18px;
    font-style: italic;
    color: #aaaaaa;
    font-weight: 600;
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

# ------------------ 📤 File Upload ---------------------
uploaded_files = st.file_uploader(
    "Upload Résumés (PDFs)", type="pdf", accept_multiple_files=True
)


# ------------------ ✅ Verdict Logic ---------------------
def extract_verdict(results):
    score = results["Total Score"]
    exp = results["Experience Match"]
    tank = results["Bonus - Tank Work"]

    if score >= 85:
        return "✅ Send to Weld Test"
    elif exp >= 10 and score < 65:
        return "🔍 Trust but Verify"
    elif 65 <= score < 85:
        return "⚠️ Promising – Needs Clarification"
    else:
        return "❌ Not Test-Ready"


# ------------------ 🧮 Resume Processing ---------------------
if uploaded_files:
    score_list = []

    for file in uploaded_files:
        with st.spinner(f"Processing: {file.name}"):
            text = extract_text_from_pdf(file)
            results = score_resume(text)
            verdict = extract_verdict(results)
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

    # ------------------ 📂 Detailed Breakdown ---------------------
    for name, results, _ in score_list:
        with st.expander(f"📄 {name} – Detailed Breakdown"):
            score_display = f"{results['Total Score']}%"
            if results["Total Score"] > 100:
                score_display += " 🔥"
            st.metric("Total Score", score_display)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Core Categories")
                st.write("Experience Match:", results["Experience Match"])
                if "Experience Years" in results:
                    st.write(
                        "Estimated Welding Experience:",
                        results["Experience Years"],
                        "years",
                    )
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

    # ------------------ 📘 Scoring Guide ---------------------
    with st.expander("📘 Scoring Guide"):
        st.markdown(
            """
- **✅ Send to Weld Test**: 85%+
- **🔍 Trust but Verify**: 10+ years welding experience but weak score
- **⚠️ Promising – Needs Clarification**: 65–84%
- **❌ Not Test-Ready**: Under 65%

**Scoring Breakdown**:
- Core: experience, processes, materials, tools, safety
- Bonus: tank work, certifications, local shop names, relocation
- Welding position terms (e.g., 6G, overhead) enhance process match

“RigReady doesn't guess — it grinds.”
"""
        )
