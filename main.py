import subprocess
import PyPDF2

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

source_file = "./2023-Apartment-Lease-Contract-12-23-SAMPLE.pdf"
data = read_pdf(source_file)



print(data)
