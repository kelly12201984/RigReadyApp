# resume_utils.py
import fitz  # PyMuPDF
import re

# Welding process aliases
PROCESS_ALIASES = {
    "FCAW": ["fluxcore", "flux-core", "fcaw", "semi-automatic"],
    "GMAW": ["mig", "gmaw", "wire feed", "wire welding"],
    "SMAW": ["stick", "smaw", "arc welding", "stick welding"],
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
    "welding certificate",
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


def score_resume(text):
    score = 0
    text_lower = text.lower()
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

    # Experience Match
    match = re.search(r"(\d+)[+ ]*years?", text_lower)
    if match:
        years = int(match.group(1))
        pts = 20 if years >= 8 else 15 if years >= 5 else 10 if years >= 3 else 5
        result["Experience Match"] = pts
        score += pts

    # Process Match
    found_processes = set()
    for process, aliases in PROCESS_ALIASES.items():
        for term in aliases:
            if term in text_lower:
                found_processes.add(process)
                break
    if "FCAW" in found_processes:
        result["Welding Process Match"] += 15
    if "GMAW" in found_processes:
        result["Welding Process Match"] += 10
    if "SMAW" in found_processes:
        result["Welding Process Match"] += 5
    if "GTAW" in found_processes:
        result["Welding Process Match"] += 3
    score += min(result["Welding Process Match"], 30)

    # Material Experience
    for material, pts in MATERIALS.items():
        if material in text_lower:
            result["Material Experience"] += pts
    if result["Material Experience"] == 0 and any(
        alias in text_lower for alias in ["jcb", "blue bird", "macaljon", "bendron"]
    ):
        result["Material Experience"] += 10
    score += min(result["Material Experience"], 25)

    # Tools & Fit-Up
    fit_score = sum(pts for term, pts in FIT_UP.items() if term in text_lower)
    tool_score = min((len([t for t in TOOLS if t in text_lower]) // 2), 5)
    result["Tools & Fit-Up Match"] = min(fit_score + tool_score, 10)
    score += result["Tools & Fit-Up Match"]

    # Safety
    for term, pts in SAFETY.items():
        if term.lower() in text_lower:
            result["Safety & Inspection"] += pts
    if "ppe" in text_lower or "hazard" in text_lower:
        result["Safety & Inspection"] += 1
    score += min(result["Safety & Inspection"], 5)

    # Tank Work
    if any(term in text_lower for term in TANK_KEYWORDS):
        result["Bonus - Tank Work"] = 30

    # Certifications
    cert_pts = 0
    for cert in CERTS:
        if cert in text_lower:
            cert_pts += (
                7
                if cert in ["aws", "asme", "api"]
                else 5 if "school" in cert or "college" in cert else 3
            )
    result["Bonus - Certifications"] = min(cert_pts, 10)

    # Local Shops
    for shop, data in LOCAL_SHOPS.items():
        if any(alias in text_lower for alias in data["aliases"]):
            result["Bonus - Local Shop"] += data["score"]
            result["Flags"].append(f"🏭 Worked at {shop.title()}")
    result["Bonus - Local Shop"] = min(result["Bonus - Local Shop"], 15)

    # Inference: shop implies skills
    if result["Bonus - Local Shop"] >= 15:
        if result["Tools & Fit-Up Match"] < 5:
            result["Tools & Fit-Up Match"] += 3
            score += 3
        if result["Safety & Inspection"] < 3:
            result["Safety & Inspection"] += 2
            score += 2

    # Relocation
    if "relocat" in text_lower and score >= 50:
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

    # Flags
    if any(zip in text_lower for zip in SAVANNAH_ZIPS) or "savannah" in text_lower:
        result["Flags"].append("📍 Local to Savannah area")

    # Verdict flag (comes first)
    if result["Total Score"] >= 85:
        result["Flags"].insert(0, "✅ Send to Weld Test")
    elif result["Total Score"] >= 65:
        result["Flags"].insert(0, "⚠️ Promising – Needs Clarification")
    else:
        result["Flags"].insert(0, "❌ Not Test-Ready")

    return result
