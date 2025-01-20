import csv
import os
from rhubarb import DocAnalysis, LanguageModels
from models.model_params import model_params
import boto3


def process_pdf(file_path):
    session = boto3.Session(region_name=model_params["region"])
    doc_analysis = DocAnalysis(file_path=file_path, boto3_session=session,
        modelId=LanguageModels.CLAUDE_HAIKU_V1)

    # Get the document summary
    summary_response = doc_analysis.run(
        message=(
            "Summarize this document briefly, including:" 
            "\n- Contract or Reference Number"
            "\n- Service Hotline"
            "\n- Customer Name"
            "\n- Period"
            "\n- Main Contact Person"
            "\n- Email Address"
        )
    )

    # Mask sensitive information in the document
    masking_prompt = (
        "Mask sensitive details in this document, including:" 
        "\n- Contract or Reference Numbers"
        "\n- Personal Details"
        "\n- Any other identifiable or sensitive information. "
        "Replace sensitive information with appropriate placeholders."
    )
    masked_response = doc_analysis.run(message=masking_prompt)

    print("\n[INFO] Processing the PDF file using Rhubarb...")

    print("\n[INFO] Summary of the Document:")
    summary_content = format_summary_output(summary_response)
    print(summary_content)

    print("\n[INFO] Masked Document:")
    print(format_masked_output(masked_response))

    # Save the formatted summary to a CSV file
    save_summary_to_csv(summary_response, "/home/ubuntu/scanned-pdf-extraction/assets/examples/output_csv/summary_output.csv")

    return {
        "Summary": summary_response,
        "Masked Document": masked_response,
    }


def format_summary_output(summary_response):
    try:
        summary = summary_response.get("output", [])
        formatted_summary = []
        for page_data in summary:
            page = page_data.get("page", "Unknown Page")
            content = page_data.get("content", "No content available")

            # Parse key-value pairs from the content
            for line in content.split("\n"):
                if ": " in line:
                    field, value = line.split(": ", 1)
                    formatted_summary.append({"Page": page, "Field": field.strip(), "Value": value.strip()})
                else:
                    formatted_summary.append({"Page": page, "Field": "Unstructured Content", "Value": line.strip()})
        return formatted_summary
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


def save_summary_to_csv(summary_response, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Page", "Field", "Value"])  # CSV Header

            # Ensure summary_response is parsed correctly
            formatted_summary = format_summary_output(summary_response)  # Use the formatted summary output
            for entry in formatted_summary:
                csv_writer.writerow([entry["Page"], entry["Field"], entry["Value"]])
    except Exception as e:
        print(f"[ERROR] Failed to save summary to CSV: {e}")
