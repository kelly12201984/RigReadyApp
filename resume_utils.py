# resume_utils.py

import fitz  # PyMuPDF
import re

# Define welding process aliases
PROCESS_ALIASES = {
    "FCAW": ["fluxcore", "flux-core", "fcaw", "semi-automatic"],
    "GMAW": ["mig", "gmaw", "wire feed", "wire welding"],
    "SMAW": ["stick", "smaw", "arc welding"],
    "GTAW": ["tig", "gtaw"],
}

TOOLS = [
    "grinder",
    "torch",
    "saw",
    "chipping hammer",
    "welder",
    "plasma",
    "beveler",
    "caliper",
    "micrometer",
    "square",
]

FIT_UP = {"blueprint": 5, "tape measure": 3, "math": 2}
SAFETY = {"OSHA": 3, "drug": 1, "quality": 1, "inspection": 1}
MATERIALS = {"stainless": 10, "carbon": 10, "steel": 5, "aluminum": 2}

LOCAL_SHOPS = {
    "macaljon": 15,
    "coastal welding": 12,
    "griffin contracting": 8,
    "jcb": 5,
    "big john trailers": 5,
}

TANK_KEYWORDS = [
    "pressure vessel",
    "vessel",
    "tank fabrication",
    "API 650",
    "ASME Section VIII",
]

CERTS = ["aws", "asme", "api", "6g", "3g", "certified", "welding school", "weld test"]
SAVANNAH_ZIPS = ["313", "314", "315", "312"]


def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.lower()


def score_resume(text):
    score = 0
    result = {
        "Experience Match": 0,
        "Welding Process Match": 0,
        "Material Experience": 0,
        "Tools & Fit-Up Match": 0,
        "Safety & Inspection": 0,
        "Bonus - Tank Work": 0,
        "Bonus - Certifications": 0,
        "Bonus - Local Shop": 0,
        "Bonus - Relocation": 0,
        "Total Score": 0,
        "Flags": [],
    }

    # 1. Experience Match (robust capture)
    exp_matches = re.findall(r"(\d+)[+ ]*years?", text)
    if exp_matches:
        max_years = max([int(y) for y in exp_matches if y.isdigit()])
        if max_years >= 8:
            pts = 20
        elif max_years >= 5:
            pts = 15
        elif max_years >= 3:
            pts = 10
        elif max_years >= 1:
            pts = 5
        else:
            pts = 0
        result["Experience Match"] = pts
        score += pts

    # 2. Welding Process Match
    process_points = 0
    found_processes = set()
    for process, aliases in PROCESS_ALIASES.items():
        for term in aliases:
            if term in text:
                found_processes.add(process)
                break

    if "FCAW" in found_processes:
        process_points += 15
    if "GMAW" in found_processes:
        process_points += 10
    if "SMAW" in found_processes:
        process_points += 5
    if "GTAW" in found_processes:
        process_points += 3

    result["Welding Process Match"] = min(30, process_points)
    score += result["Welding Process Match"]

    # 3. Material Experience
    for material, pts in MATERIALS.items():
        if material in text:
            result["Material Experience"] += pts
    score += min(result["Material Experience"], 25)

    # 4. Tools & Fit-Up Match
    for term, pts in FIT_UP.items():
        if term in text:
            result["Tools & Fit-Up Match"] += pts

    tool_hits = len([t for t in TOOLS if t in text])
    result["Tools & Fit-Up Match"] += min((tool_hits // 2), 5)
    score += min(result["Tools & Fit-Up Match"], 10)

    # 5. Safety & Inspection
    for term, pts in SAFETY.items():
        if term in text:
            result["Safety & Inspection"] += pts
    score += min(result["Safety & Inspection"], 5)

    # Bonus: Tank Work
    if any(term in text for term in TANK_KEYWORDS):
        result["Bonus - Tank Work"] = 30

    # Bonus: Certifications
    cert_pts = 0
    for cert in CERTS:
        if cert in text:
            if cert in ["aws", "asme", "api"]:
                cert_pts += 7
            elif cert == "welding school":
                cert_pts += 5
            else:
                cert_pts += 3
    result["Bonus - Certifications"] = min(cert_pts, 10)

    # Bonus: Local Shop (accumulate multiple matches + inference boosts)
    local_hit = False
    for shop, pts in LOCAL_SHOPS.items():
        if shop in text:
            result["Bonus - Local Shop"] += pts
            result["Flags"].append(f"🏭 Worked at {shop.title()}")
            local_hit = True

    result["Bonus - Local Shop"] = min(result["Bonus - Local Shop"], 15)

    # Inference boost from local shop if tools/safety weak
    if local_hit:
        if result["Tools & Fit-Up Match"] < 4:
            result["Tools & Fit-Up Match"] += 3
            score += 3
        if result["Safety & Inspection"] < 2:
            result["Safety & Inspection"] += 2
            score += 2

    # Bonus: Relocation
    if "relocat" in text and score >= 50:
        result["Bonus - Relocation"] = 5

    result["Total Score"] = (
        score
        + result["Bonus - Tank Work"]
        + result["Bonus - Certifications"]
        + result["Bonus - Local Shop"]
        + result["Bonus - Relocation"]
    )

    # Verdict Flag (goes first)
    if result["Total Score"] >= 85:
        result["Flags"].insert(0, "✅ Send to Weld Test")
    elif result["Total Score"] >= 65:
        result["Flags"].insert(0, "⚠️ Promising – Needs Clarification")
    else:
        result["Flags"].insert(0, "❌ Not Test-Ready")

    # Location Flag
    if any(zipcode in text for zipcode in SAVANNAH_ZIPS) or "savannah" in text:
        result["Flags"].append("📍 Local to Savannah area")

    return result
