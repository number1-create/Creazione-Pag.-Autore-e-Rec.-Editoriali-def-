import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

app = FastAPI()

# NUOVO: La classe ora include 'content_type'
class GenerationRequest(BaseModel):
    content_type: str # 'penName' o 'publisher'
    prompt: str
    dati_input: str
    esempio_output: str
    pen_name: str
    resource_title: str 

@app.post("/api/generate")
def generate_content(request: GenerationRequest):
    # Definiamo le regole di base
    base_rules = f"""
You are an expert marketing copywriter for the publishing industry.
Your task is to generate compelling descriptions and editorial reviews.
The language must be American English, with a persuasive and professional tone.
Based on the target buyer persona and their needs, build a description that instills trust and credibility.
It must represent the author or publishing house as the one who produces the resource the buyer needs to solve their problem.

**Author and Title (HARD RULE):** Use EXACTLY this Pen Name: "{request.pen_name}" and this Resource Title: "{request.resource_title}".
Do not alter, translate, reorder, abbreviate, or invent other names or titles.

Structure the output into two distinct sections: '## Description' and '## Editorial Reviews' (provide 3 separate reviews).
Strictly adhere to the style, length, and voice of the provided example.
"""

    # Scegliamo il target in base alla scelta dell'utente
    if request.content_type == "penName":
        target_instruction = "The description should be for a Pen Name."
    elif request.content_type == "publisher":
        target_instruction = "The description should be for a Publishing House."
    else:
        target_instruction = "" # Default se il valore non è valido

    # Uniamo tutte le istruzioni per creare il prompt finale per l'AI
    full_prompt = f"""
    {base_rules}
    {target_instruction}

    ### USER-PROVIDED DATA:
    {request.dati_input}

    ### USER-PROVIDED EXAMPLE (to inspire the style):
    {request.esempio_output}

    ### ADDITIONAL INSTRUCTIONS:
    {request.prompt if request.prompt else "None"}
    """

    # Eseguiamo la chiamata ad Azure
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in writing for the publishing industry."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.75, # Un po' più creativo
        max_tokens=1000,
    )

    generated_text = response.choices[0].message.content
    return {"output": generated_text.strip()}

# Servi il frontend
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")