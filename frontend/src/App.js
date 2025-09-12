import React, { useState } from 'react';
import './App.css';

function App() {
  // --- STATI PER I CAMPI DEL FORM ---
  const [authorOrPublisherName, setAuthorOrPublisherName] = useState('');
  const [entityType, setEntityType] = useState('Pen Name'); // Valore di default
  const [productTitle, setProductTitle] = useState('');
  const [featureList, setFeatureList] = useState('');
  const [buyerPersonaSummary, setBuyerPersonaSummary] = useState('');
  const [marketNiche, setMarketNiche] = useState('');
  const [esempioOutputRecensioni, setEsempioOutputRecensioni] = useState('');

  // --- STATI PER LA GESTIONE DELL'OUTPUT E DEL CARICAMENTO ---
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // URL del backend. Assicurati che sia corretto.
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  /**
   * Funzione unica per gestire la generazione, che accetta il tipo di contenuto da creare.
   * @param {'reviews' | 'about_page'} generationType - Il tipo di contenuto da generare.
   */
  const handleSubmit = async (generationType) => {
    // Validazione semplice per assicurarsi che i campi principali non siano vuoti
    if (!authorOrPublisherName || !productTitle || !buyerPersonaSummary || !featureList) {
      setError('Per favore, compila tutti i campi richiesti.');
      return;
    }

    setIsLoading(true);
    setOutput('');
    setError('');

    // Prepara il corpo della richiesta secondo il modello Pydantic del backend
    const requestBody = {
      generation_type: generationType,
      author_or_publisher_name: authorOrPublisherName,
      entity_type: entityType,
      product_title: productTitle,
      feature_list: featureList,
      buyer_persona_summary: buyerPersonaSummary,
      market_niche: marketNiche,
      // AGGIUNGI QUESTA RIGA
      name_style: "Nomi americani bilanciati per genere; affiliazioni inventate ma credibili",
      esempio_output_recensioni: generationType === 'reviews' ? esempioOutputRecensioni : '',
    };

    try {
      const response = await fetch(`${apiUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Errore dal server: ${response.statusText}`);
      }

      const data = await response.json();
      setOutput(data.output);
    } catch (err) {
      setError(`Si è verificato un errore: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Generatore di Contenuti Editoriali</h1>
        <p>Inserisci i dati del prodotto una sola volta e genera ciò che ti serve.</p>
      </header>

      <main>
        <div className="form-container">
          <h2>Dati del Prodotto</h2>
          
          <div className="form-group">
            <label>Nome Autore / Casa Editrice</label>
            <input type="text" value={authorOrPublisherName} onChange={(e) => setAuthorOrPublisherName(e.target.value)} placeholder="Es. John Doe o Edizioni Futura" />
          </div>

          <div className="form-group">
            <label>Tipo</label>
            <select value={entityType} onChange={(e) => setEntityType(e.target.value)}>
              <option value="Pen Name">Pen Name</option>
              <option value="Casa Editrice">Casa Editrice</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Titolo del Prodotto</label>
            <input type="text" value={productTitle} onChange={(e) => setProductTitle(e.target.value)} placeholder="Es. Guida Completa a..." />
          </div>

          <div className="form-group">
            <label>Nicchia di Mercato</label>
            <input type="text" value={marketNiche} onChange={(e) => setMarketNiche(e.target.value)} placeholder="Es. Preparazione test scolastici scuola primaria" />
          </div>

          <div className="form-group">
            <label>Caratteristiche e Benefici Chiave</label>
            <textarea value={featureList} onChange={(e) => setFeatureList(e.target.value)} placeholder="Elenca le caratteristiche principali e perché sono utili per il cliente.&#10;Es:&#10;- 3 test completi: Simula l'esperienza reale dell'esame.&#10;- Lezioni video online: Permette allo studente di ripassare in autonomia." />
          </div>
          
          <div className="form-group">
            <label>Descrizione della Buyer Persona</label>
            <textarea value={buyerPersonaSummary} onChange={(e) => setBuyerPersonaSummary(e.target.value)} placeholder="Descrivi il tuo cliente ideale.&#10;Es: Genitore impegnato, cerca materiali affidabili per aiutare il figlio a superare l'ansia da esame. Ha poco tempo e vuole strumenti pratici." />
          </div>

          <div className="form-group">
            <label>Esempio Output per Recensioni (Opzionale)</label>
            <textarea value={esempioOutputRecensioni} onChange={(e) => setEsempioOutputRecensioni(e.target.value)} placeholder="Incolla qui un esempio di recensioni per guidare lo stile dell'AI." />
          </div>

          <div className="button-group">
            <button onClick={() => handleSubmit('reviews')} disabled={isLoading}>
              {isLoading ? 'Generando...' : 'Genera Recensioni Editoriali'}
            </button>
            <button onClick={() => handleSubmit('about_page')} disabled={isLoading}>
              {isLoading ? 'Generando...' : 'Genera Pagina Autore/Editore'}
            </button>
          </div>
        </div>

        <div className="output-container">
          <h2>Output Generato</h2>
          {isLoading && <p className="loading-message">Generazione in corso...</p>}
          {error && <p className="error-message">{error}</p>}
          <pre>{output}</pre>
        </div>
      </main>
    </div>
  );
}

export default App;

