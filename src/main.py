import logging
import os
from src.processing.pdf_processor import process_pdf

logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO,
)

def main():
    pdf_path = input("Enter the path to your scanned PDF file: ").strip()
    if not os.path.exists(pdf_path):
        logging.error(f"The file path '{pdf_path}' does not exist.")
        return

    if not pdf_path.lower().endswith(".pdf"):
        logging.error("The provided file is not a PDF. Please provide a valid PDF file.")
        return

    logging.info(f"Processing the PDF file: {pdf_path}...")

    try:
        results = process_pdf(pdf_path)
        summary = results.get("Summary", "No summary available.")
        masked_document = results.get("Masked Document", "No masked document available.")
        logging.info("Summary of the Document:")
        logging.info(summary)
        logging.info("Masked Document:")
        logging.info(masked_document)
    except Exception as e:
        logging.error(f"An error occurred while processing the PDF: {e}")

if __name__ == "__main__":
    main()
