import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useCourse } from '../contexts/CourseContext';
import './Dashboard.css';

interface TrainingStep {
  id: string;
  name: string;
  title: string;
  icon: string;
  description: string;
  completed: boolean;
}

interface DashboardProps {
  onNavigate?: (page: 'training' | 'login') => void;
}

const TrainingDashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const { stepCompletion, currentStep, setCurrentStep } = useCourse();

  // Training steps with their details
  const trainingSteps: TrainingStep[] = [
    {
      id: 'reading-assessment',
      name: 'reading-assessment',
      title: 'Reading Assessment',
      icon: '📖',
      description: 'Read a paragraph aloud while we assess your performance',
      completed: stepCompletion['reading-assessment'] || false,
    },
    {
      id: 'result-analysis',
      name: 'result-analysis',
      title: 'Result Analysis',
      icon: '📊',
      description: 'Review detailed metrics and dyslexia risk assessment',
      completed: stepCompletion['result-analysis'] || false,
    },
    {
      id: 'pronunciation-training',
      name: 'pronunciation-training',
      title: 'Pronunciation Training',
      icon: '🎤',
      description: 'Practice pronouncing difficult words correctly',
      completed: stepCompletion['pronunciation-training'] || false,
    },
    {
      id: 'eye-focus-test',
      name: 'eye-focus-test',
      title: 'Eye Focus Training',
      icon: '👁️',
      description: 'Train your eye tracking with word highlighting exercises',
      completed: stepCompletion['eye-focus-test'] || false,
    },
    {
      id: 'phrase-training',
      name: 'phrase-training',
      title: 'Phrase Reading (Chunk Training)',
      icon: '📖',
      description: 'Learn to read in meaningful phrases instead of word-by-word',
      completed: stepCompletion['phrase-training'] || false,
    },
  ];

  const handleStartTraining = () => {
    // If no steps completed yet, go to reading assessment
    const completedCount = Object.values(stepCompletion).filter(Boolean).length;
    if (completedCount === 0) {
      setCurrentStep('reading-assessment');
    } else {
      // Go to the first incomplete step
      const incompletedStep = trainingSteps.find(step => !step.completed);
      if (incompletedStep) {
        setCurrentStep(incompletedStep.id as any);
      }
    }
    onNavigate?.('training');
  };

  const handleStepClick = (stepId: string) => {
    setCurrentStep(stepId as any);
    onNavigate?.('training');
  };

  const completedCount = trainingSteps.filter(step => step.completed).length;
  const progressPercentage = Math.round((completedCount / trainingSteps.length) * 100);

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Training Dashboard 🎓</h1>
          <p>Welcome, {user?.username || 'User'}!</p>
        </div>
        <button className="logout-button" onClick={logout}>
          📤 Logout
        </button>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Progress Overview */}
        <section className="progress-section">
          <div className="progress-card">
            <h2>Your Progress</h2>
            <div className="progress-stats">
              <div className="stat">
                <span className="stat-label">Completed Steps</span>
                <span className="stat-value">{completedCount}/{trainingSteps.length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Overall Progress</span>
                <span className="stat-value">{progressPercentage}%</span>
              </div>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progressPercentage}%` }}></div>
            </div>
          </div>
        </section>

        {/* Quick Action */}
        <section className="quick-action-section">
          <button className="continue-button" onClick={handleStartTraining}>
            {completedCount === 0 ? '🚀 Start Training' : '▶️ Continue Training'}
          </button>
        </section>

        {/* Training Steps */}
        <section className="steps-section">
          <h2>Training Exercises</h2>
          <div className="steps-grid">
            {trainingSteps.map((step, index) => (
              <div
                key={step.id}
                className={`step-card ${step.completed ? 'completed' : ''}`}
                onClick={() => handleStepClick(step.id)}
              >
                <div className="step-number">{index + 1}</div>
                <div className="step-icon">{step.icon}</div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
                {step.completed && (
                  <div className="completion-badge">
                    <span className="checkmark">✓</span>
                    <span>Completed</span>
                  </div>
                )}
                <div className="step-arrow">→</div>
              </div>
            ))}
          </div>
        </section>

        {/* User Info */}
        <section className="user-info-section">
          <div className="info-card">
            <h3>Account Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Username:</span>
                <span className="info-value">{user?.username}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email:</span>
                <span className="info-value">{user?.email}</span>
              </div>
              {user?.age && (
                <div className="info-item">
                  <span className="info-label">Age:</span>
                  <span className="info-value">{user.age}</span>
                </div>
              )}
              <div className="info-item">
                <span className="info-label">Joined:</span>
                <span className="info-value">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default TrainingDashboard;
