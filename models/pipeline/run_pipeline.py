# Wires extraction, clause splitting, and classification into one document pipeline.

from models.analysis.clause_classifier import analyze_contract_clause
from models.clause_splitter.splitter import (
    NUMBERED_CLAUSE_PATTERN,
    SECTION_HEADER_PATTERN,
    split_into_clauses,
)
from models.extraction.model1b_paddleocr import extract_text_from_image

# Below this word count, an unmarked clause (e.g. a title) is treated as too
# trivial to classify, and not sent to the Llama classifier. Marked clauses (numbered or
# ARTICLE-style) skip this check entirely.
MIN_CLAUSE_WORD_COUNT = 5


# Checks whether a clause has enough real content to be worth classifying
def _has_enough_content(clause_text):
    return len(clause_text.split()) >= MIN_CLAUSE_WORD_COUNT


# Checks whether a clause begins with a recognized numbered or ARTICLE-style marker. 
def _starts_with_marker(clause_text):
    return bool(NUMBERED_CLAUSE_PATTERN.match(clause_text) or SECTION_HEADER_PATTERN.match(clause_text))


# Classifies one clause turning any failure into an Error result
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


# Decides whether to classify a clause or skip it as too short to mean anything.
# Marked clauses always get classified, regardless of length.
def _process_clause(clause_text):
    if not _starts_with_marker(clause_text) and not _has_enough_content(clause_text):
        return {
            "clause_text": clause_text,
            "status": "skipped",
            "reason": "insufficient content for classification",
        }
    return _analyze_clause_safely(clause_text)


# Runs one document image through extraction, splitting, and classification end-to-end
def process_document(image_path: str) -> list[dict]:
    try:
        lines = extract_text_from_image(image_path)
    except Exception:
        return []  # unreadable or corrupt image

    text = "\n".join(lines)
    clauses = split_into_clauses(text)

    return [_process_clause(clause) for clause in clauses]
