import os
from rhubarb import DocAnalysis, LanguageModels
from src.models.model_params import model_params
import boto3
import logging
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def create_summary_pdf(summary_text, output_path):
    """Creates a PDF with the provided summary content, handling text wrapping and pagination."""
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        margin = 50  
        text_width = width - 2 * margin
        line_height = 14  
        start_x = margin
        start_y = height - margin - 40  

        c.setFont("Helvetica-Bold", 14)
        c.drawString(start_x, start_y, "Document Summary:")

        c.setFont("Helvetica", 10)
        text_object = c.beginText(start_x, start_y - line_height * 2)

        lines = simpleSplit(summary_text, "Helvetica", 10, text_width)

        for line in lines:
            if text_object.getY() <= margin:  
                c.drawText(text_object)
                c.showPage()
                c.setFont("Helvetica", 10)
                text_object = c.beginText(start_x, height - margin)

            text_object.textLine(line)

        c.drawText(text_object) 
        c.save()

    except Exception as e:
        logger.error(f"Error creating summary PDF: {e}")
        raise

def parse_response(response):
    """Parses the response from doc_analysis.run to ensure correct data extraction."""
    try:
        if isinstance(response, str):
            logger.info(f"Parsing response as JSON string: {response[:100]}...")
            if response.startswith("```json"):
                response = response.strip('```json').strip()  # Strip triple backticks and 'json'
            response = json.loads(response)
        elif isinstance(response, list):  # Sometimes the response might already be a list
            return response
        elif not isinstance(response, (dict, list)):
            raise ValueError("Unexpected response type from doc_analysis")
        return response
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from response: {response}")
        raise ValueError("Invalid response format from doc_analysis") from e


def process_pdf(file_path, hr_entity, finance_entity, operation_entity, summarize, mask):
    try:
        base_output_dir = "/home/ubuntu/content_extraction/assets"
        os.makedirs(base_output_dir, exist_ok=True)

        session = boto3.Session(region_name=model_params["region"])
        doc_analysis = DocAnalysis(
            file_path=file_path,
            boto3_session=session,
            modelId=model_params["model_id"]
        )

        classification_message = (
            "Classify this document into a department based on these keywords and context clues:\n"
            "Finance: payroll, purchase order, PO Number, Contract No, invoice, budget, accounting, "
            "financial statement, expense, revenue, tax, salary, compensation, financial report, fiscal, procurement\n"
            "HR: HR, Human resource, employee ID, SOP ID, employment, recruitment, onboarding, "
            "performance review, training, employee handbook, benefits, compensation, hiring, job description, workforce\n"
            "Operation: logistics, batch no, serial no, supply chain, inventory, workflow, process, manufacturing, "
            "distribution, operations manual, production, service delivery, quality control\n"
            "Respond with ONLY the department name: HR, Finance, Operation, or Unknown."
        )

        classification_response = doc_analysis.run(message=classification_message)
        logger.info(f"Raw classification response: {classification_response}")
        classification_response = parse_response(classification_response)
        department = classification_response.get("output", [{}])[0].get("content", "Unknown").strip()

        if department not in ["HR", "Finance", "Operation"]:
            department = "Unknown"

        entity_extraction_message = ""
        extracted_entity = "Unknown"
        if department == "HR" and hr_entity:
            entity_extraction_message = f"Extract all content related to the HR entity: {hr_entity}."
        elif department == "Finance" and finance_entity:
            entity_extraction_message = f"Extract all content related to the Finance entity: {finance_entity}."
        elif department == "Operation" and operation_entity:
            entity_extraction_message = f"Extract all content related to the Operation entity: {operation_entity}."

        if entity_extraction_message:
            extraction_response = doc_analysis.run(message=entity_extraction_message)
            logger.info(f"Raw extraction response: {extraction_response}")
            extraction_response = parse_response(extraction_response)
            extracted_entity = extraction_response.get("output", [{}])[0].get("content", "Unknown").strip()

        if extracted_entity in ["Content not extracted due to uncertainty.", "Unknown"]:
            logger.info(f"Document {file_path} not saved as the extracted entity is 'Unknown'.")
            return {
                "Department": department,
                "Extracted Entity": "Unknown",
                "Destination Path": None,
                "Status": "Document not saved"
            }

        extracted_entity = extracted_entity.replace(" ", "_").replace("/", "-")
        dept_dir = os.path.join(base_output_dir, department)
        os.makedirs(dept_dir, exist_ok=True)

        filename = f"{extracted_entity}.pdf"
        destination_path = os.path.join(dept_dir, filename)
        os.rename(file_path, destination_path)
        logger.info(f"File saved to: {destination_path}")

        summary_destination_path = None
        masked_destination_path = None

        doc_analysis = DocAnalysis(
            file_path=destination_path,
            boto3_session=session,
            modelId=model_params["model_id"]
        )

        if summarize:
            summary_message = "Summarize the content of this document with details. Highlight any important remarks such as urgent documents etc."
            summary_response = doc_analysis.run(message=summary_message)
            logger.info(f"Raw summary response: {summary_response}")
            summary_response = parse_response(summary_response)
            summary_text = summary_response.get("output", [{}])[0].get("content", "No summary available.").strip()

            summary_filename = f"{extracted_entity}_summary.pdf"
            summary_destination_path = os.path.join(dept_dir, summary_filename)
            create_summary_pdf(summary_text, summary_destination_path)
            logger.info(f"Summary saved to: {summary_destination_path}")

        if mask:
            masking_prompt = (
                "Mask sensitive details in this document, including:"
                "\n- Contract or Reference Numbers"
                "\n- Personal Details, address or contact details."
                "\n- Any other identifiable or sensitive information. "
                "Replace sensitive information with appropriate placeholders."
            )
            masked_response = doc_analysis.run(message=masking_prompt)
            logger.info(f"Raw masking response: {masked_response}")
            masked_response = parse_response(masked_response)

            if isinstance(masked_response, str) and masked_response.startswith("```json"):
                masked_response = parse_response(masked_response.strip("```json").strip())
            
            if isinstance(masked_response, list):
                masked_text = "\n\n".join(item.get("content", "No masked content available.").strip() for item in masked_response)
            elif isinstance(masked_response, dict) and "output" in masked_response:
                masked_text = "\n\n".join(
                    item.get("content", "No masked content available.").strip()
                    for item in masked_response.get("output", [])
                )
            else:
                masked_text = "No masked content available."

            masked_filename = f"{extracted_entity}_masked.pdf"
            masked_destination_path = os.path.join(dept_dir, masked_filename)
            create_summary_pdf(masked_text, masked_destination_path)
            logger.info(f"Masked file saved to: {masked_destination_path}")

        return {
            "Department": department,
            "Extracted Entity": extracted_entity,
            "Destination Path": destination_path,
            "Summary Path": summary_destination_path,
            "Masked Path": masked_destination_path,
            "Status": "Document, summary, and masked files saved successfully"
        }

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise