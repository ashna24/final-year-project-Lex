# Wires extraction, clause splitting, and classification into one document pipeline.

from models.analysis.clause_classifier import analyze_contract_clause
from models.clause_splitter.splitter import split_into_clauses
from models.extraction.model1b_paddleocr import extract_text_from_image

# Classifies one clause turning any failure into an Error result instead of crashing the batch
def _analyze_clause_safely(clause_text):
    try:
        analysis = analyze_contract_clause(clause_text)
    except Exception as e:
        analysis = {
            "risk_level": "Error",
            "confidence_score": 0,
            "explanation": f"Classification failed: {e}",
        }
    return {"clause_text": clause_text, **analysis}


# Runs one document image through extraction, splitting, and classification end-to-end
def process_document(image_path: str) -> list[dict]:
    try:
        lines = extract_text_from_image(image_path)
    except Exception:
        return []  # unreadable or corrupt image

    text = "\n".join(lines)
    clauses = split_into_clauses(text)

    return [_analyze_clause_safely(clause) for clause in clauses]
