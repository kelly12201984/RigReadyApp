import fitz  # PyMuPDF
import re
from datetime import datetime

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
TANK_KEYWORDS = [
    "pressure vessel",
    "vessel",
    "tank fabrication",
    "api 650",
    "asme section viii",
]
CERTS = [
    "aws",
    "asme",
    "api",
    "6g",
    "3g",
    "certified",
    "welding school",
    "technical college",
    "weld test",
]
SAVANNAH_ZIPS = ["313", "314", "315", "312"]

LOCAL_SHOPS = {
    "macaljon": {"aliases": ["macaljon", "mac aljon", "macaljon inc"], "score": 15},
    "coastal welding": {"aliases": ["coastal welding"], "score": 12},
    "griffin contracting": {"aliases": ["griffin contracting"], "score": 8},
    "jcb": {"aliases": ["jcb", "jcb north america"], "score": 10},
    "big john trailers": {"aliases": ["big john", "big john trailers"], "score": 10},
    "blue bird": {"aliases": ["blue bird", "blue bird bus company"], "score": 10},
    "bendron titan": {"aliases": ["bendron", "bendron titan"], "score": 8},
}


def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.lower()


def estimate_experience_from_dates(text):
    job_lines = [
        line
        for line in text.split("\n")
        if any(w in line for w in ["welder", "fabricator", "welding"])
    ]
    years_total = 0
    now = datetime.now().year

    for line in job_lines:
        # Match patterns like "2015 - 2020", "2018 to Present", etc.
        match = re.search(r"(\d{4})\s?[-to]{1,3}\s?(present|\d{4})", line)
        if match:
            start = int(match.group(1))
            end_str = match.group(2)
            end = now if "present" in end_str.lower() else int(end_str)
            if 1980 <= start <= now and start <= end:
                years_total += end - start
    return years_total


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

    # ✅ 1. Experience Match
    years = 0
    match = re.search(r"(\d{1,2})\s?[\+]?\s?(?:years|yrs)", text)
    if match:
        years = int(match.group(1))
    else:
        years = estimate_experience_from_dates(text)

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

    # 4. Tools & Fit-Up
    fit_score = sum(pts for term, pts in FIT_UP.items() if term in text)
    tool_score = min((len([t for t in TOOLS if t in text]) // 2), 5)
    result["Tools & Fit-Up Match"] = min(fit_score + tool_score, 10)
    score += result["Tools & Fit-Up Match"]

    # 5. Safety
    for term, pts in SAFETY.items():
        if term in text:
            result["Safety & Inspection"] += pts
    if "ppe" in text or "hazard" in text:
        result["Safety & Inspection"] += 1
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
            elif "school" in cert or "college" in cert:
                cert_pts += 5
            else:
                cert_pts += 3
    result["Bonus - Certifications"] = min(cert_pts, 10)

    # Bonus: Local Shop
    for shop, data in LOCAL_SHOPS.items():
        if any(alias in text for alias in data["aliases"]):
            result["Bonus - Local Shop"] += data["score"]
            result["Flags"].append(f"🏭 Worked at {shop.title()}")
    result["Bonus - Local Shop"] = min(result["Bonus - Local Shop"], 15)

    # Inference bonus
    if result["Bonus - Local Shop"] >= 15:
        if result["Tools & Fit-Up Match"] < 5:
            result["Tools & Fit-Up Match"] += 3
            score += 3
        if result["Safety & Inspection"] < 3:
            result["Safety & Inspection"] += 2
            score += 2

    # Bonus: Relocation
    if "relocat" in text and score >= 50:
        result["Bonus - Relocation"] = 5

    # Final Score
    result["Total Score"] = min(
        score
        + result["Bonus - Tank Work"]
        + result["Bonus - Certifications"]
        + result["Bonus - Local Shop"]
        + result["Bonus - Relocation"],
        100,
    )

    # Location flag
    if any(zip in text for zip in SAVANNAH_ZIPS) or "savannah" in text:
        result["Flags"].append("📍 Local to Savannah area")

    # Final recommendation flag
    if result["Total Score"] >= 85:
        result["Flags"].insert(0, "✅ Send to Weld Test")
    elif result["Total Score"] >= 65:
        result["Flags"].insert(0, "⚠️ Promising – Needs Clarification")
    else:
        result["Flags"].insert(0, "❌ Not Test-Ready")

    return result
