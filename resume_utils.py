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
LOCAL_SHOPS = {"macaljon": 15, "coastal welding": 12, "griffin contracting": 8}
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

    # 1. Experience Match (regex-based)
    match = re.search(r"(\d+)[+ ]*years?", text)
    if match:
        years = int(match.group(1))
        if years >= 8:
            pts = 20
        elif years >= 5:
            pts = 15
        elif years >= 3:
            pts = 10
        elif years >= 1:
            pts = 5
        else:
            pts = 0
        result["Experience Match"] = pts
        score += pts
    else:
        # Fallback: count number of welding jobs listed
        years_count = len(re.findall(r"\b(welder|welding)\b", text))
        if years_count >= 3:
            result["Experience Match"] = 10
            score += 10

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

    if len(found_processes) >= 3:
        result["Flags"].append("🛠 Multiple welding processes listed")

    # 3. Material Experience
    for material, pts in MATERIALS.items():
        if material in text:
            result["Material Experience"] += pts
    score += min(result["Material Experience"], 25)

    # 4. Fit-Up & Blueprint + Tools
    fit_score = sum(pts for term, pts in FIT_UP.items() if term in text)
    tool_score = min((len([t for t in TOOLS if t in text]) // 2), 5)
    result["Tools & Fit-Up Match"] = min(fit_score + tool_score, 10)
    score += result["Tools & Fit-Up Match"]

    # 5. Safety
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
            elif cert in ["6g", "3g", "weld test", "certified"]:
                cert_pts += 3
    result["Bonus - Certifications"] = min(cert_pts, 10)

    # Bonus: Local Shop (accumulate multiple matches)
    for shop in LOCAL_SHOPS:
        if shop in text:
            result["Bonus - Local Shop"] += LOCAL_SHOPS[shop]
    result["Bonus - Local Shop"] = min(result["Bonus - Local Shop"], 15)

    # Bonus: Relocation
    if re.search(r"relocat(e|ing|ion)", text) and score >= 50:
        result["Bonus - Relocation"] = 5

    # Score capping and calculation
    result["Total Score"] = min(
        score
        + result["Bonus - Tank Work"]
        + result["Bonus - Certifications"]
        + result["Bonus - Local Shop"]
        + result["Bonus - Relocation"],
        100,
    )

    # Flags
    if any(text.find(zip) != -1 for zip in SAVANNAH_ZIPS) or "savannah" in text:
        result["Flags"].append("📍 Local to Savannah area")

    # Recommendation flag
    if result["Total Score"] >= 85:
        result["Flags"].append("✅ Send to Weld Test")
    elif result["Total Score"] >= 65:
        result["Flags"].append("⚠️ Promising – Needs Clarification")
    else:
        result["Flags"].append("❌ Not Test-Ready")

    return result
