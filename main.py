import subprocess
import PyPDF2
import re

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    output_file = "out.txt"
    with open(output_file, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    return text

source_file = "./2023-Apartment-Lease-Contract-12-23-SAMPLE.pdf"
map_section_to_text = {}
data = read_pdf(source_file)

