from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

SAMPLE_IMAGE_PATH = Path(__file__).resolve().parent.parent / "models" / "test_docs" / "numbered_clean.jpg"
SAMPLE_IMAGE_BYTES = SAMPLE_IMAGE_PATH.read_bytes()

SAMPLE_PDF_PATH = Path(__file__).resolve().parent.parent / "models" / "test_docs" / "numbered_clean.pdf"
SAMPLE_PDF_BYTES = SAMPLE_PDF_PATH.read_bytes()

FAKE_RESULTS = [
    {"clause_text": "SERVICE AGREEMENT ...", "risk_level": "Low", "confidence_score": 90, "explanation": "mock"},
]

# Checks the health endpoint reports OK without touching the pipeline at all
def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Checks a request with no file at all gets a clear 400
def test_analyze_with_no_file_returns_400():
    response = client.post("/analyze")

    assert response.status_code == 400
    assert "no file" in response.json()["detail"].lower()


# Checks an empty upload gets a clear 400 instead of being sent into the pipeline
def test_analyze_with_empty_file_returns_400():
    response = client.post("/analyze", files={"file": ("empty.jpg", b"", "image/jpeg")})

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# Checks a file that isn't a real image gets a clear 400 not a pipeline crash
def test_analyze_with_invalid_image_returns_400():
    response = client.post("/analyze", files={"file": ("not_an_image.txt", b"this is not an image", "text/plain")})

    assert response.status_code == 400
    assert "not a valid image" in response.json()["detail"].lower()


# Checks a fake PDF gets a clear 400 instead of crashing
def test_analyze_with_invalid_pdf_returns_400():
    response = client.post(
        "/analyze", files={"file": ("not_a_real.pdf", b"this is not a real pdf", "application/pdf")}
    )

    assert response.status_code == 400
    assert "not a valid pdf" in response.json()["detail"].lower()


# Checks a real PDF upload is accepted and reaches the pipeline as a .pdf path
def test_analyze_with_valid_pdf_reaches_the_pipeline():
    with patch("api.main.process_document", return_value=FAKE_RESULTS) as mock_process:
        response = client.post(
            "/analyze", files={"file": ("contract.pdf", SAMPLE_PDF_BYTES, "application/pdf")}
        )

    assert response.status_code == 200
    assert response.json() == FAKE_RESULTS
    call_path = mock_process.call_args.args[0]
    assert call_path.endswith(".pdf")


# Checks a PDF with no file extension still reaches the pipeline as .pdf
# The content type says PDF so the temp file must end in .pdf
def test_analyze_with_pdf_content_type_but_no_extension_reaches_the_pipeline():
    with patch("api.main.process_document", return_value=FAKE_RESULTS) as mock_process:
        response = client.post(
            "/analyze", files={"file": ("contract", SAMPLE_PDF_BYTES, "application/pdf")}
        )

    assert response.status_code == 200
    call_path = mock_process.call_args.args[0]
    assert call_path.endswith(".pdf")


# Checks a successful analysis returns the pipeline's own result list as JSON
def test_analyze_with_mocked_pipeline_returns_results():
    with patch("api.main.process_document", return_value=FAKE_RESULTS) as mock_process:
        response = client.post("/analyze", files={"file": ("numbered_clean.jpg", SAMPLE_IMAGE_BYTES, "image/jpeg")})

    assert response.status_code == 200
    assert response.json() == FAKE_RESULTS
    assert mock_process.call_args.kwargs["translate"] is False


# Checks the translate query parameter is actually passed through to the pipeline
def test_analyze_passes_translate_flag_through():
    with patch("api.main.process_document", return_value=FAKE_RESULTS) as mock_process:
        response = client.post(
            "/analyze?translate=true",
            files={"file": ("numbered_clean.jpg", SAMPLE_IMAGE_BYTES, "image/jpeg")},
        )

    assert response.status_code == 200
    assert mock_process.call_args.kwargs["translate"] is True


# Checks an unexpected pipeline failure returns a generic 500
def test_analyze_internal_error_returns_generic_500():
    with patch("api.main.process_document", side_effect=RuntimeError("boom - sensitive internal detail")):
        response = client.post("/analyze", files={"file": ("numbered_clean.jpg", SAMPLE_IMAGE_BYTES, "image/jpeg")})

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "boom" not in detail
    assert "sensitive internal detail" not in detail


# Real end-to-end: real OCR, real Llama classification, real NLLB translation, through the actual API
def test_analyze_real_end_to_end():
    response = client.post(
        "/analyze?translate=true",
        files={"file": ("numbered_clean.jpg", SAMPLE_IMAGE_BYTES, "image/jpeg")},
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 5
    for result in results:
        assert "clause_text" in result
        if result.get("status") != "skipped":
            assert "risk_level" in result
            assert "explanation_urdu" in result


# Checks a request with no body/text field at all gets a clear 400
def test_translate_with_no_text_returns_400():
    response = client.post("/translate", json={})

    assert response.status_code == 400
    assert "no text" in response.json()["detail"].lower()


# Checks an empty or blank text field gets a clear 400 and never reaches NLLB
def test_translate_with_empty_text_returns_400():
    response = client.post("/translate", json={"text": "   "})

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# Checks a good translation returns the output without touching OCR or classification
def test_translate_with_mocked_translator_returns_translation():
    with (
        patch("api.main.translate_to_urdu", return_value="اردو ترجمہ") as mock_translate,
        patch("api.main.process_document") as mock_process,
    ):
        response = client.post("/translate", json={"text": "This is a test clause."})

    assert response.status_code == 200
    assert response.json() == {"translation": "اردو ترجمہ"}
    mock_translate.assert_called_once_with("This is a test clause.")
    mock_process.assert_not_called()


# Checks a translator failure returns a generic 500 and hides the real error
def test_translate_internal_error_returns_generic_500():
    with patch("api.main.translate_to_urdu", side_effect=RuntimeError("boom - sensitive internal detail")):
        response = client.post("/translate", json={"text": "This is a test clause."})

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "boom" not in detail
    assert "sensitive internal detail" not in detail


# Real NLLB call through the API with no OCR or classification
def test_translate_real_end_to_end():
    response = client.post(
        "/translate",
        json={"text": "The tenant must pay rent on the first day of each month."},
    )

    assert response.status_code == 200
    translation = response.json()["translation"]
    assert isinstance(translation, str)
    assert len(translation.strip()) > 0


# Checks the translator is still unloaded when translation fails
def test_translate_finally_unloads_translator_even_on_failure():
    with (
        patch("api.main.translate_to_urdu", side_effect=RuntimeError("boom")),
        patch("api.main.unload_translator") as mock_unload,
    ):
        response = client.post("/translate", json={"text": "This is a test clause."})

    assert response.status_code == 500
    mock_unload.assert_called_once()


# Checks NLLB is not left in memory after /translate So a later /analyze call never runs next to a loaded translator
def test_translate_then_analyze_never_leaves_both_models_resident():
    import models.extraction.model1b_paddleocr as ocr_module
    import models.translation.model4_nllb as nllb_module

    ocr_module._ocr_engine = object()  # pretends PaddleOCR is still loaded

    try:
        translate_response = client.post(
            "/translate", json={"text": "The tenant must pay rent on the first day of each month."}
        )
        assert translate_response.status_code == 200
        # The translator should be unloaded by now
        assert nllb_module._translator is None

        with patch("api.main.process_document", return_value=[]) as mock_process:
            analyze_response = client.post(
                "/analyze?translate=false",
                files={"file": ("numbered_clean.jpg", SAMPLE_IMAGE_BYTES, "image/jpeg")},
            )
        assert analyze_response.status_code == 200
        mock_process.assert_called_once()

        # NLLB stays unloaded so PaddleOCR and NLLB were never in memory together
        assert nllb_module._translator is None
    finally:
        ocr_module._ocr_engine = None
        nllb_module._translator = None
