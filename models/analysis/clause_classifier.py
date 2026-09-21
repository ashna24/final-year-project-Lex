import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

# Forces the model to respond with strict, parseable JSON in these three fields
SYSTEM_PROMPT = """You are an expert legal AI assistant designed to help non-lawyers understand contracts.
Analyze the following clause and output your response STRICTLY as a JSON object with the following three keys:
1. "risk_level": A string that must be exactly "High", "Medium", or "Low".
   - Use "High" for severe financial penalties, predatory traps, extreme liability shifts, or highly unusual restrictions.
   - Use "Medium" for standard industry obligations, temporary restrictions, or vague timelines (e.g., standard 6-month non-solicitation, "reasonable" effort clauses).
   - Use "Low" for standard legal boilerplate (e.g., severability, basic jurisdiction).
2. "confidence_score": An integer from 0 to 100 representing how confident you are in your classification.
3. "explanation": A plain English explanation of what this clause actually means, written at a 12-year-old reading level.
Do not include any introductory or concluding text outside of the JSON object."""


def analyze_contract_clause(clause_text):
    """Classify a single contract clause via the local Ollama llama3.2 model.

    Returns a dict with keys: risk_level (str), confidence_score (int), explanation (str).
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nClause to analyze:\n{clause_text}",
        "format": "json",
        "stream": False,
        # Unloads the model right after each reply so it does not stay in memory next to NLLB
        "keep_alive": 0,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            parsed_data = json.loads(result['response'])  # model's JSON reply is nested 

            return {
                "risk_level": parsed_data.get("risk_level", "Unknown"),
                "confidence_score": parsed_data.get("confidence_score", 0),
                "explanation": parsed_data.get("explanation", "No explanation provided."),
            }

        return {  # Ollama responded with a non-200 status
            "risk_level": "Error",
            "confidence_score": 0,
            "explanation": f"API Error: {response.status_code}",
        }
    except Exception as e:  # Ollama unreachable or request failed
        return {
            "risk_level": "Error",
            "confidence_score": 0,
            "explanation": f"Could not connect to local Ollama instance: {str(e)}",
        }
