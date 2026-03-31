import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { CourseLayout } from './components/CourseLayout';
import { CourseView } from './components/CourseView';
import { CourseProvider } from './contexts/CourseContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import SignUpPage from './components/SignUpPage';
import TrainingDashboard from './components/Dashboard';
import { getParagraphForAge } from './paragraphs';
import { assessReading, getHealth } from './api';
import { AssessmentResponse } from './types';
import './theme.css';
import './App.css';

type AppPage = 'login' | 'signup' | 'dashboard' | 'training';

function AppContent() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [currentPage, setCurrentPage] = useState<AppPage>('login');
  const [age, setAge] = useState<number>(12); // Default age for paragraph selection
  const [paragraph, setParagraph] = useState<string>('');
  const [assessmentResults, setAssessmentResults] = useState<AssessmentResponse | null>(null);
  const [appIsLoading, setAppIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Redirect based on authentication state
  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        setCurrentPage('dashboard');
        // Set age from user profile if available
        if (user?.age) {
          setAge(user.age);
        }
      } else {
        setCurrentPage('login');
      }
    }
  }, [isAuthenticated, isLoading, user?.age]);

  // Check backend health and initialize paragraph on component mount
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
    
    // Initialize paragraph with default age
    const selectedParagraph = getParagraphForAge(age);
    setParagraph(selectedParagraph);
  }, [age]);

  const handleAgeSubmit = (selectedAge: number) => {
    setAge(selectedAge);
    const selectedParagraph = getParagraphForAge(selectedAge);
    setParagraph(selectedParagraph);
  };

  const handleReadingComplete = async (audioBlob: Blob, recognizedText: string) => {
    setAppIsLoading(true);
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
      setAppIsLoading(false);
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

  const navigateTo = (page: AppPage) => {
    setCurrentPage(page);
  };

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Render different pages based on authentication and current page
  if (!isAuthenticated) {
    return (
      <div className="app">
        {currentPage === 'signup' ? (
          <SignUpPage onNavigate={(page) => navigateTo(page === 'dashboard' ? 'dashboard' : page)} />
        ) : (
          <LoginPage onNavigate={(page) => navigateTo(page === 'dashboard' ? 'dashboard' : page)} />
        )}
      </div>
    );
  }

  // User is authenticated
  if (currentPage === 'dashboard') {
    return (
      <div className="app">
        <TrainingDashboard onNavigate={(page) => navigateTo(page === 'training' ? 'training' : page)} />
      </div>
    );
  }

  // Training course view
  return (
    <div className="app">
      <Navigation onDashboard={() => navigateTo('dashboard')} />
      <CourseLayout onEndSession={() => navigateTo('dashboard')}>
        <CourseView
          age={age}
          paragraph={paragraph}
          assessmentResults={assessmentResults}
          isLoading={appIsLoading}
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
      <AuthProvider>
        <CourseProvider>
          <AppContent />
        </CourseProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
