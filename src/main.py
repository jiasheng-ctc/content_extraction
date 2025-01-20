import logging
from src.processing.pdf_processor import process_pdf

# Configure logger
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO,
)

def main():
    pdf_path = input("Enter the path to your scanned PDF file: ").strip()
    logging.info("Processing the PDF file using Rhubarb...")

    try:
            # Get results
        results = process_pdf(pdf_path)

        # Log results
        # logging.info("Named Entity Recognition:")
        # logging.info(results.get("Named Entity Recognition", "No NER data available."))

        logging.info("Summary of the Document:")
        logging.info(results.get("Summary", "No summary available."))

        logging.info("Masked Document:")
        logging.info(results.get("Masked Document", "No masked document available."))
    except Exception as e:
        logging.error(f"An error occurred while processing the PDF: {e}")

if __name__ == "__main__":
    main()
