from pathlib import Path
from unittest.mock import patch

import pytest

from models.extraction.model1b_paddleocr import extract_text_from_image
from models.pipeline.run_pipeline import process_document

TEST_DOC_IMAGE = str(Path(__file__).resolve().parent.parent / "models" / "test_docs" / "numbered_clean.jpg")

# A fake classifier result used instead of actually calling Ollama
FAKE_ANALYSIS = {
    "risk_level": "Low",
    "confidence_score": 90,
    "explanation": "This is a mocked explanation.",
}


# Reads the real sample contract once so the tests below don't redo OCR each time
@pytest.fixture(scope="module")
def real_ocr_lines():
    return extract_text_from_image(TEST_DOC_IMAGE)


# Checks a real document gets fully classified clause by clause
def test_processes_real_document_into_classified_clauses(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS) as mock_analyze:
        results = process_document("numbered_clean.jpg")

    assert len(results) == 5  # the intro paragraph plus the 4 numbered clauses
    assert mock_analyze.call_count == 5
    for result in results:
        assert set(result.keys()) == {"clause_text", "risk_level", "confidence_score", "explanation"}
        assert result["risk_level"] == "Low"
        assert result["confidence_score"] == 90
    assert results[1]["clause_text"].startswith("1.")
    assert results[2]["clause_text"].startswith("2.")
    assert results[3]["clause_text"].startswith("3.")
    assert results[4]["clause_text"].startswith("4.")


# Checks one failed clause doesn't stop the others from being processed
def test_classifier_failure_on_one_clause_does_not_stop_the_others(real_ocr_lines):
    def flaky_analyze(clause_text):
        if clause_text.startswith("2."):
            raise ConnectionError("Ollama is not running")
        return FAKE_ANALYSIS

    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", side_effect=flaky_analyze):
        results = process_document("numbered_clean.jpg")

    assert len(results) == 5  # every clause still gets a result
    assert results[2]["risk_level"] == "Error"
    assert "Ollama is not running" in results[2]["explanation"]
    assert results[0]["risk_level"] == "Low"  # the other clauses still work fine
    assert results[1]["risk_level"] == "Low"
    assert results[3]["risk_level"] == "Low"
    assert results[4]["risk_level"] == "Low"


# Checks the classifier's own error message is passed through as is
def test_classifier_own_error_response_passes_through(real_ocr_lines):
    error_analysis = {
        "risk_level": "Error",
        "confidence_score": 0,
        "explanation": "Could not connect to local Ollama instance: ...",
    }

    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=error_analysis):
        results = process_document("numbered_clean.jpg")

    assert len(results) == 5
    for result in results:
        assert result["risk_level"] == "Error"
        assert "clause_text" in result


# Checks a blank image returns an empty list
def test_returns_empty_list_when_ocr_finds_no_text():
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=[]):
        with patch("models.pipeline.run_pipeline.analyze_contract_clause") as mock_analyze:
            results = process_document("blank.jpg")

    assert results == []
    mock_analyze.assert_not_called()


# Checks a broken image file is caught and returns an empty list
def test_returns_empty_list_when_ocr_raises():
    with patch("models.pipeline.run_pipeline.extract_text_from_image", side_effect=OSError("cannot identify image file")):
        results = process_document("corrupt.jpg")

    assert results == []
