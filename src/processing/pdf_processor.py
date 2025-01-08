from rhubarb import DocAnalysis, LanguageModels
from models.model_params import model_params
import boto3

def process_pdf(file_path):
    session = boto3.Session(region_name=model_params["region"])
    doc_analysis = DocAnalysis(file_path=file_path, boto3_session=session)
    
    ner_response = doc_analysis.run_entity(
        message=(
            "Extract key information such as:"
            "\n- Contract or Reference Number"
            "\n- Service Hotline"
            "\n- Customer Name"
            "\n- Period"
            "\n- Main Contact Person"
        ),
        entities=model_params["ner_entities"]
    )

    summary_response = doc_analysis.run(
        message=(
            "Summarize this document briefly, including:"
            "\n- Contract or Reference Number"
            "\n- Service Hotline"
            "\n- Customer Name"
            "\n- Period"
            "\n- Main Contact Person"
        )
    )

    masking_prompt = (
        "Mask sensitive details in this document, including:"
        "\n- Contract or Reference Numbers"
        "\n- Personal Details"
        "\n- Any other identifiable or sensitive information. "
        "Replace sensitive information with appropriate placeholders."
    )
    masked_response = doc_analysis.run(
        message=masking_prompt
    )

    print("\n[INFO] Processing the PDF file using Rhubarb...")

    print("\n[INFO] Named Entity Recognition:")
    print(format_ner_output(ner_response))

    print("\n[INFO] Summary of the Document:")
    print(format_summary_output(summary_response))

    print("\n[INFO] Masked Document:")
    print(format_masked_output(masked_response))

    return {
        "Named Entity Recognition": ner_response,
        "Summary": summary_response,
        "Masked Document": masked_response,
    }


def format_ner_output(ner_response):
    try:
        entities = ner_response.get("output", [])
        formatted_entities = []
        for page_data in entities:
            page = page_data.get("page", "Unknown Page")
            entity_list = page_data.get("entities", [])
            formatted_entities.append(f"Page {page}:")
            for entity in entity_list:
                for key, value in entity.items():
                    formatted_entities.append(f"  - {key}: {value}")
        return "\n".join(formatted_entities)
    except Exception as e:
        return f"[ERROR] Failed to format NER output: {e}"


def format_summary_output(summary_response):
    try:
        summary = summary_response.get("output", [])
        formatted_summary = []
        for page_data in summary:
            page = page_data.get("page", "Unknown Page")
            content = page_data.get("content", "No content available")
            formatted_summary.append(f"Page {page}: {content}")
        return "\n".join(formatted_summary)
    except Exception as e:
        return f"[ERROR] Failed to format summary output: {e}"


def format_masked_output(masked_response):
    try:
        masked = masked_response.get("output", [])
        formatted_masked = []
        for page_data in masked:
            page = page_data.get("page", "Unknown Page")
            content = page_data.get("content", "No content available")
            formatted_masked.append(f"Page {page}:\n{content}")
        return "\n\n".join(formatted_masked)
    except Exception as e:
        return f"[ERROR] Failed to format masked output: {e}"
