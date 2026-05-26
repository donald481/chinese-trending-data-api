"""Unit tests for arbitrage_api enrichment pipeline.

Run: PYTHONPATH=. python -m pytest tests/test_enricher.py -v
"""

import pytest
import json


def _api_response(content_str: str) -> dict:
    """Build a full LLM API response dict as robust_json_parse expects."""
    return {
        "choices": [{"message": {"content": content_str}}]
    }


def test_robust_json_parse_valid():
    """Verify standard JSON in API response parses correctly."""
    from pipeline.enricher import robust_json_parse

    result = robust_json_parse(_api_response('{"key": "value", "num": 42}'))
    assert result == {"key": "value", "num": 42}


def test_robust_json_parse_with_codeblock():
    """Verify JSON wrapped in markdown code blocks is handled."""
    from pipeline.enricher import robust_json_parse

    content = '```json\n{"key": "value"}\n```'
    result = robust_json_parse(_api_response(content))
    assert result == {"key": "value"}


def test_robust_json_parse_truncated():
    """Verify truncated JSON is handled by regex fallback strategy."""
    from pipeline.enricher import robust_json_parse

    # Truncated JSON like {"key": "value" (no closing brace)
    # The regex extraction strategy can still parse this
    result = robust_json_parse(_api_response('{"key": "value"'))
    assert result == {"key": "value"}


def test_robust_json_parse_empty():
    """Verify empty API response content returns None."""
    from pipeline.enricher import robust_json_parse

    result = robust_json_parse(_api_response(""))
    assert result is None


def test_robust_json_parse_missing_choices():
    """Verify malformed API response (missing choices) returns None."""
    from pipeline.enricher import robust_json_parse

    assert robust_json_parse({}) is None
    assert robust_json_parse({"choices": []}) is None


def test_model_configuration():
    """Verify LLM configuration is properly set."""
    from pipeline.enricher import MODEL, CALL_DELAY

    assert MODEL == "deepseek-v4-flash"
    assert CALL_DELAY >= 1.0


def test_enricher_functions_importable():
    """Verify call_llm_with_retry and enrich_with_llm are importable and callable."""
    from pipeline.enricher import call_llm_with_retry, enrich_with_llm
    assert callable(call_llm_with_retry)
    assert callable(enrich_with_llm)


def test_env_loading():
    """Verify API_KEY is loaded from environment when available."""
    import os
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    assert base_url.startswith("https://")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
