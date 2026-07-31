from model4_heleinski import translate_to_urdu

ENGLISH_SENTENCE = "Either party can end this contract with 30 days notice."


# Checks the translator gives back a proper text result
def test_translates_english_input_to_a_string():
    result = translate_to_urdu(ENGLISH_SENTENCE)

    assert isinstance(result, str)
    assert result.strip() != ""


# Checks the function correctly uses a custom translator when given one
def test_uses_provided_translator_if_given():
    calls = {}

    class FakeTranslator:  # stub so this test doesn't need the real Helsinki model
        def __call__(self, text, max_length=512):
            calls["text"] = text
            calls["max_length"] = max_length
            return [{"generated_text": "fake translation"}]

    result = translate_to_urdu(ENGLISH_SENTENCE, translator=FakeTranslator())

    assert result == "fake translation"
    assert calls["text"] == ENGLISH_SENTENCE
