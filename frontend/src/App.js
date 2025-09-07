import React, { useState } from 'react';
import './App.css';

function App() {
  // NUOVO: Stato per memorizzare la scelta del tipo di contenuto
  const [contentType, setContentType] = useState('penName'); // 'penName' è il valore di default

  const [prompt, setPrompt] = useState('');
  const [dati, setDati] = useState('');
  const [esempio, setEsempio] = useState('');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [penName, setPenName] = useState('');
  const [resourceTitle, setResourceTitle] = useState('');
  

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setOutput('');

    try {
      const response = await fetch('/api/generate', { // Rimuoviamo l'URL completo, Render lo gestirà
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          // NUOVO: Inviamo anche il tipo di contenuto
          content_type: contentType,
          prompt: prompt,
          dati_input: dati,
          esempio_output: esempio,
          pen_name: penName,            
          resource_title: resourceTitle,
        }),
      });

      if (!response.ok) {
        throw new Error(`Errore dal server: ${response.statusText}`);
      }

      const data = await response.json();
      setOutput(data.output);
    } catch (error) {
      setOutput(`Si è verificato un errore: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Generatore di Contenuti Editoriali</h1>
      <form onSubmit={handleSubmit}>
        {/* NUOVO: Menu a tendina (select) */}
        <select value={contentType} onChange={(e) => setContentType(e.target.value)} required>
          <option value="penName">Pen Name Description + Reviews</option>
          <option value="publisher">Publishing House Description + Reviews</option>
        </select>
        <input 
          type="text" 
          value={penName} 
          onChange={(e) => setPenName(e.target.value)} 
          placeholder="Inserisci qui il Pen Name (es. Dr. Jane Smith)" 
          required 
        />
        <input 
          type="text" 
          value={resourceTitle} 
          onChange={(e) => setResourceTitle(e.target.value)} 
          placeholder="Inserisci qui il Titolo della Risorsa (es. Med-Surg Mastery)" 
          required 
        />
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Prompt aggiuntivo (opzionale)" />
        <textarea value={dati} onChange={(e) => setDati(e.target.value)} placeholder="Dati su cui costruire (es. nome autore, genere libri, valori...)" required />
        <textarea value={esempio} onChange={(e) => setEsempio(e.target.value)} placeholder="Esempio di output a cui ispirarsi" required />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generazione...' : 'Genera'}
        </button>
      </form>
      <div className="output-area">
        <h2>Output Generato</h2>
        <pre>{output}</pre>
      </div>
    </div>
  );
}

export default App;