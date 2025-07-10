# 🔧 RigReady: Welder Résumé Reviewer App

RigReady is a rule-based résumé reviewer app developed for a **custom tank fabrication company in the Southeast U.S.** The app was built to help the hiring team screen welder résumés more efficiently by scoring them against real job criteria — such as materials experience, blueprint reading, and fabrication tools — with instant, transparent results.

---

## 🧠 Business Problem

The company needed to **speed up and standardize the evaluation of welder résumés** to fill urgent job openings. Manual review was time-consuming, inconsistent, and required constant back-and-forth between estimators and HR.

---

## 🛠️ Approach

I created a **functional Streamlit app** that reads uploaded PDF résumés, extracts relevant content, and applies a custom scoring rubric based on domain-specific hiring needs. It flags:

- Experience with MIG, Fluxcore, Carbon & Stainless Steel
- Blueprint/math/tool knowledge
- Pressure vessel work
- Willingness to relocate
- Savannah-area ZIP codes (local bonus)

Each résumé receives a **detailed breakdown** of points awarded and missed, supporting faster, more objective hiring decisions.

### Key Tools
- Python
- Streamlit
- PyMuPDF for PDF parsing
- Rule-based NLP logic (regex & keyword detection)
- Domain-specific scoring engine

---

## ✅ Results

- **Reduced résumé review time by ~50%**
- **Batch-processing support for 60+ résumés at once**
- Delivered a working prototype that is actively being tested and refined in a real hiring environment
- Improved confidence and speed in selecting qualified welder candidates

---

## 🔮 Roadmap

- Add AI-based skill extraction (OpenAI or spaCy pipeline)
- Allow manager-defined scoring criteria via dropdown config
- Option to export scored résumé summaries to CSV or push into ATS
- Flag résumés from previous applicants or specific companies (e.g., past employees)

---

## 🔐 Context

Built in direct collaboration with a hiring manager in heavy manufacturing, **RigReady was designed for the real-world pace and constraints of fabrication hiring.** It’s not a fluff tool — it solves a bottleneck where hiring speed makes or breaks jobsite timelines.
