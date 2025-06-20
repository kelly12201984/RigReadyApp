import re
import fitz  # PyMuPDF
from datetime import datetime


# --------------------- PDF Text Extraction ---------------------
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    # Normalize slashes and lowercase
    return text.replace("/", " ").lower()


# --------------------- Date Parsing Helper ---------------------
def parse_date(text):
    """Parses month-year or year-only formats."""
    text = text.strip().lower()
    for fmt in ("%B %Y", "%b %Y", "%m %Y", "%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


# --------------------- Contextual Experience Fallback ---------------------
def extract_years_from_contextual_date_ranges(text):
    lines = text.split("\n")
    total_years = 0
    welding_keywords = ["weld", "fabrication", "fitter", "welder", "welding"]
    date_pattern = re.compile(
        r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*\d{4}"
    )

    for i, line in enumerate(lines):
        if not date_pattern.search(line):
            continue

        # Look up to 3 lines above for a welding job title
        context_block = " ".join(lines[max(0, i - 3) : i + 1])
        if not any(kw in context_block for kw in welding_keywords):
            continue

        # Look for date pairs in the block
        date_matches = re.findall(
            r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*\d{4})\s*(?:to|–|-)\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*\d{4}|present|current)",
            context_block,
        )

        for start_text, end_text in date_matches:
            start_date = parse_date(start_text)
            if "present" in end_text or "current" in end_text:
                end_date = datetime.today()
            else:
                end_date = parse_date(end_text)

            if start_date and end_date and start_date < end_date:
                delta = end_date.year - start_date.year
                if delta > 0 and delta <= 40:
                    total_years += delta

    return min(total_years, 20)


# --------------------- Resume Scoring ---------------------
def score_resume(text):
    result = {}
    score = 0

    # ---- Normalize Text ----
    text = text.replace("/", " ").lower()

    # ------------------ 1. Experience Match ------------------
    match = re.search(r"(\d+)[+ ]*(?:years?|yrs?)", text)
    years = None

    if match:
        years = int(match.group(1))
    else:
        fallback_years = extract_years_from_contextual_date_ranges(text)
        if fallback_years >= 1:
            years = fallback_years

    if years is not None:
        if years >= 20:
            pts = 20
        elif years >= 15:
            pts = 15
        elif years >= 10:
            pts = 10
        elif years >= 5:
            pts = 5
        else:
            pts = 2
        result["Experience Match"] = pts
        score += pts
    else:
        result["Experience Match"] = 0

    # ------------------ 2. Welding Process Match ------------------
    PROCESS_ALIASES = {
        "FCAW": ["fluxcore", "flux-core", "fcaw", "semi-automatic"],
        "GMAW": ["mig", "gmaw", "wire feed", "wire welding"],
        "SMAW": ["stick", "smaw", "arc welding", "arc"],
        "GTAW": ["tig", "gtaw"],
    }
    positions = [
        "overhead",
        "vertical",
        "horizontal",
        "multiple positions",
        "various positions",
    ]
    total = 0
    for group in PROCESS_ALIASES.values():
        if any(term in text for term in group):
            total += 10
    if any(p in text for p in positions):
        total += 5
    result["Welding Process Match"] = total
    score += total

    # ------------------ 3. Material Experience ------------------
    MATERIALS = {"stainless": 10, "carbon": 10, "steel": 5, "aluminum": 2}
    mat_score = sum(pts for mat, pts in MATERIALS.items() if mat in text)
    result["Material Experience"] = mat_score
    score += mat_score

    # ------------------ 4. Tools & Fit-Up Match ------------------
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
    FIT_UP = {"blueprint": 5}
    tool_score = sum(1 for tool in TOOLS if tool in text)
    fitup_score = sum(pts for key, pts in FIT_UP.items() if key in text)
    result["Tools & Fit-Up Match"] = tool_score + fitup_score
    score += tool_score + fitup_score

    # ------------------ 5. Safety & Inspection ------------------
    SAFETY = {"osha": 3, "code": 3, "quality": 1, "inspection": 1}
    safe_score = sum(pts for key, pts in SAFETY.items() if key in text)
    result["Safety & Inspection"] = safe_score
    score += safe_score

    # ------------------ 🔧 Bonus Scoring ------------------
    tank_keywords = ["pressure vessel", "tank"]
    cert_keywords = ["aws", "welding cert", "certified welder"]
    local_shops = {
        "macaljon": 15,
        "coastal welding": 12,
        "griffin contracting": 8,
        "jcb": 10,
        "big john trailers": 10,
        "gulfstream": 12,
    }

    result["Bonus - Tank Work"] = 5 if any(t in text for t in tank_keywords) else 0
    score += result["Bonus - Tank Work"]

    cert_score = 0
    for kw in cert_keywords:
        if kw in text:
            cert_score = 10
            break
    result["Bonus - Certifications"] = cert_score
    score += cert_score

    local_bonus = 0
    for shop, pts in local_shops.items():
        if shop in text:
            local_bonus = pts
            break
    result["Bonus - Local Shop"] = local_bonus
    score += local_bonus

    result["Bonus - Relocation"] = 5 if "relocate" in text else 0
    score += result["Bonus - Willing to Relocate"]

    # ------------------ Final Output ------------------
    result["Total Score"] = min(score, 100)
    return result
