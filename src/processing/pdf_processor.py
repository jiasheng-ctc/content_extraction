from rhubarb import DocAnalysis
from models.model_params import model_params
import boto3

def process_pdf(file_path):

    session = boto3.Session(region_name=model_params["region"])
    doc_analysis = DocAnalysis(file_path=file_path, boto3_session=session)
    ner_response = doc_analysis.run_entity(
        message="Extract key information such as names, date of signing, place of signing, loan account number, and loan details.",
        entities=model_params["ner_entities"]
    )

    summary_response = doc_analysis.run(
        message="Summarize this document briefly, including loan details and terms."
    )

    masking_prompt = (
        "Mask sensitive details like Loan Account No and personal details in this document. "
        "Replace sensitive information with placeholders."
    )
    masked_response = doc_analysis.run(
        message=masking_prompt
    )

    results = {
        "Named Entity Recognition": ner_response,
        "Summary": summary_response,
        "Masked Document": masked_response
    }

    return results
