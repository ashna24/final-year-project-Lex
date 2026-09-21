from unittest.mock import patch
import model4_nllb
from model4_nllb import get_default_translator, translate_to_urdu, unload_translator

ENGLISH_SENTENCE = "Either party can end this contract with 30 days notice."


# Checks the translator gives back a proper text result
def test_translates_english_input_to_a_string():
    result = translate_to_urdu(ENGLISH_SENTENCE)

    assert isinstance(result, str)
    assert result.strip() != ""


# Checks the function correctly uses a custom translator when given one
def test_uses_provided_translator_if_given():
    calls = {}

    class FakeTranslator:  # stub so this test doesn't need the real NLLB model
        def __call__(self, text, max_length=512):
            calls["text"] = text
            calls["max_length"] = max_length
            return [{"translation_text": "fake translation"}]

    result = translate_to_urdu(ENGLISH_SENTENCE, translator=FakeTranslator())

    assert result == "fake translation"
    assert calls["text"] == ENGLISH_SENTENCE


# Checks unloading clears the cache and the next call builds a fresh translator
def test_unload_translator_clears_cache_and_forces_fresh_reload():
    created = []

    class FakeTranslator:
        def __init__(self):
            created.append(self)

    # An earlier test caches a real translator so save it and put it back after
    # This stops the fake translator leaking into later tests
    original_translator = model4_nllb._translator
    model4_nllb._translator = None
    try:
        with patch("model4_nllb.load_translator", side_effect=FakeTranslator):
            first_translator = get_default_translator()
            assert model4_nllb._translator is first_translator

            unload_translator()
            assert model4_nllb._translator is None

            second_translator = get_default_translator()

        assert len(created) == 2  # a fresh translator was built and the old one was not reused
        assert second_translator is not first_translator
        assert model4_nllb._translator is second_translator
    finally:
        model4_nllb._translator = original_translator
