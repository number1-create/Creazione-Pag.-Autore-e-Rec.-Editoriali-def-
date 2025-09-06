import React, { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [dati, setDati] = useState('');
  const [esempio, setEsempio] = useState('');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Inserisci qui l'URL del tuo backend su Render quando sarà online
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000'; 

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setOutput('');
    try {
      const response = await fetch(`${apiUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          dati_input: dati,
          esempio_output: esempio,
        }),
      });
      if (!response.ok) throw new Error(`Errore dal server`);
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
      <h1>Generatore di Contenuti</h1>
      <form onSubmit={handleSubmit}>
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Prompt da utilizzare" required />
        <textarea value={dati} onChange={(e) => setDati(e.target.value)} placeholder="Dati su cui costruire il prodotto" required />
        <textarea value={esempio} onChange={(e) => setEsempio(e.target.value)} placeholder="Esempio di output" required />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generazione...' : 'Genera'}
        </button>
      </form>
      <div className="output-area">
        <h2>Output</h2>
        <pre>{output}</pre>
      </div>
    </div>
  );
}
export default App;