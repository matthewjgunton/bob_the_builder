import gradio as gr
import PyPDF2
from main import Bob  # Assuming the Bob class is in a file named bob.py
import traceback

def process_pdf(file):
    if file is None:
        return "No file uploaded."
    
    try:
        pdf_reader = PyPDF2.PdfReader(file.name)
        num_pages = len(pdf_reader.pages)
        
        # Extract text from all pages
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        # Call Bob's analyze function
        bob = Bob()
        analysis_result = bob.analyze(full_text)
    
        # Consume the generator and yield results
        for chunk in analysis_result:
            yield chunk
        
    except Exception as e:
        traceback.print_exception(e)
        return f"Error processing PDF: {str(e)}"

def append_yields(file):
    output_text = ""
    for chunk in process_pdf(file):
        output_text += chunk
        yield output_text


with gr.Blocks() as demo:
    gr.Markdown("# PDF Analysis with Bob")
    with gr.Row():
        pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
        analyze_button = gr.Button("Analyze")
    output_text = gr.Markdown(label="Analysis Result")

    analyze_button.click(append_yields, inputs=pdf_input, outputs=output_text)

demo.launch()