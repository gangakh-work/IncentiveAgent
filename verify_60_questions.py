"""Verify that all 60 FY27 acceptance questions are hardcoded and resolvable."""
from pathlib import Path
import sys
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixed_answers import get_fixed_answer, FIXED_ANSWERS

DOC = Path(__file__).resolve().parents[1] / "FY27_Chatbot_Test_Questions.docx"

def load_questions():
    questions = []
    for p in Document(DOC).paragraphs:
        text = p.text.strip()
        if text and text[0].isdigit() and ". " in text[:5]:
            questions.append(text.split(". ", 1)[1])
    return questions

questions = load_questions()
missing = [q for q in questions if get_fixed_answer(q) is None]
assert len(FIXED_ANSWERS) == 60, len(FIXED_ANSWERS)
assert len(questions) == 60, len(questions)
assert not missing, missing
print("PASS: 60/60 acceptance questions are hardcoded and resolvable.")
