import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerationRequest(BaseModel):
    prompt: str
    dati_input: str
    esempio_output: str

@app.post("/api/generate")
def generate_content(request: GenerationRequest):
    full_prompt = f"""
    PROMPT DI SISTEMA: {request.prompt}
    DATI FORNITI: {request.dati_input}
    ESEMPIO DI OUTPUT (prendi spunto, non copiare): {request.esempio_output}
    ---
    OUTPUT GENERATO:
    """
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.7,
        max_tokens=800,
    )
    generated_text = response.choices[0].message.content
    return {"output": generated_text.strip()}