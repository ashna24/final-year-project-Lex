from unittest.mock import MagicMock, patch
from clause_classifier import analyze_contract_clause

CLEAN_CLAUSE = (  # expected Low risk
    "This agreement constitutes the entire agreement between the parties "
    "with respect to its subject matter and supersedes all prior discussions, "
    "representations, or agreements."
)

HIGH_RISK_CLAUSE = (  # predatory penalty clause 
    "If the Tenant is late on rent by even one day, the Landlord may immediately "
    "seize all personal property in the unit, terminate the lease without notice, "
    "and charge a penalty of five times the monthly rent, non-negotiable and "
    "non-refundable under any circumstances."
)


# Checks the result comes back as a dictionary with the right keys
def test_returns_dict_with_expected_keys(require_ollama):
    result = analyze_contract_clause(CLEAN_CLAUSE)

    assert isinstance(result, dict)
    assert set(result.keys()) == {"risk_level", "confidence_score", "explanation"}


# Checks each value in the result is the right data type
def test_returns_expected_value_types(require_ollama):
    result = analyze_contract_clause(CLEAN_CLAUSE)

    assert isinstance(result["risk_level"], str)
    assert isinstance(result["confidence_score"], int)
    assert isinstance(result["explanation"], str)


# Checks the risk level is one of High, Medium, or Low
def test_risk_level_is_a_known_category(require_ollama):
    result = analyze_contract_clause(CLEAN_CLAUSE)

    assert result["risk_level"] in {"High", "Medium", "Low"}


# Checks the explanation text isn't empty
def test_explanation_is_non_empty(require_ollama):
    result = analyze_contract_clause(CLEAN_CLAUSE)

    assert result["explanation"].strip() != ""


# Checks a normal boilerplate clause gets marked Low risk
def test_boilerplate_clause_is_classified_as_low_risk(require_ollama):
    result = analyze_contract_clause(CLEAN_CLAUSE)

    assert result["risk_level"] == "Low"


# Checks predatory clause gets marked High risk
def test_predatory_clause_is_classified_as_high_risk(require_ollama):
    result = analyze_contract_clause(HIGH_RISK_CLAUSE)

    assert result["risk_level"] == "High"


# Checks keep_alive=0 is sent with every request so Ollama unloads the model straight away
def test_sends_keep_alive_zero_to_unload_model_after_response():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "response": '{"risk_level": "Low", "confidence_score": 90, "explanation": "mock"}'
    }

    with patch("clause_classifier.requests.post", return_value=fake_response) as mock_post:
        analyze_contract_clause(CLEAN_CLAUSE)

    mock_post.assert_called_once()
    sent_payload = mock_post.call_args.kwargs["json"]
    assert sent_payload["keep_alive"] == 0
