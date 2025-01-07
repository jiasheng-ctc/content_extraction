from api.ocr_extractor import extract_text_from_pdf
from api.bedrock_client import invoke_claude
from models.model_params import model_params

def process_pdf(file_path):
    extracted_text = extract_text_from_pdf(file_path)
    prompt = f"""Given the following document:

    {extracted_text}

    Extract key information such as names, date of signing, place of signing. Provide a structured response in JSON format."""
    return invoke_claude(prompt, model_params)
