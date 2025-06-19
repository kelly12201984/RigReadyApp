from docx import Document


def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])


def evaluate_resume(text):
    required_keywords = [
        "welding",
        "fluxcore",
        "mig",
        "stainless",
        "carbon",
        "blueprint",
        "fabrication",
        "tape measure",
        "10 hour shift",
    ]
    score = sum(keyword.lower() in text.lower() for keyword in required_keywords) * 10
    feedback = []

    for word in required_keywords:
        if word.lower() not in text.lower():
            feedback.append(f"❌ Missing keyword: `{word}`")

    if not feedback:
        feedback.append("✅ All key terms found! This resume looks solid.")

    return {"score": score, "feedback": "\n".join(feedback)}
