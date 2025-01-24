import os
from rhubarb import DocAnalysis
from src.models.model_params import model_params
import boto3
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf(file_path):
   try:
       base_output_dir = "/home/ubuntu/content_extraction/assets"
       os.makedirs(base_output_dir, exist_ok=True)

       session = boto3.Session(region_name=model_params["region"])
       doc_analysis = DocAnalysis(
           file_path=file_path,
           boto3_session=session,
           modelId=model_params["model_id"]
       )

       classification_response = doc_analysis.run(
           message=(
               "Classify this document into a department based on these keywords and context clues:\n"
               "Finance: payroll, Pruchase order, PO Number, Contract No, invoice, budget, accounting, financial statement, expense, revenue, tax, salary, compensation, financial report, fiscal, procurement\n"
               "HR: HR, Human resrouce, employee ID, SOP ID, employment, recruitment, onboarding, performance review, training, employee handbook, benefits, compensation, hiring, job description, workforce\n"
               "Operation: logistics, batch no, serial no, supply chain, inventory, workflow, process, manufacturing, distribution, operations manual, production, service delivery, quality control\n"
               "If the document does not clearly match any of these categories, mention the context clues.\n"
               "Respond with ONLY the department name: HR, Finance, Operation, or Unknown."
           )
       )

       department = classification_response.get("output", [{}])[0].get("content", "Unknown").strip()
       
       if department not in ["HR", "Finance", "Operation"]:
           department = "Unknown"

       dept_dir = os.path.join(base_output_dir, department)
       os.makedirs(dept_dir, exist_ok=True)

       filename = os.path.basename(file_path)
       destination_path = os.path.join(dept_dir, filename)
       os.rename(file_path, destination_path)

       return {
           "Department": department,
           "Destination Path": destination_path
       }

   except Exception as e:
       logger.error(f"Error processing PDF: {e}")
       raise