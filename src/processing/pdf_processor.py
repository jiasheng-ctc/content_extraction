from rhubarb import DocAnalysis, Entities
from models.model_params import model_params
import boto3

def process_pdf(file_path):

    session = boto3.Session(region_name=model_params["region"])
    da = DocAnalysis(file_path=file_path, boto3_session=session)
    response = da.run_entity(
        message="Extract the specified named entities from this document.",
        entities=model_params["ner_entities"]
    )

    return response
