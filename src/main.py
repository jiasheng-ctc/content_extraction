from src.processing.pdf_processor import process_pdf

def main():
    pdf_path = input("Enter the path to your scanned PDF file: ").strip()
    print("[INFO] Processing the PDF file using Rhubarb...")
    
    # Get results
    results = process_pdf(pdf_path)
    
    # Display results
    print("[INFO] Named Entity Recognition:")
    print(results["Named Entity Recognition"])

    print("\n[INFO] Summary of the Document:")
    print(results["Summary"])

    print("\n[INFO] Masked Document:")
    print(results["Masked Document"])

if __name__ == "__main__":
    main()
