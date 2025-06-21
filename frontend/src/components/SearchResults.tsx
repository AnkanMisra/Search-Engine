import React from 'react';
import './SearchResults.css';

interface SearchResult {
  id: string;
  title: string;
  content: string;
  url: string;
  score: number;
}

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
}

const SearchResults: React.FC<SearchResultsProps> = ({ results, loading }) => {
  if (loading) {
    return (
      <div className="search-results">
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Searching...</p>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="search-results">
      {results.map((result) => (
        <div key={result.id} className="search-result-item">
          <div className="result-header">
            <h3 className="result-title">
              <a 
                href={result.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="result-link"
              >
                {result.title}
              </a>
            </h3>
            <div className="result-url">{result.url}</div>
          </div>
          <p className="result-content">
            {result.content.length > 300 
              ? `${result.content.substring(0, 300)}...` 
              : result.content
            }
          </p>
          <div className="result-metadata">
            <span className="result-score">Score: {result.score.toFixed(2)}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SearchResults; 