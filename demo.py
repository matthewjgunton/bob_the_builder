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
        if hasattr(chunk, '__iter__') and not isinstance(chunk, str):
            chunk = ''.join(str(item) for item in chunk)
        output_text += chunk
        yield output_text

def process_output(output_text):
    bob = Bob()
    output = ""
    prompt = f"""
    Read the below analysis comparing our lease with the TAA standard lease.
    {output_text}
    Using the analysis above, write an email to my landlord negotiating to make the lease better for me
    """
    for chunk in bob.llm_call(prompt):
        output += chunk
        yield output

def summarize(output_text):
    print(output_text)
    bob = Bob()
    output = ""
    prompt = f"""
    Read the below analysis comparing our lease with the TAA standard lease.
    {output_text}
    Give me a list of what should I do before I decide to sign the lease
    """
    for chunk in bob.llm_call(prompt):
        print(chunk)
        output += chunk
        yield output

with gr.Blocks() as demo:
    gr.Markdown("# PDF Analysis with Bob")
    with gr.Row():
        pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
        analyze_button = gr.Button("Analyze")
    output_text = gr.Markdown(label="Analysis Result")
    analyze_button.click(append_yields, inputs=pdf_input, outputs=output_text)

    summarize_button = gr.Button("Summarize")
    sum_out = gr.Markdown(label="Sign")

    process_button = gr.Button("Create Email for Negotiation")
    processed_output = gr.Markdown(label="Processed Output")

    summarize_button.click(summarize, inputs=output_text, outputs=sum_out)
    process_button.click(process_output, inputs=output_text, outputs=processed_output)

demo.launch()

# should you live here >> scale of 1 to 10
# 3 key questions