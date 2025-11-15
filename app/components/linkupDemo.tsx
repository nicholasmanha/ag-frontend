// app/components/LinkupSearch.tsx
'use client';

import { useState } from 'react';

interface SearchResult {
  name: string;
  url: string;
  content: string;
}

export default function LinkupSearch() {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('standard');
  const [outputType, setOutputType] = useState('searchResults');
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const res = await fetch('/api/linkup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          depth,
          outputType,
        }),
      });

      // Get the raw text first to see what we're getting
      const text = await res.text();
      console.log('Raw response:', text);

      let data;
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        setError(`Invalid JSON response: ${text.substring(0, 200)}`);
        return;
      }

      if (!res.ok) {
        setError(data.error || data.details || 'Search failed');
        return;
      }

      setResults(data.data);
    } catch (err) {
      setError('Failed to connect to API: ' + String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-2">Linkup Search Demo</h1>
      <p className="text-gray-600 mb-8">Search the web using Linkup SDK</p>

      {/* Search Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Search Query</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="What do you want to search for?"
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
          />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Search Depth</label>
            <select
              value={depth}
              onChange={(e) => setDepth(e.target.value)}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="standard">Standard</option>
              <option value="deep">Deep</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Output Type</label>
            <select
              value={outputType}
              onChange={(e) => setOutputType(e.target.value)}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="searchResults">Search Results</option>
              <option value="sourcedAnswer">Sourced Answer</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium transition-colors"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-6">
          <p className="font-medium">Error:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Results</h2>
          
          {/* Display based on outputType */}
          {outputType === 'sourcedAnswer' && results.answer && (
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h3 className="text-lg font-semibold mb-3">Answer</h3>
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{results.answer}</p>
              
              {results.sources && results.sources.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold mb-2">Sources:</h4>
                  <ul className="space-y-2">
                    {results.sources.map((source: any, idx: number) => (
                      <li key={idx} className="text-sm">
                        <a 
                          href={source.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {source.name || source.url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {outputType === 'searchResults' && results.results && results.results.length > 0 && (
            <>
              <p className="text-gray-600">Found {results.results.length} results</p>
              {results.results.map((result: any, index: number) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                  <h3 className="text-xl font-semibold text-blue-600 mb-2">
                    <a href={result.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {result.name}
                    </a>
                  </h3>
                  <p className="text-sm text-gray-500 mb-3 break-all">{result.url}</p>
                  <p className="text-gray-700 leading-relaxed">{result.content}</p>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {results && outputType === 'searchResults' && results.results && results.results.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-6 py-4 rounded-lg">
          No results found for your query.
        </div>
      )}
    </div>
  );
}