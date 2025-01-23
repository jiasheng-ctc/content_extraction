import csv
import os
from rhubarb import DocAnalysis
from src.models.model_params import model_params
import boto3
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf(file_path):
    try:
        session = boto3.Session(region_name=model_params["region"])
        doc_analysis = DocAnalysis(
            file_path=file_path,
            boto3_session=session,
            modelId=model_params["model_id"]
        )

        logger.info("Processing the PDF file using Rhubarb...")

        summary_response = doc_analysis.run(
            message=(
                "Summarize this document briefly, including:" \
                "\n- Contract or Reference Number" \
                "\n- Service Hotline" \
                "\n- Customer Name" \
                "\n- Period" \
                "\n- Main Contact Person" \
                "\n- Email Address"
            )
        )

        masking_prompt = (
            "Mask sensitive details in this document, including:" \
            "\n- Contract or Reference Numbers" \
            "\n- Personal Details" \
            "\n- Any other identifiable or sensitive information. " \
            "Replace sensitive information with appropriate placeholders."
        )
        masked_response = doc_analysis.run(message=masking_prompt)

        logger.info("Summary of the Document:")
        summary_content = format_summary_output(summary_response)
        logger.info(summary_content)

        logger.info("Masked Document:")
        logger.info(format_masked_output(masked_response))

        csv_path = "/home/ubuntu/scanned-pdf-extraction/assets/examples/output_csv/summary_output.csv"
        save_summary_to_csv(summary_response, csv_path)

        return {
            "Summary": summary_response,
            "Masked Document": masked_response,
        }

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise

def format_summary_output(summary_response):
    try:
        summary = summary_response.get("output", [])
        formatted_summary = []
        for page_data in summary:
            page = page_data.get("page", "Unknown Page")
            content = page_data.get("content", "No content available")

            for line in content.split("\n"):
                if ": " in line:
                    field, value = line.split(": ", 1)
                    formatted_summary.append({"Page": page, "Field": field.strip(), "Value": value.strip()})
                else:
                    formatted_summary.append({"Page": page, "Field": "Unstructured Content", "Value": line.strip()})
        return formatted_summary
    except Exception as e:
        logger.error(f"Failed to format summary output: {e}")
        return []

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
        logger.error(f"Failed to format masked output: {e}")
        return ""

def save_summary_to_csv(summary_response, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Page", "Field", "Value"])
            formatted_summary = format_summary_output(summary_response)
            for entry in formatted_summary:
                csv_writer.writerow([entry["Page"], entry["Field"], entry["Value"]])
    except Exception as e:
        logger.error(f"Failed to save summary to CSV: {e}")
        raise
