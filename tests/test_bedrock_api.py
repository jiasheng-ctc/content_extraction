import pytest
from src.api.bedrock_client import invoke_claude

def test_invoke_claude():
    prompt = "Extract the key details from the document."
    model_params = {
        "model_id": "anthropic.claude-3-sonnet:2025-01-01-v1",
        "region": "us-east-1",
        "max_tokens": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }
    response = invoke_claude(prompt, model_params)
    assert response is not None
