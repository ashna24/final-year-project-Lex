"""Standalone comparison harness for evaluating candidate Urdu translation approaches.
runs each candidate against a fixed set of 5 real Llama-generated clause explanations and 
records the output. 
"""

import json
from pathlib import Path

import requests

from models.translation.model4_heleinski import translate_to_urdu as helsinki_translate

OLLAMA_URL = "http://localhost:11434/api/generate"
LLAMA_MODEL_NAME = "llama3.2"

# facebook's smallest/distilled NLLB-200 checkpoint (
NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"

# FLORES-200 codes
NLLB_SRC_LANG = "eng_Latn"
NLLB_TGT_LANG = "urd_Arab"

# Fixed test set of 5 english explanations produced in earlier testing. 
TEST_STRINGS = [
    "This part of the contract says who's making the agreement. The Company (Horizon "
    "Consulting Ltd.) is the one creating this deal, and the Contractor is the person "
    "signing it.",

    "This clause says that the person called the 'Contractor' will do their job right and "
    "give good advice about using software. It doesn't say what specific things they have "
    "to do or how long it will take, so it's a pretty standard part of any contract.",

    "This clause says that the company must pay the contractor money within 30 days after "
    "they send an invoice. If it takes longer than 30 days, the company will have to pay "
    "extra interest on the payment.",

    "This clause means that the person hired (Contractor) promises not to share any secret "
    "or private information from the company they work for with anyone else. Even after "
    "their contract ends, they still can't share this info.",

    "This clause means that either side can end the agreement with 14 days' written notice. "
    "This is a standard provision that allows businesses to leave contracts if they need to.",
]

_nllb_translator = None


# Lazily loads and caches the NLLB pipeline (downloads weights on first call)
def _get_nllb_translator():
    global _nllb_translator
    if _nllb_translator is None:
        from transformers import pipeline
        _nllb_translator = pipeline(
            "translation",
            model=NLLB_MODEL_NAME,
            src_lang=NLLB_SRC_LANG,
            tgt_lang=NLLB_TGT_LANG,
        )
    return _nllb_translator


# Candidate 1: the existing Helsinki-NLP opus-mt-en-ur model
def translate_with_helsinki(text):
    return helsinki_translate(text)


# Candidate 2: Meta's NLLB-200
def translate_with_nllb(text):
    translator = _get_nllb_translator()
    result = translator(text, max_length=512)
    return result[0]["translation_text"]


# Candidate 3: Llama 3.2 prompted to translate 
def translate_with_llama_prompt(text):
    prompt = (
        "Translate the following English text into natural, accurate Urdu. "
        "Preserve the full meaning exactly - do not summarize, add, or omit anything. "
        "Respond with ONLY the Urdu translation. Do not include the English text, "
        "notes, explanations, or any other commentary.\n\n"
        f"English text:\n{text}"
    )
    payload = {
        "model": LLAMA_MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    return result["response"].strip()


CANDIDATES = [
    ("HELSINKI_NLP", translate_with_helsinki),
    ("NLLB_200", translate_with_nllb),
    ("LLAMA_PROMPT", translate_with_llama_prompt),
]


# Runs every candidate against every test string. A failure on one candidate is recorded inline
def run_comparison():
    all_results = []

    for i, text in enumerate(TEST_STRINGS, start=1):
        clause_result = {"clause_number": i, "original_en": text, "translations": {}}

        print(f"=== Clause {i} ===")
        print(f"Original (EN): {text}")

        for name, translate_fn in CANDIDATES:
            try:
                translation = translate_fn(text)
            except Exception as e:
                translation = f"[ERROR: {type(e).__name__}: {e}]"
            clause_result["translations"][name] = translation
            print(f"{name}: {translation}")

        print()
        all_results.append(clause_result)

    return all_results


# Writes a human-readable Markdown record of the comparison
def write_markdown_report(all_results, output_path):
    lines = ["# Urdu Translation Candidate Comparison", ""]
    for r in all_results:
        lines.append(f"## Clause {r['clause_number']}")
        lines.append("")
        lines.append(f"**Original (EN):** {r['original_en']}")
        lines.append("")
        for name, translation in r["translations"].items():
            lines.append(f"**{name}:** {translation}")
            lines.append("")
        lines.append("---")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    results = run_comparison()

    output_dir = Path(__file__).resolve().parent
    markdown_path = output_dir / "results.md"
    json_path = output_dir / "results.json"

    write_markdown_report(results, markdown_path)
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Results written to {markdown_path} and {json_path}")
