from pdf2image import convert_from_path
from pytesseract import image_to_string

def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    extracted_text = ""
    for image in images:
        text = image_to_string(image, lang='eng')
        extracted_text += text + "\n"
    return extracted_text.strip()
