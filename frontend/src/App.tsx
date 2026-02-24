import React, { useState, useEffect } from 'react';
import { AgeInput } from './components/AgeInput';
import { ReadingTask } from './components/ReadingTask';
import { ResultsDisplay } from './components/ResultsDisplay';
import { Loading } from './components/Loading';
import { ErrorDisplay } from './components/ErrorDisplay';
import { getParagraphForAge } from './paragraphs';
import { assessReading, getHealth } from './api';
import { AssessmentResponse, AppState } from './types';
import './App.css';

function App() {
  const [state, setState] = useState<AppState>('age-input');
  const [age, setAge] = useState<number>(0);
  const [paragraph, setParagraph] = useState<string>('');
  const [results, setResults] = useState<AssessmentResponse | null>(null);
  const [error, setError] = useState<string>('');

  // Check backend health on component mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await getHealth();
        console.log('✅ Backend is healthy');
      } catch (err) {
        console.warn('⚠️ Backend not responding - functionality limited');
        // Don't show error on startup, just warn
      }
    };

    checkBackend();
  }, []);

  const handleAgeSubmit = (selectedAge: number) => {
    setAge(selectedAge);
    const selectedParagraph = getParagraphForAge(selectedAge);
    setParagraph(selectedParagraph);
    setState('reading');
  };

  const handleReadingComplete = async (audioBlob: Blob) => {
    setState('loading');
    setError('');

    try {
      console.log('📤 Processing assessment...');
      const response = await assessReading(age, paragraph, audioBlob);
      console.log('📊 Assessment response received:', response);
      setResults(response);
      setState('results');
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to assess reading. Please try again.';
      console.error('Assessment error:', errorMessage);
      setError(errorMessage);
      setState('error');
    }
  };

  const handleRestart = () => {
    setState('age-input');
    setAge(0);
    setParagraph('');
    setResults(null);
    setError('');
  };

  const handleRetry = () => {
    setState('age-input');
    setError('');
  };

  return (
    <div className="app">
      {state === 'age-input' && <AgeInput onAgeSubmit={handleAgeSubmit} />}
      {state === 'reading' && (
        <ReadingTask age={age} paragraph={paragraph} onComplete={handleReadingComplete} />
      )}
      {state === 'loading' && <Loading />}
      {state === 'results' && results && (
        <ResultsDisplay results={results} onRestart={handleRestart} />
      )}
      {state === 'error' && <ErrorDisplay error={error} onRetry={handleRetry} />}
    </div>
  );
}

export default App;
