from unittest.mock import patch
import model1b_paddleocr
from model1b_paddleocr import extract_text_from_image, get_default_ocr_engine, unload_ocr_engine


# Checks the OCR function actually reads text from a real image
def test_extracts_non_empty_text_from_clean_image(test_docs_dir):
    image_path = test_docs_dir / "numbered_clean.jpg"

    result = extract_text_from_image(str(image_path))

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(line, str) for line in result)
    assert any(line.strip() != "" for line in result)


# Checks the function returns an empty list when OCR finds nothing
def test_returns_empty_list_when_no_result():
    class FakeOCREngine:  
        def ocr(self, image_path):
            return []

    result = extract_text_from_image("unused.jpg", ocr_engine=FakeOCREngine())

    assert result == []


# Checks unloading clears the cache and the next call builds a fresh engine
def test_unload_ocr_engine_clears_cache_and_forces_fresh_reload():
    created = []

    class FakeOCREngine:
        def __init__(self):
            created.append(self)

    # Other tests in this file cache a real engine so save it and put it back after
    # This stops the fake engine leaking into later tests
    original_engine = model1b_paddleocr._ocr_engine
    model1b_paddleocr._ocr_engine = None
    try:
        with patch("model1b_paddleocr.load_ocr_engine", side_effect=FakeOCREngine):
            first_engine = get_default_ocr_engine()
            assert model1b_paddleocr._ocr_engine is first_engine

            unload_ocr_engine()
            assert model1b_paddleocr._ocr_engine is None

            second_engine = get_default_ocr_engine()

        assert len(created) == 2  # a fresh engine was built and the old one was not reused
        assert second_engine is not first_engine
        assert model1b_paddleocr._ocr_engine is second_engine
    finally:
        model1b_paddleocr._ocr_engine = original_engine
