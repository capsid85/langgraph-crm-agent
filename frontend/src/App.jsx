import React, { useState } from 'react';
import axios from 'axios';
import SearchForm from './components/SearchForm';
import EnrichmentResult from './components/EnrichmentResult';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleEnrichment = async (companyName) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // In production, configure API URL appropriately
      const response = await axios.post('http://localhost:8000/enrich', {
        company_name: companyName
      });
      
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || 'An error occurred during enrichment');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>Agentic Enrichment</h1>
        <p>AI-powered CRM data enrichment and resolution via LangGraph</p>
      </div>
      
      <SearchForm onSubmit={handleEnrichment} isLoading={isLoading} />
      
      {error && (
        <div className="glass-card" style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
          <p style={{ color: '#fca5a5', textAlign: 'center' }}>Error: {error}</p>
        </div>
      )}

      {result && <EnrichmentResult result={result} />}
    </div>
  );
}

export default App;
