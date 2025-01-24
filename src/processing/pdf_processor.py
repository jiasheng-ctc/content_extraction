import os
from rhubarb import DocAnalysis
from src.models.model_params import model_params
import boto3
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def process_pdf(file_path, hr_entity, finance_entity, operation_entity):
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
        department = classification_response.get("output", [{}])[0].get("content", "Unknown").strip()

        if department not in ["HR", "Finance", "Operation"]:
            department = "Unknown"

        entity_extraction_message = ""
        extracted_entity = "Unknown"
        if department == "HR" and hr_entity:
            entity_extraction_message = (
                f"Extract all content related to the HR entity: {hr_entity}. "
                "If the content is unclear, handwritten text is illegible, or you cannot provide a confident answer, "
                "do not proceed with extraction. Respond with: 'Answer not found.'"
            )
        elif department == "Finance" and finance_entity:
            entity_extraction_message = (
                f"Extract all content related to the Finance entity: {finance_entity}. "
                "If the content is unclear, handwritten text is illegible, or you cannot provide a confident answer, "
                "do not proceed with extraction. Respond with: 'Answer not found.'"
            )
        elif department == "Operation" and operation_entity:
            entity_extraction_message = (
                f"Extract all content related to the Operation entity: {operation_entity}. "
                "If the content is unclear, handwritten text is illegible, or you cannot provide a confident answer, "
                "do not proceed with extraction. Respond with: 'Answer not found.'"
            )

        if entity_extraction_message:
            extraction_response = doc_analysis.run(message=entity_extraction_message)
            extracted_entity = extraction_response.get("output", [{}])[0].get("content", "Unknown").strip()

        if extracted_entity in ["Content not extracted due to uncertainty.", "Unknown","Answer not found"]:
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

        return {
            "Department": department,
            "Extracted Entity": extracted_entity,
            "Destination Path": destination_path,
            "Status": "Document saved successfully"
        }

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise
