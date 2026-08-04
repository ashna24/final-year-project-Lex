from model1b_paddleocr import extract_text_from_image


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
