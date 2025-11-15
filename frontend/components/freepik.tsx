'use client';

import { useState } from 'react';

interface Prompts {
  imagePrompt: string;
  videoPrompt: string;
  voicePrompt: string;
}

export default function PromptGenerator() {
  const [prompts, setPrompts] = useState<Prompts | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPrompts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: 'creative' // You can make this dynamic
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch prompts');
      }

      const data = await response.json();
      setPrompts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
          AI Prompt Generator
        </h1>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <button
            onClick={fetchPrompts}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating Prompts...' : 'Generate New Prompts'}
          </button>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">Error: {error}</p>
            </div>
          )}

          {prompts && (
            <div className="mt-8 space-y-6">
              {/* Image Prompt */}
              <div className="border-l-4 border-purple-500 pl-4">
                <h2 className="text-xl font-semibold text-gray-800 mb-2 flex items-center">
                  <span className="text-2xl mr-2">🖼️</span>
                  Image Prompt
                </h2>
                <p className="text-gray-700 leading-relaxed">
                  {prompts.imagePrompt}
                </p>
              </div>

              {/* Video Prompt */}
              <div className="border-l-4 border-blue-500 pl-4">
                <h2 className="text-xl font-semibold text-gray-800 mb-2 flex items-center">
                  <span className="text-2xl mr-2">🎬</span>
                  Video Prompt
                </h2>
                <p className="text-gray-700 leading-relaxed">
                  {prompts.videoPrompt}
                </p>
              </div>

              {/* Voice Prompt */}
              <div className="border-l-4 border-green-500 pl-4">
                <h2 className="text-xl font-semibold text-gray-800 mb-2 flex items-center">
                  <span className="text-2xl mr-2">🎤</span>
                  Voice Prompt
                </h2>
                <p className="text-gray-700 leading-relaxed">
                  {prompts.voicePrompt}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}