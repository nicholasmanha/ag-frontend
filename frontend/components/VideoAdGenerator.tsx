'use client';

import { useState } from 'react';

interface TaskStatus {
  status: 'processing' | 'completed' | 'failed';
  progress?: string;
  base_image?: string;
  video?: string;
  error?: string;
}

interface VideoAdResult {
  base_image: string;
  video: string;
  imageUrl?: string;
  videoUrl?: string;
}

export default function VideoAdGenerator() {
  const [basePrompt, setBasePrompt] = useState('');
  const [adPrompt, setAdPrompt] = useState('');
  const [result, setResult] = useState<VideoAdResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>('');

  const FLASK_API_URL = process.env.NEXT_PUBLIC_FLASK_API_URL || 'http://localhost:5000';
  const API_KEY = process.env.NEXT_PUBLIC_FREEPIK_API_KEY || '';

  const pollTaskStatus = async (id: string) => {
    const maxAttempts = 60; // 5 minutes max (60 * 5 seconds)
    let attempts = 0;

    const poll = async (): Promise<void> => {
      try {
        const response = await fetch(`${FLASK_API_URL}/api/task-status/${id}`);
        
        if (!response.ok) {
          throw new Error('Failed to check task status');
        }

        const data: TaskStatus = await response.json();
        
        if (data.status === 'completed' && data.base_image && data.video) {
          setResult({
            base_image: data.base_image,
            video: data.video,
            imageUrl: `${FLASK_API_URL}${data.base_image}`,
            videoUrl: `${FLASK_API_URL}${data.video}`
          });
          setLoading(false);
          setProgress('');
          return;
        } else if (data.status === 'failed') {
          throw new Error(data.error || 'Video generation failed');
        } else if (data.status === 'processing') {
          setProgress(data.progress || 'Processing...');
          attempts++;
          
          if (attempts >= maxAttempts) {
            throw new Error('Task timed out');
          }
          
          // Poll again after 5 seconds
          setTimeout(() => poll(), 5000);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setLoading(false);
        setProgress('');
      }
    };

    await poll();
  };

  const generateVideoAd = async (useAsync: boolean = true) => {
    if (!basePrompt.trim() || !adPrompt.trim()) {
      setError('Both prompts are required');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setProgress('Initializing...');
    
    try {
      const endpoint = useAsync ? '/api/create-video-ad-async' : '/api/create-video-ad';
      
      const response = await fetch(`${FLASK_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Freepik-API-Key': API_KEY,
        },
        body: JSON.stringify({
          base_prompt: basePrompt,
          ad_prompt: adPrompt,
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate video ad');
      }

      const data = await response.json();

      if (useAsync) {
        // Async mode - poll for status
        setTaskId(data.task_id);
        setProgress('Task created, processing...');
        await pollTaskStatus(data.task_id);
      } else {
        // Sync mode - immediate result
        setResult({
          base_image: data.base_image,
          video: data.video,
          imageUrl: `${FLASK_API_URL}${data.base_image}`,
          videoUrl: `${FLASK_API_URL}${data.video}`
        });
        setLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
      setProgress('');
    }
  };

  const downloadFile = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-2 text-center">
          AI Video Ad Generator
        </h1>
        <p className="text-gray-600 text-center mb-8">
          Create stunning video ads from text prompts
        </p>

        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Input Section */}
          <div className="space-y-6 mb-8">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Base Image Prompt
              </label>
              <textarea
                value={basePrompt}
                onChange={(e) => setBasePrompt(e.target.value)}
                placeholder="e.g., A sleek sports car in a futuristic city at sunset"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={3}
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Video Animation Prompt
              </label>
              <textarea
                value={adPrompt}
                onChange={(e) => setAdPrompt(e.target.value)}
                placeholder="e.g., Camera zooms in dramatically while neon lights pulse"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={3}
                disabled={loading}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => generateVideoAd(true)}
              disabled={loading || !basePrompt.trim() || !adPrompt.trim()}
              className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Generating...' : 'Generate Video Ad'}
            </button>
          </div>

          {/* Progress Indicator */}
          {loading && progress && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                <p className="text-blue-700">{progress}</p>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">Error: {error}</p>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="mt-8 space-y-6">
              <div className="border-t border-gray-200 pt-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">
                  Generated Content
                </h2>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Base Image */}
                  <div className="border-l-4 border-purple-500 pl-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                        <span className="text-2xl mr-2">🖼️</span>
                        Base Image
                      </h3>
                      <button
                        onClick={() => downloadFile(result.imageUrl!, 'base-image.png')}
                        className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                      >
                        Download
                      </button>
                    </div>
                    {result.imageUrl && (
                      <img
                        src={result.imageUrl}
                        alt="Generated base image"
                        className="w-full rounded-lg shadow-md"
                      />
                    )}
                  </div>

                  {/* Video */}
                  <div className="border-l-4 border-blue-500 pl-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                        <span className="text-2xl mr-2">🎬</span>
                        Video Ad
                      </h3>
                      <button
                        onClick={() => downloadFile(result.videoUrl!, 'video-ad.mp4')}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Download
                      </button>
                    </div>
                    {result.videoUrl && (
                      <video
                        src={result.videoUrl}
                        controls
                        className="w-full rounded-lg shadow-md"
                        autoPlay
                        loop
                      />
                    )}
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => {
                    setResult(null);
                    setBasePrompt('');
                    setAdPrompt('');
                  }}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Clear & Start Over
                </button>
                <button
                  onClick={() => generateVideoAd(true)}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all"
                >
                  Generate Another
                </button>
              </div>
            </div>
          )}

          {/* Sample Prompts */}
          {!result && !loading && (
            <div className="mt-8 p-6 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                💡 Example Prompts
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div>
                  <strong>Base:</strong> "A premium coffee cup on a minimalist desk with morning sunlight"
                  <br />
                  <strong>Video:</strong> "Steam rising gently from the cup, camera slowly zooming in"
                </div>
                <div>
                  <strong>Base:</strong> "A smartphone displaying a vibrant app interface"
                  <br />
                  <strong>Video:</strong> "Screen lighting up with smooth animations and notifications"
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Info Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Powered by Freepik Gemini API • Video generation may take 2-3 minutes</p>
        </div>
      </div>
    </div>
  );
}