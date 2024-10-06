import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [trials, setTrials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to handle the search request
  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Please enter a search term.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/search', {
        params: { query }
      });
      setTrials(response.data);  // Set the clinical trials returned from Flask
    } catch (err) {
      console.error(err);
      setError("An error occurred while fetching the data.");
    }

    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Clinical Trials Search</h1>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search for a disease or condition..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => { if (e.key === 'Enter') handleSearch(); }}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      <div className="results">
        {trials.length > 0 ? (
          trials.map((trial, index) => (
            <div key={index} className="trial-card">
            <a href={`https://clinicaltrials.gov/study/${trial.nctId}`} target="_blank" rel="noopener noreferrer">
               <h2>{trial.briefTitle}</h2>
            </a>              
            <h3>{trial.officialTitle}</h3>
              <p>{trial.briefSummary}</p>
              <p><strong>NCT ID:</strong> {trial.nctId}</p>
            </div>
          ))
        ) : (
          !loading && <p>No results found.</p>
        )}
      </div>
    </div>
  );
}

export default App;