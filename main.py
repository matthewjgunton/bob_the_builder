import subprocess
import PyPDF2
import re
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

class Bob:

    def __init__(self):
        # pull out data by knowing all of our sections
        self.section_headers = [
            "LEASE DETAILS", "LEASE TERMS AND CONDITIONS", "RESIDENT LIFE", 
            "EVICTION AND REMEDIES", "END OF THE LEASE TERM", "GENERAL PROVISIONS AND SIGNATURES",
        ]

        self.taa_map_section_to_text = {}
        self.my_map_section_to_text = {}


    def read_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        output_file = "out.txt"
        with open(output_file, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        return text

    def extract_between_headers(self, text, header1, header2):
        pattern = f"{re.escape(header1)}(.*?){re.escape(header2)}"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def extract_from_last_header(self, text, header):
        pattern = f"{re.escape(header)}(.*)$"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def generate(self):
        for header in self.section_headers:
            if header == "LEASE DETAILS":
                continue
            print("section "+header)
            prompt = f"""You\'re a helpful AI Assistant, giving me some feedback on a lease. I\'m going to give you the Texas Apartment Association (TAA) base lease and my lease. I am giving you the section on {header}. 
            Do two things:
            (1) show me what are the differences between them
            (2) explain to me if these differences matter

            TAA Lease:
            ```
            {self.taa_map_section_to_text[header]}
            ```

            My Lease:
            ```
            {self.my_map_section_to_text[header]}
            ```"""
            return self.llm_call(prompt)

    def llm_call(self, prompt):
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        vertexai.init(project="aitxhack24aus-632", location="us-central1")
        model = GenerativeModel(
        "gemini-1.5-pro-001",
        )
        responses = model.generate_content(
                [prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
        )
        for response in responses:
            yield response.text

    def analyze(self, my_data):
        # get our data
        taa_file = "./2023-Apartment-Lease-Contract-12-23-SAMPLE.pdf"
        # my_file = "./parktowerlease.pdf"
        taa_data = self.read_pdf(taa_file)
        # my_data = read_pdf(my_file)

        for i in range(len(self.section_headers) - 1):
            taa_section = self.extract_between_headers(taa_data, self.section_headers[i], self.section_headers[i+1])
            self.taa_map_section_to_text[self.section_headers[i]] = taa_section
            my_section = self.extract_between_headers(my_data, self.section_headers[i], self.section_headers[i+1])
            self.my_map_section_to_text[self.section_headers[i]] = my_section

        self.taa_map_section_to_text[self.section_headers[len(self.section_headers)-1]] = self.extract_from_last_header(taa_data, self.section_headers[len(self.section_headers)-1])
        self.my_map_section_to_text[self.section_headers[len(self.section_headers)-1]] = self.extract_from_last_header(my_data, self.section_headers[len(self.section_headers)-1])
        yield from self.generate()

# ui
