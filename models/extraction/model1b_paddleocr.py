import gc
import tempfile

import pymupdf
from paddleocr import PaddleOCR

# Sharp enough for OCR without making huge page images
PDF_RENDER_DPI = 200

_ocr_engine = None


# Sets up a new PaddleOCR reader
def load_ocr_engine(lang='en', use_angle_cls=False):
    """Create a PaddleOCR engine instance. Model weights load on first call."""
    return PaddleOCR(use_angle_cls=use_angle_cls, lang=lang)


# Reuses the same OCR reader instead of creating a new one each time
def get_default_ocr_engine():
    """Lazily initialize and cache a module-level PaddleOCR engine."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = load_ocr_engine()
    return _ocr_engine


# Reads the text out of an image file
def extract_text_from_image(image_path, ocr_engine=None):
    """Run OCR on image_path and return the recognized lines of text as a list of strings."""
    if ocr_engine is None:
        ocr_engine = get_default_ocr_engine()

    result = ocr_engine.ocr(image_path)

    if result and len(result) > 0:
        return result[0].get('rec_texts', [])  # recognized lines live under this key
    return []


# Renders every page of a PDF to an image and OCRs each one in turn
def extract_text_from_pdf(pdf_path, ocr_engine=None):
    lines = []
    document = pymupdf.open(pdf_path)
    try:
        for page in document:
            pixmap = page.get_pixmap(dpi=PDF_RENDER_DPI)
            with tempfile.NamedTemporaryFile(suffix=".png") as page_image:
                pixmap.save(page_image.name)
                lines.extend(extract_text_from_image(page_image.name, ocr_engine=ocr_engine))
    finally:
        document.close()
    return lines


# Drops the cached OCR engine and forces Python to give the freed memory back to the OS
def unload_ocr_engine():
    global _ocr_engine
    _ocr_engine = None
    gc.collect()


if __name__ == "__main__":
    print("\n--- EXTRACTING LEGAL TEXT ---")
    for sentence in extract_text_from_image('numbered_clean.jpg'):
        print(sentence)
