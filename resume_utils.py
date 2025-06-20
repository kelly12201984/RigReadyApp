import fitz  # PyMuPDF
import re
import difflib
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

# 🧠 Welding-related keywords for context fallback
WELDING_KEYWORDS = [
    "weld",
    "welder",
    "welding",
    "fabrication",
    "fabricator",
    "fitter",
    "metal",
    "grind",
    "blueprint",
    "mig",
    "tig",
    "flux",
    "fcaw",
    "gmaw",
    "smaw",
    "gtaw",
]
# 🛠️ Welding process aliases and welding position terms
PROCESS_ALIASES = {
    "FCAW": ["fluxcore", "flux-core", "fcaw", "semi-automatic"],
    "GMAW": ["mig", "gmaw", "wire feed", "wire welding"],
    "SMAW": ["stick", "smaw", "arc welding", "arc"],
    "GTAW": ["tig", "gtaw"],
    "POS": [
        "vertical",
        "horizontal",
        "overhead",
        "multiple positions",
        "various positions",
        "1g",
        "3g",
        "4g",
        "6g",
    ],
}

# 🔧 Tools and fabrication instruments
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

# 📐 Blueprint / fit-up
FIT_UP = {"blueprint": 5}

# 🔒 Safety knowledge
SAFETY = {"osha": 3, "code": 3, "quality": 1, "inspection": 1}

# 🔩 Material experience
MATERIALS = {"stainless": 10, "carbon": 10, "steel": 5, "aluminum": 2}

# 🏭 Local shop experience
LOCAL_SHOPS = {
    "macaljon": 15,
    "coastal welding": 12,
    "griffin contracting": 8,
    "jcb": 10,
    "big john trailers": 10,
    "gulfstream": 10,
}

# 🚢 Tank / pressure vessel keywords
TANK_KEYWORDS = [
    "pressure vessel",
    "vessel",
    "tank fabrication",
    "api 650",
    "section viii",
    "asme section viii",
]

# 🎓 Certifications and test terms
CERTS = [
    "aws",
    "asme",
    "api",
    "6g",
    "3g",
    "certified",
    "welding school",
    "weld test",
    "technical",
]

# 📍 Savannah zip code prefixes
SAVANNAH_ZIPS = ["313", "314", "315", "312"]


# -----------------------------------------------------
# 🔍 PDF Text Extraction (Lowercase + Normalize Slashes)
# -----------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.lower().replace("/", " ")  # Normalize slashes


# 📆 Flexible Date Parsing for Contextual Experience
# -----------------------------------------------------
def parse_flexible_date(date_str):
    formats = ["%b %Y", "%B %Y", "%m/%Y", "%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None


def extract_years_from_contextual_date_ranges(text):
    text = text.lower()
    total_years = 0
    max_cap = 20

    # Normalize dashes and wording
    normalized = text.replace("–", "-").replace("—", "-").replace(" to ", "-")

    # Pattern to catch date ranges like Jan 2020 - Mar 2022
    date_pattern = r"(?:\d{1,2}[/-])?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?[a-z]*[ -/]*(20\d{2})"
    matches = re.finditer(rf"({date_pattern})\s*[-–to]+\s*({date_pattern})", normalized)

    for match in matches:
        start_str, end_str = match.group(1), match.group(2)
        start_date = parse_flexible_date(start_str)
        end_date = parse_flexible_date(end_str)

    if start_date and end_date and start_date < end_date:
        span_start = max(0, match.start() - 100)
        span_end = min(len(text), match.end() + 100)
        context = text[span_start:span_end]
        if any(kw in context for kw in WELDING_KEYWORDS):
            delta = (end_date - start_date).days / 365
            total_years += min(delta, max_cap - total_years)

    return "20+" if total_years > max_cap else str(round(total_years))


# -----------------------------------------------------
# 🧩 Experience Years Wrapper
# -----------------------------------------------------
def extract_experience_years(text):
    match = re.search(r"(\d+)[+ ]*(?:years?|yrs?)", text)
    if match:
        return match.group(1) + "+" if "+" in match.group(0) else match.group(1)
    else:
        return extract_years_from_contextual_date_ranges(text)


# -----------------------------------------------------
# 🧮 Main Resume Scoring Logic
# -----------------------------------------------------
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
    # -----------------------------------------------------
    # 🔹 1. Experience Match (inside score_resume)
    # -----------------------------------------------------

    years_text = extract_experience_years(text)
    years = 0
    try:
        years = int(re.sub(r"\D", "", years_text))
    except:
        pass

    if years >= 10:
        pts = 20
    elif years >= 5:
        pts = 15
    elif years >= 2:
        pts = 5
    else:
        pts = 0
    result["Experience Match"] = pts
    score += pts

    # 🔹 2. Welding Process Match (includes welding positions)
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
    if "POS" in found_processes:
        process_points += 2

    result["Welding Process Match"] = min(30, process_points)
    score += result["Welding Process Match"]

    # 🔹 3. Material Experience
    for material, pts in MATERIALS.items():
        if material in text:
            result["Material Experience"] += pts
    score += min(result["Material Experience"], 25)

    # 🔹 4. Tools & Fit-Up
    result["Tools & Fit-Up Match"] += sum(
        pts for term, pts in FIT_UP.items() if term in text
    )
    tool_hits = len([t for t in TOOLS if t in text])
    result["Tools & Fit-Up Match"] += min((tool_hits // 2), 5)
    score += min(result["Tools & Fit-Up Match"], 10)

    # 🔹 5. Safety
    for term, pts in SAFETY.items():
        if term in text:
            result["Safety & Inspection"] += pts
    score += min(result["Safety & Inspection"], 5)

    # 🔹 Bonus: Tank Work
    if any(term in text for term in TANK_KEYWORDS):
        result["Bonus - Tank Work"] = 30

    # 🔹 Bonus: Certifications
    cert_pts = 0
    for cert in CERTS:
        if cert in text:
            if cert in ["aws", "asme", "api"]:
                cert_pts += 7
            elif cert in ["welding school"]:
                cert_pts += 5
            elif cert in ["6g", "3g", "weld test", "certified"]:
                cert_pts += 3
    result["Bonus - Certifications"] = min(cert_pts, 10)

    # 🔹 Bonus: Local Shop (accumulate multiple matches)
    for shop in LOCAL_SHOPS:
        if shop in text:
            result["Bonus - Local Shop"] += LOCAL_SHOPS[shop]
    result["Bonus - Local Shop"] = min(result["Bonus - Local Shop"], 15)

    # 🔹 Bonus: Relocation
    if "relocat" in text and score >= 50:
        result["Bonus - Relocation"] = 5

    # 🧮 Final Score Tally
    result["Total Score"] = (
        score
        + result["Bonus - Tank Work"]
        + result["Bonus - Certifications"]
        + result["Bonus - Local Shop"]
        + result["Bonus - Relocation"]
    )

    # 🚩 Flags
    if any(text.strip().startswith(zip) for zip in SAVANNAH_ZIPS) or "savannah" in text:
        result["Flags"].append("📍 Local to Savannah area")

    if result["Total Score"] >= 85:
        result["Flags"].insert(0, "✅ Send to Weld Test")
    elif result["Total Score"] >= 65:
        result["Flags"].insert(0, "⚠️ Promising – Needs Clarification")
    else:
        result["Flags"].insert(0, "❌ Not Test-Ready")

    return result
