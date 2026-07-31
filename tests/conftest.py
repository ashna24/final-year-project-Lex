from pathlib import Path

import pytest
import requests

TEST_DOCS_DIR = Path(__file__).resolve().parent.parent / "models" / "test_docs"  # sample images for OCR tests

OLLAMA_HEALTH_URL = "http://localhost:11434/api/tags"  # used as a reachability check


# Gives tests the folder path where sample images are stored
@pytest.fixture
def test_docs_dir():
    return TEST_DOCS_DIR


# Checks if Ollama is up and reachable
def ollama_is_running():
    try:
        requests.get(OLLAMA_HEALTH_URL, timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False


# Skips a test if Ollama isn't running
@pytest.fixture
def require_ollama():
    # Skips the test instead of hanging/failing when Ollama isn't running locally
    if not ollama_is_running():
        pytest.skip("Ollama server is not running on localhost:11434")
