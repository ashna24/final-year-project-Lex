import sys

from transformers import pipeline

MODEL_NAME = "facebook/nllb-200-distilled-600M"
# FLORES-200 codes
SRC_LANG = "eng_Latn"
TGT_LANG = "urd_Arab"

_translator = None

# Sets up the English to Urdu translator
def load_translator():
    # Loads the English to Urdu NLLB-200 translation pipeline. Downloads model weights on first call.
    return pipeline("translation", model=MODEL_NAME, src_lang=SRC_LANG, tgt_lang=TGT_LANG)

# Reuses the same translator instead of loading it again each time
def get_default_translator():
    global _translator
    if _translator is None:
        _translator = load_translator()
    return _translator


# Translates one English sentence into Urdu
def translate_to_urdu(text, translator=None, max_length=512):
    if translator is None:
        translator = get_default_translator()

    result = translator(text, max_length=max_length)
    return result[0]['translation_text']


if __name__ == "__main__":
    # will run this file directly to translate a few sample sentences
    print("Loading model...", flush=True)
    try:
        translator = load_translator()
        print("Model loaded successfully.", flush=True)
    except Exception as e:
        print(f"Error loading model: {e}", flush=True)
        sys.exit(1)

    sample_sentences = [
        "You must pay all costs if someone makes a claim.",
        "Either party can end this contract with 30 days notice.",
        "This contract follows the laws of England and Wales."
    ]

    for sentence in sample_sentences:
        print(f"Translating: {sentence}", flush=True)
        try:
            translation = translate_to_urdu(sentence, translator=translator)
            print(f"Translation: {translation}", flush=True)
        except Exception as e:
            print(f"Error during translation: {e}", flush=True)
