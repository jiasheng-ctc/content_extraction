import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from api.ocr_extractor import extract_text_from_pdf
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_ocr_extraction():
    sample_pdf = "assets/examples/sample_pdf.pdf"
    text = extract_text_from_pdf(sample_pdf)
    assert len(text) > 0
