# Wires extraction, clause splitting, and classification into one document pipeline.

from models.analysis.clause_classifier import analyze_contract_clause
from models.clause_splitter.splitter import (
    NUMBERED_CLAUSE_PATTERN,
    SECTION_HEADER_PATTERN,
    split_into_clauses,
)
from models.extraction.model1b_paddleocr import extract_text_from_image, unload_ocr_engine
from models.translation.model4_nllb import translate_to_urdu, unload_translator

# Below this word count, an unmarked clause (e.g. a title) is treated as too trivial to classify, and not sent to the Llama classifier. 
# Marked clauses (numbered or ARTICLE-style) skip this check entirely.
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


# Translates a clause's explanation to Urdu
def _translate_explanation_safely(explanation):
    try:
        return translate_to_urdu(explanation)
    except Exception:
        return None


# Decides whether to classify a clause or skip it as too short to mean anything.
def _process_clause(clause_text, translate):
    if not _starts_with_marker(clause_text) and not _has_enough_content(clause_text):
        return {
            "clause_text": clause_text,
            "status": "skipped",
            "reason": "insufficient content for classification",
        }

    result = _analyze_clause_safely(clause_text)

    if translate and result["risk_level"] != "Error":
        result["explanation_urdu"] = _translate_explanation_safely(result["explanation"])

    return result


# Runs one document image through extraction, splitting, and classification end-to-end.
# optionally translates each classified clause's explanation to Urdu.
def process_document(image_path: str, translate: bool = False) -> list[dict]:
    try:
        lines = extract_text_from_image(image_path)
    except Exception:
        return []  # unreadable or corrupt image
    finally:
        # OCR is finished so freeing it before the other models load
        unload_ocr_engine()

    text = "\n".join(lines)
    clauses = split_into_clauses(text)

    if translate:
        try:
            return [_process_clause(clause, translate) for clause in clauses]
        finally:
            unload_translator()

    return [_process_clause(clause, translate) for clause in clauses]
