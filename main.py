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

def extract_between_headers(text, header1, header2):
    pattern = f"{re.escape(header1)}(.*?){re.escape(header2)}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_from_last_header(text, header):
    pattern = f"{re.escape(header)}(.*)$"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# pull out data by knowing all of our sections

section_headers = [
    "LEASE DETAILS", "LEASE TERMS AND CONDITIONS", "RESIDENT LIFE", 
    "EVICTION AND REMEDIES", "END OF THE LEASE TERM", "GENERAL PROVISIONS AND SIGNATURES",
]
for i in range(len(section_headers) - 1):
    print(section_headers[i])
    print(extract_between_headers(data, section_headers[i], section_headers[i+1]))
    print("****")

print(extract_from_last_header(data, section_headers[len(section_headers)-1]))

# data = read_pdf("./parktowerlease.pdf")