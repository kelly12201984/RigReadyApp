import re
import datetime
from dateutil import parser
from PyPDF2 import PdfReader

# --------- Updated Keywords ---------

WELDING_KEYWORDS = {
    "mig": 5,
    "gmaw": 5,
    "tig": 10,
    "gtaw": 10,
    "stick": 5,
    "smaw": 5,
    "flux": 5,
    "fcaw": 5,
    "overhead": 2,
    "vertical": 2,
    "6g": 2,
    "5g": 2,
    "3g": 2,
    "2g": 2,
    "blueprint": 5,
    "mechanical drawing": 5,
}

TOOLS_KEYWORDS = [
    "caliper",
    "micrometer",
    "tape measure",
    "angle finder",
    "grinder",
    "bevel",
    "layout",
    "tack",
    "fit",
    "square",
    "oxy",
    "torch",
    "plasma",
]

MATERIAL_KEYWORDS = ["steel", "stainless", "carbon", "aluminum", "metal", "alloy"]

SAFETY_KEYWORDS = {
    "osha": 3,
    "code": 3,
    "quality": 1,
    "inspection": 1,
}

CERT_KEYWORDS = [
    "aws",
    "d1.1",
    "api 1104",
    "asme",
    "section ix",
    "certified",
    "welding certificate",
]

TANK_KEYWORDS = [
    "pressure vessel",
    "vessels",
    "tank fabrication",
    "tank welder",
    "asme",
    "section viii",
    "section ix",
    "storage tank",
    "process vessel",
    "welded tanks",
    "savannah tank",
    "macaljon",
]

LOCAL_SHOPS = {
    "macaljon": 15,
    "coastal welding": 12,
    "jcb": 10,
    "tate metalworks": 10,
    "gulfstream": 10,
    "ross engineering": 15,
}

# --------- Helper Functions ---------


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join([page.extract_text() or "" for page in reader.pages])


def clean_text(text):
    return re.sub(r"[^\x00-\x7F]+", " ", text.lower().replace("/", "-"))


def extract_years_experience(text):
    text = clean_text(text)
    total_months = 0
    matches = re.findall(
        r"(\b\w+\s\d{4})\s*(?:to|-|–)\s*(\b\w+\s\d{4}|present|current)", text
    )
    for start, end in matches:
        try:
            start_date = parser.parse(start)
            end_date = (
                parser.parse(end)
                if "present" not in end and "current" not in end
                else datetime.datetime.today()
            )
            delta = (end_date.year - start_date.year) * 12 + (
                end_date.month - start_date.month
            )
            context_window = text[
                max(0, text.find(start) - 100) : text.find(start) + 100
            ]
            if any(
                kw in context_window
                for kw in ["welder", "welding", "fabricator", "fitter"]
            ):
                total_months += delta
        except Exception:
            continue
    return total_months // 12


def score_experience_years(years):
    if years <= 1:
        return 0
    elif years <= 4:
        return 5
    elif years <= 9:
        return 10
    elif years <= 14:
        return 15
    else:
        return 20


def score_certifications(text):
    return 15 if any(cert in text for cert in CERT_KEYWORDS) else 0


def score_safety(text):
    return sum(weight for word, weight in SAFETY_KEYWORDS.items() if word in text)


def score_materials(text):
    return sum(5 for word in MATERIAL_KEYWORDS if word in text)


def score_tools(text):
    return 10 if any(tool in text for tool in TOOLS_KEYWORDS) else 0


def score_processes(text):
    points = 0
    found = set()
    for keyword, weight in WELDING_KEYWORDS.items():
        if keyword in text and keyword not in found:
            points += weight
            found.add(keyword)
    return min(points, 30)


def detect_tank_flag(text):
    return any(tank_word in text for tank_word in TANK_KEYWORDS)


def score_tank_bonus(text):
    return 5 if detect_tank_flag(text) else 0


def score_local_bonus(text):
    return max(
        [points for shop, points in LOCAL_SHOPS.items() if shop in text], default=0
    )


def score_mig_absence(text):
    return -5 if "mig" not in text and "gmaw" not in text else 0


def interpret_verdict(score, years_experience):
    if score >= 85:
        return "✅ Send to Weld Test"
    elif years_experience >= 10 and 50 <= score <= 65:
        return "🔍 TBV: Confirm Type of Experience"
    elif 65 < score < 85:
        return "📞 Promising, call in to talk"
    else:
        return "❌ Not Test-Ready"


def score_resume(text):
    text = clean_text(text)
    years_experience = extract_years_experience(text)
    experience_score = score_experience_years(years_experience)
    process_score = score_processes(text)
    material_score = score_materials(text)
    tool_score = score_tools(text)
    safety_score = score_safety(text)
    cert_score = score_certifications(text)

    base_score = (
        experience_score + process_score + material_score + tool_score + safety_score
    )
    local_bonus = score_local_bonus(text)
    bonus_score = (
        score_tank_bonus(text) + local_bonus + score_mig_absence(text) + cert_score
    )

    total_score = min(100, base_score + bonus_score)

    verdict = interpret_verdict(total_score, years_experience)
    tank_flag = "😘 Mentions Tank Experience" if detect_tank_flag(text) else ""

    return {
        "Experience Points": experience_score,
        "Process Points": process_score,
        "Material Points": material_score,
        "Tools Points": tool_score,
        "Safety Points": safety_score,
        "Cert Points": cert_score,
        "Bonus Points": bonus_score,
        "Total Score": total_score,
        "Verdict": verdict,
        "Tank Flag": tank_flag,
        "Years of Experience": years_experience,
        "Local Bonus": local_bonus,
    }
