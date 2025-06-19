import re
from datetime import datetime


def score_resume(text):
    current_year = datetime.now().year
    text_lower = text.lower()
    flags = []

    # --- EXPERIENCE ---
    welding_jobs = re.findall(
        r"(welder|welding|fabricator|fitter|iron worker|metal finisher).*?(\d{4}).*?(present|current|\d{4})",
        text,
        re.I | re.DOTALL,
    )

    total_years = 0
    for job in welding_jobs:
        start = int(job[1])
        end = current_year if job[2].lower() in ["present", "current"] else int(job[2])
        years = end - start
        if years > 0:
            total_years += years

    exp_match = min(round((total_years / 5) * 100), 100)  # cap at 100%
    exp_score = 0.2 * exp_match  # 20% weight

    # --- WELDING PROCESS MATCH ---
    welding_terms = {
        "Fluxcore": ["fluxcore", "fcaw"],
        "MIG": ["mig", "gmaw"],
        "Stick/TIG": ["smaw", "tig", "gtaw", "stick"],
    }
    process_hits = sum(
        any(re.search(k, text_lower) for k in v) for v in welding_terms.values()
    )
    process_match = round((process_hits / len(welding_terms)) * 100)
    process_score = 0.4 * process_match  # 40% weight

    # --- MATERIALS / TOOLS / FIT-UP ---
    skill_terms = {
        "Blueprint Reading": ["blueprint", "schematic"],
        "Measuring Tools": ["tape measure", "measuring tape"],
        "Fabrication Tools": ["grinder", "torch", "hand tools", "fabrication"],
        "Safety/Inspection": ["safety", "osha", "inspection"],
        "Tank/Pressure Vessel": ["tank", "pressure vessel"],
    }
    skill_hits = sum(
        any(re.search(k, text_lower) for k in v) for v in skill_terms.values()
    )
    skill_match = round((skill_hits / len(skill_terms)) * 100)
    skill_score = 0.4 * skill_match  # 40% weight

    # --- FINAL WEIGHTED SCORE ---
    total_score = round(exp_score + process_score + skill_score)

    # --- FLAGS ---
    if "savannah tank" in text_lower:
        flags.append("✅ Worked at Savannah Tank")
        years = re.findall(r"(20\d{2})", text)
        if years:
            flags.append(f"📅 Years: {', '.join(sorted(set(years)))}")

    if re.search(r"\b(31[2-5]\d{2})\b", text):
        flags.append("📍 Local to Savannah area")
    else:
        citystate = re.search(r"\b([A-Z][a-z]+,\s?[A-Z]{2})\b", text)
        if citystate:
            flags.append(f"🌎 Location: {citystate.group(1)}")

    if "willing to relocate" in text_lower:
        flags.append("🚚 Mentions relocation")

    return {
        "Experience Match": f"{exp_match}%",
        "Welding Process Match": f"{process_match}%",
        "Tools & Fit-Up Match": f"{skill_match}%",
        "Total Score": f"{total_score}%",
        "Flags": flags,
    }
