import fitz  # PyMuPDF
import re
import difflib
from datetime import datetime


# ------------------------------
# PDF TEXT EXTRACTION
# ------------------------------
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    text = text.replace("/", " ")  # Normalize slashes
    return text.lower()


# ------------------------------
# HELPER: CONTEXTUAL DATE RANGE EXPERIENCE
# ------------------------------
def extract_years_from_contextual_date_ranges(text):
    date_patterns = re.findall(
        r"([a-z]{3,9} \d{4}|[0-1]?\d/[0-9]{4}|20\d{2})", text, re.IGNORECASE
    )
    date_objects = []
    for date_str in date_patterns:
        parsed = parse_flexible_date(date_str)
        if parsed:
            date_objects.append(parsed)

    # Group into pairs (start, end)
    total_months = 0
    for i in range(len(date_objects) - 1):
        start_date = date_objects[i]
        end_date = date_objects[i + 1]

        context_window = text[
            max(0, text.find(date_str) - 100) : text.find(date_str) + 100
        ]
        if any(
            kw in context_window
            for kw in ["welder", "welding", "fabrication", "fitter"]
        ):
            if start_date is not None and end_date is not None:
                if start_date < end_date:
                    months = (end_date.year - start_date.year) * 12 + (
                        end_date.month - start_date.month
                    )
                    total_months += months

    years = round(total_months / 12)
    return min(years, 20)


def parse_flexible_date(date_str):
    for fmt in ("%b %Y", "%B %Y", "%m/%Y", "%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None


# ------------------------------
# EXPERIENCE WRAPPER FUNCTION
# ------------------------------
def extract_experience_years(text):
    # First try keyword method
    match = re.search(r"(\d+)[+ ]*(?:years?|yrs?)", text)
    if match:
        return int(match.group(1))

    # Else, fallback to contextual date scanning
    fallback = extract_years_from_contextual_date_ranges(text)
    return fallback if fallback else 0


# ------------------------------
# SCORING LOGIC
# ------------------------------
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
        "Flags": [],
    }

    # PROCESS ALIASES
    PROCESS_ALIASES = {
        "FCAW": ["fluxcore", "flux-core", "fcaw", "semi-automatic"],
        "GMAW": ["mig", "gmaw", "wire feed", "wire welding"],
        "SMAW": ["stick", "smaw", "arc", "arc welding"],
        "GTAW": ["tig", "gtaw"],
    }

    # WELDING POSITIONS
    POSITION_KEYWORDS = [
        "overhead",
        "vertical",
        "horizontal",
        "multiple positions",
        "various positions",
        "1g",
        "2g",
        "3g",
        "4g",
        "5g",
        "6g",
    ]

    # TOOLS
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
        "precision",
        "welding",
    ]

    # FIT UP
    FIT_UP = {
        "blueprint": 5,
        "tape measure": 0,  # muted
    }

    # SAFETY
    SAFETY = {"osha": 3, "code": 3, "quality": 1, "inspection": 1}

    # MATERIALS
    MATERIALS = {
        "stainless": 10,
        "carbon": 10,
        "steel": 5,
        "aluminum": 2,
    }

    # LOCAL SHOPS (w/ fuzzy)
    LOCAL_SHOPS = {
        "macaljon": 15,
        "coastal welding": 12,
        "griffin contracting": 8,
        "jcb": 10,
        "big john trailers": 10,
        "gulfstream": 10,
    }

    # CERTIFICATIONS
    CERTS = [
        "aws",
        "d1.1",
        "certified welder",
        "welding certificate",
        "welding cert",
        "technical college",
        "welding school",
    ]

    # TANK WORK
    TANK_KEYWORDS = [
        "pressure vessel",
        "tank fabrication",
        "asme",
        "section viii",
        "savannah tank",
    ]

    # RELOCATION
    if "willing to relocate" in text:
        result["Bonus - Relocation"] = 5

    # ------------------------
    # SCORING BEGINS
    # ------------------------

    # 1. Experience
    years_text = extract_experience_years(text)
    if years_text >= 15:
        pts = 20
    elif years_text >= 10:
        pts = 15
    elif years_text >= 5:
        pts = 10
    elif years_text >= 2:
        pts = 5
    else:
        pts = 0
    result["Experience Match"] = pts
    score += pts

    # 2. Welding Process Match (including position terms)
    found = []
    for alias_list in PROCESS_ALIASES.values():
        for kw in alias_list:
            if kw in text:
                found.append(kw)
    for pos in POSITION_KEYWORDS:
        if pos in text:
            found.append(pos)

    proc_pts = min(len(set(found)) * 5, 30)
    result["Welding Process Match"] = proc_pts
    score += proc_pts

    # 3. Material Experience
    mat_pts = 0
    for mat in MATERIALS:
        if mat in text:
            mat_pts += MATERIALS[mat]
    result["Material Experience"] = mat_pts
    score += mat_pts

    # 4. Tools & Fit-Up Match
    tool_score = sum(5 for tool in TOOLS if tool in text)
    fit_score = sum(FIT_UP[key] for key in FIT_UP if key in text)
    result["Tools & Fit-Up Match"] = min(tool_score + fit_score, 10)
    score += result["Tools & Fit-Up Match"]

    # 5. Safety & Inspection
    safety_score = sum(SAFETY[key] for key in SAFETY if key in text)
    result["Safety & Inspection"] = min(safety_score, 5)
    score += result["Safety & Inspection"]

    # Bonuses — Tank
    tank_pts = sum(10 for kw in TANK_KEYWORDS if kw in text)
    result["Bonus - Tank Work"] = min(tank_pts, 30)

    # Bonus — Certs
    result["Bonus - Certifications"] = sum(5 for cert in CERTS if cert in text)

    # Bonus — Local Shop Fuzzy Match
    for shop in LOCAL_SHOPS:
        matches = difflib.get_close_matches(shop, text.split(), cutoff=0.8)
        if matches:
            result["Bonus - Local Shop"] += LOCAL_SHOPS[shop]
    result["Bonus - Local Shop"] = min(result["Bonus - Local Shop"], 15)

    # Cap total score at 100
    result["Total Score"] = (
        min(score, 100)
        + result["Bonus - Tank Work"]
        + result["Bonus - Certifications"]
        + result["Bonus - Local Shop"]
        + result["Bonus - Relocation"]
    )

    # Add Flags
    if result["Total Score"] >= 85:
        result["Flags"].append("✅ Send to Weld Test")
    elif result["Experience Match"] >= 15 and 60 <= result["Total Score"] < 85:
        result["Flags"].append("🔍 TBV: Confirm Type of Experience")
    elif result["Total Score"] >= 65:
        result["Flags"].append("⚠️ Promising – Needs Clarification")
    else:
        result["Flags"].append("❌ Not Test-Ready")

    return result
