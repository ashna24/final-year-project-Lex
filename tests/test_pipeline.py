from pathlib import Path
from unittest.mock import patch
import pytest

from models.extraction.model1b_paddleocr import extract_text_from_image
from models.pipeline.run_pipeline import process_document

TEST_DOC_IMAGE = str(Path(__file__).resolve().parent.parent / "models" / "test_docs" / "numbered_clean.jpg")

# A fake classifier result used instead of calling Ollama
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

    assert len(results) == 5  # every clause  gets a result
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


# Checks the exact word count boundary: fewer than 5 words gets skipped, 5+ gets classified
def test_word_count_boundary_for_skipping():
    fake_lines = ["Four short words here.", "This has exactly five words."]

    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=fake_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS) as mock_analyze:
        results = process_document("doc.jpg")

    assert len(results) == 2
    assert results[0]["status"] == "skipped"
    assert results[0]["reason"] == "insufficient content for classification"
    assert "risk_level" not in results[0]
    assert results[1]["risk_level"] == "Low"
    assert mock_analyze.call_count == 1  # only the 5 word clause was actually sent to the classifier


# Checks a real document with a bare 2-word title skips unmarked title, every numbered clause gets classified 
def test_real_document_with_a_bare_title_skips_it(test_docs_dir):
    image_path = str(test_docs_dir / "mixed_length_clauses.jpg")

    with patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS) as mock_analyze:
        results = process_document(image_path)

    assert len(results) == 4  
    assert results[0]["clause_text"] == "SUPPLY AGREEMENT"
    assert results[0]["status"] == "skipped"  # unmarked preamble, under the word threshold
    assert results[1]["risk_level"] == "Low"  # "1. Definitions Confidential." is short but marked
    assert results[2]["risk_level"] == "Low"  # the long indemnification clause gets classified
    assert results[3]["risk_level"] == "Low"  # "3. Notices.." has enough words too
    assert mock_analyze.call_count == 3


# Checks a short but marker delimited clause is still classified
def test_short_marked_clause_is_not_skipped():
    fake_lines = ["1. Confidential.", "2. This is a longer clause with plenty of words to spare."]

    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=fake_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS) as mock_analyze:
        results = process_document("doc.jpg")

    assert len(results) == 2
    assert results[0]["clause_text"] == "1. Confidential."  # only 2 words
    assert "status" not in results[0]  # classified despite being under the word threshold
    assert results[0]["risk_level"] == "Low"
    assert mock_analyze.call_count == 2


# Checks translate= False(default) never touches the translator
def test_translate_false_does_not_call_translator(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS), \
         patch("models.pipeline.run_pipeline.translate_to_urdu") as mock_translate:
        results = process_document("numbered_clean.jpg")

    mock_translate.assert_not_called()
    for result in results:
        assert "explanation_urdu" not in result


# Checks translate= True adds an explanation urdu field for every classified clause
def test_translate_true_adds_urdu_explanation(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS), \
         patch("models.pipeline.run_pipeline.translate_to_urdu", return_value="مترجم وضاحت") as mock_translate:
        results = process_document("numbered_clean.jpg", translate=True)

    assert mock_translate.call_count == 5  # once per classified clause
    for result in results:
        assert result["explanation_urdu"] == "مترجم وضاحت"
    mock_translate.assert_any_call(FAKE_ANALYSIS["explanation"])


# Checks skipped clauses are never sent for translation, even when translate= True
def test_skipped_clauses_are_not_translated():
    fake_lines = ["Four short words here.", "This has exactly five words."]

    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=fake_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS), \
         patch("models.pipeline.run_pipeline.translate_to_urdu", return_value="ترجمہ") as mock_translate:
        results = process_document("doc.jpg", translate=True)

    assert results[0]["status"] == "skipped"
    assert "explanation_urdu" not in results[0]
    assert results[1]["explanation_urdu"] == "ترجمہ"
    assert mock_translate.call_count == 1  # only the classified clause was translated


# Checks a clause where classification itself failed is not sent for translation either
def test_classifier_error_clauses_are_not_translated(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", side_effect=ConnectionError("Ollama down")), \
         patch("models.pipeline.run_pipeline.translate_to_urdu") as mock_translate:
        results = process_document("numbered_clean.jpg", translate=True)

    for result in results:
        assert result["risk_level"] == "Error"
        assert "explanation_urdu" not in result
    mock_translate.assert_not_called()


# Checks a translation failure doesn't discard the English classification already gathered
def test_translation_failure_keeps_english_results_intact(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS), \
         patch("models.pipeline.run_pipeline.translate_to_urdu", side_effect=TimeoutError("translation timed out")):
        results = process_document("numbered_clean.jpg", translate=True)

    for result in results:
        assert result["risk_level"] == "Low"
        assert result["confidence_score"] == 90
        assert result["explanation"] == FAKE_ANALYSIS["explanation"]
        assert result["explanation_urdu"] is None


# Real end-to-end test- however the classifier is still mocked
def test_real_document_translation_end_to_end(real_ocr_lines):
    fake_analysis = {
        "risk_level": "Medium",
        "confidence_score": 75,
        "explanation": "The company must pay the contractor within 30 days or interest applies.",
    }

    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=fake_analysis):
        results = process_document("numbered_clean.jpg", translate=True)

    assert len(results) == 5
    for result in results:
        assert isinstance(result["explanation_urdu"], str)
        assert result["explanation_urdu"].strip() != ""


# Checks OCR is unloaded right after extraction and before classification starts
def test_unload_ocr_engine_called_after_successful_extraction(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS), \
         patch("models.pipeline.run_pipeline.unload_ocr_engine") as mock_unload:
        process_document("numbered_clean.jpg")

    mock_unload.assert_called_once()


# Checks the OCR engine is still unloaded even when extraction itself raises
def test_unload_ocr_engine_called_even_when_extraction_raises():
    with patch("models.pipeline.run_pipeline.extract_text_from_image", side_effect=OSError("cannot identify image file")), \
         patch("models.pipeline.run_pipeline.unload_ocr_engine") as mock_unload:
        results = process_document("corrupt.jpg")

    assert results == []
    mock_unload.assert_called_once()


# Checks unload_translator still runs if something fails while processing clauses
def test_unload_translator_called_even_when_clause_processing_raises(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline._process_clause", side_effect=RuntimeError("unexpected failure")), \
         patch("models.pipeline.run_pipeline.unload_translator") as mock_unload:
        with pytest.raises(RuntimeError):
            process_document("numbered_clean.jpg", translate=True)

    mock_unload.assert_called_once()


# Checks unload_translator is never invoked at all when translate=False
def test_unload_translator_not_called_when_translate_false(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines), \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS), \
         patch("models.pipeline.run_pipeline.unload_translator") as mock_unload:
        process_document("numbered_clean.jpg", translate=False)

    mock_unload.assert_not_called()


# Checks a .pdf path goes to the PDF extraction and not the image one
def test_pdf_path_is_routed_to_pdf_extraction():
    with patch("models.pipeline.run_pipeline.extract_text_from_pdf", return_value=["Clause one is fine."]) as mock_pdf, \
         patch("models.pipeline.run_pipeline.extract_text_from_image") as mock_image, \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS):
        process_document("contract.pdf")

    mock_pdf.assert_called_once_with("contract.pdf")
    mock_image.assert_not_called()


# Checks a .PDF path (uppercase extension) is still routed correctly
def test_pdf_path_routing_is_case_insensitive():
    with patch("models.pipeline.run_pipeline.extract_text_from_pdf", return_value=[]) as mock_pdf, \
         patch("models.pipeline.run_pipeline.extract_text_from_image") as mock_image:
        process_document("CONTRACT.PDF")

    mock_pdf.assert_called_once_with("CONTRACT.PDF")
    mock_image.assert_not_called()


# Checks other file types still go through the normal image extraction
def test_non_pdf_path_is_routed_to_image_extraction(real_ocr_lines):
    with patch("models.pipeline.run_pipeline.extract_text_from_image", return_value=real_ocr_lines) as mock_image, \
         patch("models.pipeline.run_pipeline.extract_text_from_pdf") as mock_pdf, \
         patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS):
        process_document("numbered_clean.jpg")

    mock_image.assert_called_once_with("numbered_clean.jpg")
    mock_pdf.assert_not_called()


# Real PDF built from numbered_clean.jpg run through the full pipeline
def test_processes_a_real_pdf_into_classified_clauses():
    pdf_path = str(Path(__file__).resolve().parent.parent / "models" / "test_docs" / "numbered_clean.pdf")

    with patch("models.pipeline.run_pipeline.analyze_contract_clause", return_value=FAKE_ANALYSIS) as mock_analyze:
        results = process_document(pdf_path)

    assert len(results) == 5  # same document content as numbered_clean.jpg
    assert mock_analyze.call_count == 5
    for result in results:
        assert result["risk_level"] == "Low"
