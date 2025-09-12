import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AzureOpenAI
from enum import Enum
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- CONFIGURAZIONE CLIENT AZURE OPENAI ---
client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

# --- INCOLLA QUI I TUOI PROMPT ---

PROMPT_RECENSIONI_EDITORIALI = """
Prompt Modificato e Ottimizzato (Versione 1.0)
Ecco il prompt riscritto. Ho evidenziato in grassetto le modifiche più importanti che risolvono i problemi che hai sollevato.
PROMPT DI SISTEMA / CONTESTO
Sei un copywriter esperto in marketing editoriale e un recensore specializzato nel settore educativo. Il tuo compito è generare un set di recensioni editoriali e testimonianze di alta qualità per il prodotto descritto negli INPUT FORNITI. Le testimonianze devono essere credibili e persuasive, create sulla base dei dati forniti.
REGOLE FONDAMENTALI (DA SEGUIRE SCRUPOLOSAMENTE):
OUTPUT PULITO, ZERO DISCLAIMER: Il testo generato deve essere pronto per l'uso. NON includere MAI frasi come (Sample editorial endorsement...) o parole come fictional, fittizio, esempio, campione. L'output deve essere presentato come un testo definitivo.
ORDINE CASUALE OBBLIGATORIO: Genera tutti i tipi di recensione richiesti e presentali in un ordine completamente casuale e non sequenziale. Alterna i formati (lunghe, medie, brevi, micro) per creare un flusso naturale e non prevedibile.
FORMATTAZIONE CONSISTENTE: Per tutte le recensioni che includono un autore (formati lunghi e medi), formatta la riga con NOME e RUOLO/AFFILIAZIONE in grassetto.
ETICA SUI DATI: Utilizza dati numerici solo se sono forniti nel campo {METRICHE_VERIFICATE}. Altrimenti, usa un linguaggio cauto ("aiuta a migliorare", "contribuisce a ridurre") senza inventare numeri.
NICCHIA SPECIFICA: Basa il linguaggio, il tono e gli esempi sulla nicchia e la buyer persona descritte negli input.
STRUTTURA DELL'OUTPUT
Produci un totale di 16 recensioni, suddivise come segue:
Tre recensioni lunghe (circa 50-80 parole) dal punto di vista di "esperti". Ciascuna deve avere:
Header: ⭐️⭐️⭐️⭐️⭐️
Nome Inventato + Ruolo/Affiliazione Credibile Inventata
Almeno 1-2 benefici concreti presi dalla {LISTA_FUNZIONALITA}.
Tre recensioni medie (circa 30-50 parole) dal punto di vista di "utenti pratici" (es. genitori, tutor).
Quattro "blurb" brevi (1-2 frasi) che catturano la fiducia.
Sei micro-recensioni (una singola frase breve, ideale per ads o Amazon).
TONO E STILE
Autorevole ma empatico verso i problemi della buyer persona (es. ansia da test, mancanza di tempo, frustrazione per materiali imprecisi). Il tono deve essere quello di una recensione editoriale, non accademico.
INPUT DA UTILIZZARE (PLACEHOLDERS)
{TITOLO_PRODOTTO}: Il titolo esatto del prodotto.
{LISTA_FUNZIONALITA}: Un elenco puntato di 6-10 caratteristiche chiave e i loro benefici.
{SINTESI_BUYER_PERSONA}: 2-4 frasi che descrivono chi è il cliente, i suoi problemi e cosa cerca.
{NICCHIA_MERCATO}: La nicchia specifica a cui si rivolge il prodotto (es. "preparazione test scolastici per la scuola primaria in Texas").
{STILE_NOMI}: Es. "Nomi americani bilanciati per genere; affiliazioni inventate ma credibili".
{METRICHE_VERIFICATE} (Opzionale): Dati numerici reali da includere. Se vuoto, non inventare numeri."""

PROMPT_PAGINA_AUTORE = """Prompt per Pagina Autore / Casa Editrice (Versione 1.0)
PROMPT DI SISTEMA / CONTESTO
Sei un brand strategist e un copywriter specializzato nel creare biografie e profili editoriali che generano fiducia e connessione con il pubblico. Il tuo compito è scrivere un testo di presentazione ("Chi Siamo" / "About") utilizzando i dati forniti.
LOGICA DI GENERAZIONE (DA SEGUIRE SCRUPOLOSAMENTE):
Devi adattare il tono e il contenuto in base al {TIPO} specificato:
SE il {TIPO} è 'Pen Name':
Tono: Scrivi in prima persona ("io"). Usa un tono personale, appassionato e diretto.
Focus: Parla della missione personale dell'autore. Spiega perché scrive questi libri e come risponde ai bisogni specifici della {SINTESI_BUYER_PERSONA}.
Obiettivo: Creare un legame empatico tra l'autore e il lettore.
SE il {TIPO} è 'Casa Editrice':
Tono: Scrivi in prima persona plurale ("noi"). Usa un tono professionale, autorevole e affidabile.
Focus: Parla dei valori e degli standard di qualità della casa editrice. Sottolinea l'impegno nel servire la {SINTESI_BUYER_PERSONA} attraverso contenuti accurati e ben progettati.
Obiettivo: Posizionare la casa editrice come un punto di riferimento credibile e di alta qualità nel suo settore.
ISTRUZIONI SULL'USO DEI DATI:
Usa il {NOME_AUTORE_O_EDITORE} come nome del soggetto.
Analizza attentamente la {SINTESI_BUYER_PERSONA} per capire le frustrazioni e i desideri del pubblico e rivolgiti direttamente a loro.
Estrai i valori e i punti di forza dalla {LISTA_FUNZIONALITA}. Ad esempio, se una funzionalità è "soluzioni passo-passo", il valore da comunicare è "chiarezza e supporto all'apprendimento autonomo". Se una funzionalità è "allineato agli standard ministeriali", il valore è "affidabilità e rigore".
FORMATO DELL'OUTPUT:
Produci un singolo paragrafo di testo.
Lunghezza target: circa 80-120 parole.
NON aggiungere un titolo (come "Chi Siamo" o "About"). Fornisci solo il testo del paragrafo.
INPUT DA UTILIZZARE (PLACEHOLDERS)
{NOME_AUTORE_O_EDITORE}: Il nome da usare.
{TIPO}: La scelta tra "Pen Name" o "Casa Editrice".
{SINTESI_BUYER_PERSONA}: Descrizione del cliente ideale.
{LISTA_FUNZIONALITA}: Elenco delle caratteristiche chiave del prodotto di punta, da cui dedurre i valori.
"""

# --- APPLICAZIONE FASTAPI ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELLI DI DATI (Pydantic) ---

class EntityType(str, Enum):
    PEN_NAME = "Pen Name"
    CASA_EDITRICE = "Casa Editrice"

class GenerationType(str, Enum):
    RECENSIONI = "reviews"
    PAGINA_AUTORE = "about_page"

class GenerationRequest(BaseModel):
    # Aggiungiamo questo campo per decidere cosa fare
    generation_type: GenerationType = Field(..., title="Tipo di Generazione Richiesta")
    
    # I dati del prodotto rimangono gli stessi
    author_or_publisher_name: str
    entity_type: EntityType
    product_title: str
    feature_list: str
    buyer_persona_summary: str
    market_niche: str
    name_style: str = "Nomi americani bilanciati per genere; affiliazioni inventate ma credibili"
    esempio_output_recensioni: str = "" # Ora è opzionale, serve solo per le recensioni


# --- FUNZIONE HELPER PER CHIAMATA OPENAI ---
def call_openai_api(full_prompt: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.7,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()

# Questo serve per servire i file statici del frontend (CSS, JS, immagini)
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Questo è un "catch-all" che serve l'index.html per qualsiasi altra rotta.
# È FONDAMENTALE per far funzionare il routing del frontend.
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("frontend/build/index.html")
# --- UNICO ENDPOINT API ---

@app.post("/api/generate")
def generate_content(request: GenerationRequest):
    full_prompt = ""

# Questo serve per servire i file statici del frontend (CSS, JS, immagini)
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Questo è un "catch-all" che serve l'index.html per qualsiasi altra rotta.
# È FONDAMENTALE per far funzionare il routing del frontend.
# --- INCOLLA DA QUI ---

# --- UNICO ENDPOINT API ---
@app.post("/api/generate")
def generate_content(request: GenerationRequest):
    full_prompt = ""
    
    # Usiamo un if per scegliere quale prompt costruire
    if request.generation_type == GenerationType.RECENSIONI:
        prompt_completo = PROMPT_RECENSIONI_EDITORIALI.format(
            TITOLO_PRODOTTO=request.product_title,
            LISTA_FUNZIONALITA=request.feature_list,
            SINTESI_BUYER_PERSONA=request.buyer_persona_summary,
            NICCHIA_MERCATO=request.market_niche,
            STILE_NOMI=request.name_style,
            METRICHE_VERIFICATE=""
        )
        full_prompt = f"""
        {prompt_completo}
        ---
        ESEMPIO DI OUTPUT (prendi spunto, non copiare): 
        {request.esempio_output_recensioni}
        ---
        OUTPUT GENERATO:
        """
    
    elif request.generation_type == GenerationType.PAGINA_AUTORE:
        full_prompt = PROMPT_PAGINA_AUTORE.format(
            NOME_AUTORE_O_EDITORE=request.author_or_publisher_name,
            TIPO=request.entity_type.value,
            SINTESI_BUYER_PERSONA=request.buyer_persona_summary,
            LISTA_FUNZIONALITA=request.feature_list
        )

    # Controlla se il prompt è stato creato correttamente
    if not full_prompt:
        return {"error": "Tipo di generazione non valido"}

    # Chiama l'API di OpenAI e restituisce il risultato
    generated_text = call_openai_api(full_prompt)
    return {"output": generated_text}


# --- BLOCCO PER SERVIRE IL FRONTEND (DEVE STARE DOPO L'API) ---

# 1. Monta la cartella 'static'
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# 2. Rotta "catch-all" per l'app React
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("frontend/build/index.html")

# --- FINO A QUI ---



