import boto3
import json

def invoke_claude(prompt, model_params):
    try:
        client = boto3.client("bedrock-runtime", region_name=model_params['region'])

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": model_params["max_tokens"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": model_params["temperature"],
            "top_p": model_params["top_p"]
        }

        response = client.invoke_model(
            body=json.dumps(payload),
            modelId=model_params["model_id"],
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response["body"].read().decode('utf-8'))
        return response_body.get("content", [])

    except client.exceptions.ClientError as e:
        raise RuntimeError(f"Bedrock API Client Error: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
