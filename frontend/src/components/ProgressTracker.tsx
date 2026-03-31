import React from 'react';
import { useCourse, CourseStep } from '../contexts/CourseContext';
import './ProgressTracker.css';

export const ProgressTracker: React.FC = () => {
  const { currentStep, stepCompletion, completionPercentage, setCurrentStep, getStepNumber, getStepTitle } = useCourse();

  const steps: CourseStep[] = [
    'reading-assessment',
    'result-analysis',
    'pronunciation-training',
    'eye-focus-test',
    'phrase-training',
  ];

  const handleStepClick = (step: CourseStep) => {
    // Only allow clicking on completed or current steps
    const stepIndex = steps.indexOf(step);
    const currentIndex = steps.indexOf(currentStep);
    
    if (stepIndex <= currentIndex || stepCompletion[step]) {
      setCurrentStep(step);
    }
  };

  return (
    <div className="progress-tracker">
      <div className="progress-header">
        <h2 className="progress-title">Learning Journey</h2>
        <div className="progress-percentage">
          {Math.round(completionPercentage)}%
        </div>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar-background">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      <div className="steps-list">
        {steps.map((step, index) => {
          const isCompleted = stepCompletion[step];
          const isCurrent = step === currentStep;
          const isAccessible = index === 0 || stepCompletion[steps[index - 1]];
          
          return (
            <div
              key={step}
              className={`step-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''} ${!isAccessible && !isCompleted ? 'disabled' : ''}`}
              onClick={() => handleStepClick(step)}
            >
              <div className="step-indicator">
                <div className="step-number">
                  {isCompleted ? (
                    <span className="checkmark">✓</span>
                  ) : isCurrent ? (
                    <span className="arrow">➤</span>
                  ) : (
                    <span className="box">⬜</span>
                  )}
                </div>
              </div>
              
              <div className="step-content">
                <div className="step-title">
                  {getStepTitle(step)}
                </div>
                <div className="step-number-label">
                  Step {getStepNumber(step)} of {steps.length}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="progress-footer">
        <div className="footer-badge">
          {completionPercentage === 100 ? (
            <>
              <span className="badge-icon">🎉</span>
              <span>Course Complete!</span>
            </>
          ) : (
            <>
              <span className="badge-icon">📚</span>
              <span>Keep going!</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
