"""This file splits raw legal document text into individual clauses.

-prioritizes numbered clause markers like "1.", "2." since that's how most contracts are
structured, but only when they appear at the start of a line.
-falls back to "ARTICLE I" / "ARTICLE II" style section headers if no numbered markers
are found at line-start.
-falls back further to plain sentence-boundary splitting if neither is found.
"""

import re

# Line-start only: optional leading spaces/tabs, digit(s), period, then a capital letter.
NUMBERED_CLAUSE_PATTERN = re.compile(r'^[ \t]*(\d{1,3})\.\s*(?=[A-Z])', re.MULTILINE)

# Line-start only: an all-caps word (e.g. "ARTICLE") followed by a Roman numeral (e.g. "II").
#  also matches OCR occasionally dropping the space, e.g. "ARTICLEI"; so we allow optional whitespace between the two.
SECTION_HEADER_PATTERN = re.compile(r'^[ \t]*([A-Z]{2,})\s*([IVXLCDM]+)\b', re.MULTILINE)

# Fallback for text with no numbering- splits after sentence-ending punctuation before a capital letter
SENTENCE_BOUNDARY_PATTERN = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')

# Needs at least 2 numbered markers before trusting the text is numbered-clause structured
MIN_NUMBERED_MARKERS = 2

# Needs at least 2 section headers before trusting the text is header-structured
MIN_SECTION_HEADERS = 2


# Cleans up messy whitespace so each clause looks tidy
def _normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


# Splits plain text into sentences when there's no clause numbering or headers
def _split_by_sentences(text):
    normalized = _normalize_whitespace(text)
    if not normalized:
        return []
    return [s.strip() for s in SENTENCE_BOUNDARY_PATTERN.split(normalized) if s.strip()]


# Cuts the text into clauses at each marker found (works for numbered markers or section headers)
def _split_by_markers(text, markers):
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

    numbered_markers = list(NUMBERED_CLAUSE_PATTERN.finditer(text))
    if len(numbered_markers) >= MIN_NUMBERED_MARKERS:
        return _split_by_markers(text, numbered_markers)

    header_markers = list(SECTION_HEADER_PATTERN.finditer(text))
    if len(header_markers) >= MIN_SECTION_HEADERS:
        return _split_by_markers(text, header_markers)

    return _split_by_sentences(text)
