import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { CourseLayout } from './components/CourseLayout';
import { CourseView } from './components/CourseView';
import { CourseProvider } from './contexts/CourseContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { getParagraphForAge } from './paragraphs';
import { assessReading, getHealth } from './api';
import { AssessmentResponse } from './types';
import './theme.css';
import './App.css';

function AppContent() {
  const [age, setAge] = useState<number>(0);
  const [paragraph, setParagraph] = useState<string>('');
  const [assessmentResults, setAssessmentResults] = useState<AssessmentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Check backend health on component mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await getHealth();
        console.log('✅ Backend is healthy');
      } catch (err) {
        console.warn('⚠️ Backend not responding - functionality limited');
      }
    };

    checkBackend();
  }, []);

  const handleAgeSubmit = (selectedAge: number) => {
    setAge(selectedAge);
    const selectedParagraph = getParagraphForAge(selectedAge);
    setParagraph(selectedParagraph);
  };

  const handleReadingComplete = async (audioBlob: Blob, recognizedText: string) => {
    setIsLoading(true);
    setError('');

    try {
      console.log('📤 Processing assessment...');
      const response = await assessReading(age, paragraph, audioBlob, recognizedText);
      console.log('📊 Assessment response received:', response);
      setAssessmentResults(response);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to assess reading. Please try again.';
      console.error('Assessment error:', errorMessage);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setError('');
  };

  const handleRestart = () => {
    setAge(0);
    setParagraph('');
    setAssessmentResults(null);
    setError('');
  };

  return (
    <div className="app">
      <Navigation />
      <CourseLayout>
        <CourseView
          age={age}
          paragraph={paragraph}
          assessmentResults={assessmentResults}
          isLoading={isLoading}
          error={error}
          onAgeSubmit={handleAgeSubmit}
          onReadingComplete={handleReadingComplete}
          onRetry={handleRetry}
          onRestart={handleRestart}
        />
      </CourseLayout>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <CourseProvider>
        <AppContent />
      </CourseProvider>
    </ThemeProvider>
  );
}

export default App;
