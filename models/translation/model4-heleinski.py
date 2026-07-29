from transformers import pipeline
import sys

print("Loading model...", flush=True)

try:
    translator = pipeline("text2text-generation",
                          model="Helsinki-NLP/opus-mt-en-ur")
    print("Model loaded successfully.", flush=True)
except Exception as e:
    print(f"Error loading model: {e}", flush=True)
    sys.exit(1)

text = [
    "You must pay all costs if someone makes a claim.",
    "Either party can end this contract with 30 days notice.",
    "This contract follows the laws of England and Wales."
]

print(f"Translating: {text}", flush=True)

try:
    result = translator(text, max_length=512)
    print(f"Raw result: {result}", flush=True)
    print(f"Translation: {result[0]['generated_text']}", flush=True)
except Exception as e:
    print(f"Error during translation: {e}", flush=True)