"""This file splits raw legal document text into individual clauses.

-proritizes numbered clause markers like "1.", "2." since that's how most contracts are 
structured.
-falls back to plain sentence-boundary splitting for documnets with no numbering.
"""

import re

NUMBERED_CLAUSE_PATTERN = re.compile(r'(?<!\S)(\d{1,3})\.\s*(?=[A-Z])')

# Fallback for text with no numbering- splits after sentence-ending punctuation before a capital letter
SENTENCE_BOUNDARY_PATTERN = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')

# Needs at least 2 numbered markers before trusting the text is numbered-clause structured
MIN_NUMBERED_MARKERS = 2


# Cleans up messy whitespace so each clause looks tidy
def _normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


# Splits plain text into sentences when there's no clause numbering
def _split_by_sentences(text):
    normalized = _normalize_whitespace(text)
    if not normalized:
        return []
    return [s.strip() for s in SENTENCE_BOUNDARY_PATTERN.split(normalized) if s.strip()]


# Cuts the text into clauses at each numbered marker found
def _split_by_numbered_clauses(text, markers):
    clauses = []

    preamble = text[:markers[0].start()].strip()
    if preamble:
        clauses.append(_normalize_whitespace(preamble))  # kept as one block, no further sentence split

    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        clause = text[marker.start():end].strip()
        if clause:
            clauses.append(_normalize_whitespace(clause))

    return clauses


# Breaks a full document's text into a list of separate clauses
def split_into_clauses(text: str) -> list[str]:
    if not text or not text.strip():
        return []

    markers = list(NUMBERED_CLAUSE_PATTERN.finditer(text))

    if len(markers) >= MIN_NUMBERED_MARKERS:
        return _split_by_numbered_clauses(text, markers)

    return _split_by_sentences(text)
