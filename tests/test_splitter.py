from model1b_paddleocr import extract_text_from_image
from splitter import split_into_clauses

# a numbered employment agreement
NUMBERED_CONTRACT = (
    "EMPLOYMENT AND LIABILITY AGREEMENT\n"
    "This Agreement is entered into on this 22nd day of June, 2026, between Lex Technologies Ltd.\n"
    "(hereinafter referred to as the \"Employer\") and the undersigned individual (hereinafter referred\n"
    "to as the \"Employee\").\n"
    "1. Term of Employment and Termination The Employer reserves the right to terminate this\n"
    "agreement at any time, provided that a minimum of 30 days written notice is issued to the\n"
    "Employee. In the event of a breach of contract, immediate termination may be enforced.\n"
    "2. Liability and Compensation The Employee shall indemnify and hold harmless the\n"
    "Employer, its directors, and its affiliates from any claims, damages, or liabilities arising directly\n"
    "from their professional conduct during the term of employment.\n"
    "3. Governing Jurisdiction All disputes, controversies, or claims arising out of or relating to this\n"
    "contract shall be resolved under the applicable legal statutes of the United Kingdom and the\n"
    "Islamic Republic of Pakistan."
)

# Same contract text as above, but with messy spacing added
IRREGULARLY_SPACED_CONTRACT = (
    "EMPLOYMENT AND LIABILITY AGREEMENT\n\n\n"
    "   This Agreement is entered into on this 22nd day of June, 2026, between Lex Technologies Ltd.\n"
    "(hereinafter referred to as the \"Employer\").\n\n\n\n"
    "1.    Term of Employment    The Employer reserves the right to terminate this agreement.\n\n"
    "   2. Liability and Compensation The Employee shall indemnify the Employer.\n"
    "3.Governing Jurisdiction   All disputes shall be resolved under UK law.   \n\n"
)

# Plain text with no clause numbers at all
PLAIN_UNNUMBERED_TEXT = (
    "This agreement is confidential. Both parties agree to the terms. "
    "Any breach will result in immediate termination."
)

# Checks a real numbered contract splits into the right number of clauses
def test_splits_numbered_contract_into_expected_clauses():
    clauses = split_into_clauses(NUMBERED_CONTRACT)

    assert len(clauses) == 4
    assert clauses[0].startswith("EMPLOYMENT AND LIABILITY AGREEMENT")
    assert clauses[1].startswith("1.")
    assert "Term of Employment" in clauses[1]
    assert clauses[2].startswith("2.")
    assert "Liability and Compensation" in clauses[2]
    assert clauses[3].startswith("3.")
    assert "Governing Jurisdiction" in clauses[3]


# Checks each clause is clean, with no extra spaces or line breaks
def test_numbered_clauses_have_no_stray_whitespace():
    clauses = split_into_clauses(NUMBERED_CONTRACT)

    for clause in clauses:
        assert clause == clause.strip()
        assert "\n" not in clause
        assert "  " not in clause


# Checks plain text with no numbers still splits into separate sentences
def test_splits_unnumbered_text_into_sentences():
    clauses = split_into_clauses(PLAIN_UNNUMBERED_TEXT)

    assert len(clauses) == 3
    assert clauses[0] == "This agreement is confidential."
    assert clauses[1] == "Both parties agree to the terms."
    assert clauses[2] == "Any breach will result in immediate termination."


# Checks messy spacing doesn't break the clause splitting
def test_handles_irregular_spacing_around_numbered_clauses():
    clauses = split_into_clauses(IRREGULARLY_SPACED_CONTRACT)

    assert len(clauses) == 4
    assert clauses[1].startswith("1.")
    assert clauses[2].startswith("2.")
    assert clauses[3].startswith("3.")
    for clause in clauses:
        assert clause == clause.strip()
        assert "  " not in clause


# Checks a short bit of text still comes back as one clause
def test_very_short_input_returns_single_clause():
    clauses = split_into_clauses("Confidential.")

    assert clauses == ["Confidential."]


# Checks empty text just returns an empty list
def test_empty_and_blank_input_returns_empty_list():
    assert split_into_clauses("") == []
    assert split_into_clauses("   \n  ") == []


# "Schedule 1." and "Schedule 2." are referenced mid-sentence here
INLINE_REFERENCE_TEXT = (
    "The parties acknowledge the terms described in Schedule 1. Additional obligations "
    "are described in Schedule 2. Governing law and jurisdiction are addressed separately below."
)

# A hand-typed contract using "ARTICLE I/II/III" headers instead of numbered clauses
ARTICLE_HEADER_CONTRACT = (
    "PARTNERSHIP AGREEMENT\n"
    "This Agreement is made between the parties listed in Schedule 1.\n"
    "ARTICLE I — PURPOSE\n"
    "The parties agree to form a partnership for consulting services.\n"
    "ARTICLE II — CAPITAL CONTRIBUTIONS\n"
    "Each partner shall contribute capital as described in Schedule 2.\n"
    "ARTICLE III — DISSOLUTION\n"
    "This partnership may be dissolved by written agreement of all partners."
)


# Checks a mid-sentence reference isn't mistaken for a real clause marker
def test_inline_numeric_references_are_not_treated_as_clause_markers():
    clauses = split_into_clauses(INLINE_REFERENCE_TEXT)

    # No numbered markers or headers found, so it falls back to sentence splitting
    assert len(clauses) == 3


# Checks "ARTICLE I" style headers are detected as clause boundaries
def test_article_style_headers_are_detected_as_clause_boundaries():
    clauses = split_into_clauses(ARTICLE_HEADER_CONTRACT)

    assert len(clauses) == 4  
    assert clauses[1].startswith("ARTICLE I")
    assert clauses[2].startswith("ARTICLE II")
    assert clauses[3].startswith("ARTICLE III")


def test_real_scan_detects_article_headers_and_ignores_schedule_references(test_docs_dir):
    image_path = test_docs_dir / "section_headers_no_numbers.jpg"
    text = "\n".join(extract_text_from_image(str(image_path)))

    clauses = split_into_clauses(text)

    assert len(clauses) == 4  # preamble + 3 ARTICLE sections
    assert "ARTICLEI" in clauses[1] or "ARTICLE I" in clauses[1]
    assert "PURPOSE" in clauses[1]
    assert clauses[2].startswith("ARTICLE II")
    assert "CAPITAL CONTRIBUTIONS" in clauses[2]
    assert clauses[3].startswith("ARTICLE III")
    assert "DISSOLUTION" in clauses[3]


# Checks clauses of different lengths  come through intact 
def test_handles_clauses_of_very_different_lengths(test_docs_dir):
    image_path = test_docs_dir / "mixed_length_clauses.jpg"
    text = "\n".join(extract_text_from_image(str(image_path)))

    clauses = split_into_clauses(text)

    assert len(clauses) == 4
    assert clauses[0] == "SUPPLY AGREEMENT"
    assert clauses[1] == "1. Definitions Confidential."
    assert clauses[2].startswith("2. Indemnification")
    assert "reasonable legal fees" in clauses[2]
    assert clauses[3] == "3. Notices Notices shall be sent in writing."
