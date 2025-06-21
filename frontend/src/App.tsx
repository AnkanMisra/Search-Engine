import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import './App.css';

interface SearchResult {
  id: string;
  title: string;
  content: string;
  url: string;
  score: number;
}

const App: React.FC = () => {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [query, setQuery] = useState<string>('');

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setQuery(searchQuery);

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      
      if (data.success) {
        setResults(data.results || []);
      } else {
        console.error('Search failed:', data.error);
        setResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">🔍 Search Engine MVP</h1>
          <p className="subtitle">Find what you're looking for</p>
        </header>

        <SearchBar onSearch={handleSearch} loading={loading} />

        {query && (
          <div className="results-info">
            {loading ? (
              <p>Searching for "{query}"...</p>
            ) : (
              <p>Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"</p>
            )}
          </div>
        )}

        <SearchResults results={results} loading={loading} />
      </div>
    </div>
  );
};

export default App; 