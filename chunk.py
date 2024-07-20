from transformers import AutoModel, AutoTokenizer
import torch
# from chromadb import ChromaDB, Document
import PyPDF2
from subprocess import call
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import requests

# def process_string_in_chunks(input_string, chunk_size=6000):
#     # Calculate the number of chunks
#     num_chunks = len(input_string) // chunk_size + (1 if len(input_string) % chunk_size != 0 else 0)
    
#     # Process each chunk
#     for i in range(num_chunks):
#         start = i * chunk_size
#         end = start + chunk_size
#         chunk = input_string[start:end]
#         # Process the chunk here
#         print("*********")
#         print(chunk)
#         print("*********")
#         prompt = """Read the below text. Separate it into logical blocks. Separate each block with a __endblock__
#         {chunk}
#         """
#         text = llm_call(prompt)
#         blocks = text.split('__endblock__')
#         print()
#         for block in blocks:
#             print(block)
#             save_embedding_to_chromadb(block)

def openAIChunking(data):
    # Set up your API key and endpoint
    api_key = 'sk-proj-wnQ6Rq8ku7PHeJPaXqX4T3BlbkFJhoDNpQzuZVaLWCKZA8Xv'
    url = 'https://api.openai.com/v1/chat/completions'

    prompt = f"""
    Please chunk the following text into manageable pieces. Each chunk should be separated by __endblock__.

    {data}
    """

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100000,  # Adjust based on your needs
    }

    response = requests.post(url, headers=headers, json=payload)
    # Print the response
    print(response.json())


# def save_embedding_to_chromadb(text, doc_id):
#     embedding = get_hugging_face_embedding(text)
#     doc = Document(id=doc_id, text=text, embedding=embedding)
#     db.insert(doc)

# embed
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
def get_hugging_face_embedding(text):
    inputs = tokenizer(text=text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy().tolist()


def llm_call(prompt):
    generation_config = {
        "max_output_tokens": 128000,
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
        return response.text

def vertex_chunking(data):
    prompt = """Please chunk the following text into logical pieces. Each chunk should be separated by __endblock__.
    {data}
    """
    return llm_call(data)

# db = ChromaDB()
output_file = "out.txt"
call(["ocrmypdf", "--sidecar", output_file, "./taa_lease_1_.pdf", "/dev/null"])

with open(output_file) as f: 
    full_text = f.read()
print(vertex_chunking(full_text))
