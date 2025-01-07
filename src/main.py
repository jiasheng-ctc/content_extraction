from src.processing.pdf_processor import process_pdf

def main():
    pdf_path = input("Enter the path to your scanned PDF file: ").strip()
    print("[INFO] Processing the PDF file...")
    structured_response = process_pdf(pdf_path)
    print("[INFO] Structured Response from Claude:")
    print(structured_response)

if __name__ == "__main__":
    main()
