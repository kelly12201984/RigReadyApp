import streamlit as st
import os
import fitz  # PyMuPDF
import re


# === Scoring Model ===
def score_resume(text):
    score = 0
    flags = []

    # Check for welding experience (5+ yrs)
    if re.search(
        r"\b(5|six|6|seven|7|eight|8|nine|9|ten|10)\+?\s*(years|yrs).*weld", text, re.I
    ):
        score += 20

    # Welding types
    if re.search(r"flux\s*core", text, re.I):
        score += 15
    if re.search(r"\bmig\b", text, re.I):
        score += 15

    # Materials
    if re.search(r"stainless\s*steel|ss\b", text, re.I):
        score += 15
    if re.search(r"carbon\s*steel|cs\b", text, re.I):
        score += 10

    # Blueprint, tape measure
    blueprint = bool(re.search(r"blue\s*print", text, re.I))
    tape = bool(re.search(r"tape\s*measure", text, re.I))
    if blueprint:
        score += 5
    if tape:
        score += 5

    # Fabrication tools
    if re.search(r"grinder|torch|fabrication", text, re.I):
        score += 5

    # Safety/inspection
    if re.search(r"safety|osha|inspect", text, re.I):
        score += 5

    # Tank or pressure vessel
    if re.search(r"tank|pressure\s*vessel", text, re.I):
        score += 30
        flags.append("✅ Tank/Pressure Vessel work")

    # Prior employment at Savannah Tank
    if "savannah tank" in text.lower():
        flags.append("✅ Worked at Savannah Tank")
        years = re.findall(r"(20\d{2})", text)
        if years:
            flags.append(f"📅 Years: {', '.join(sorted(set(years)))}")

    # Location info
    zip_match = re.search(r"\b(31[2-5]\d{2})\b", text)
    if zip_match:
        score += 5
        flags.append(f"📍 Local ZIP: {zip_match.group(1)}")
    else:
        citystate = re.search(r"\b([A-Z][a-z]+,\s?[A-Z]{2})\b", text)
        if citystate:
            flags.append(f"🌎 Location: {citystate.group(1)}")

    # Willing to relocate
    if re.search(r"willing to relocate", text, re.I):
        flags.append("🚚 Mentions relocation")

    return score, flags


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

    score, notes = score_resume(full_text)

    st.markdown(f"### 🔢 Score: `{score}`")
    if notes:
        st.markdown("### 📌 Flags & Notes:")
        for note in notes:
            st.write(f"- {note}")
    else:
        st.write("No additional notes.")
