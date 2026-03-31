import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import './CourseNavigation.css';

export interface CourseNavigationProps {
  onNextClick?: () => void;
  onPreviousClick?: () => void;
}

export const CourseNavigation: React.FC<CourseNavigationProps> = ({
  onNextClick,
  onPreviousClick,
}) => {
  const course = useCourse();
  const steps = [
    'reading-assessment',
    'result-analysis',
    'pronunciation-training',
    'eye-focus-test',
    'phrase-training',
  ];

  const currentIndex = steps.indexOf(course.currentStep);
  const isFirstStep = currentIndex === 0;
  const isLastStep = currentIndex === steps.length - 1;
  const canAdvance = course.canAdvance();

  const handleNext = () => {
    if (onNextClick) {
      onNextClick();
    } else {
      course.goNextStep();
    }
  };

  const handlePrevious = () => {
    if (onPreviousClick) {
      onPreviousClick();
    } else {
      course.goPreviousStep();
    }
  };

  return (
    <div className="course-navigation">
      <button
        className={`nav-button previous-button ${isFirstStep ? 'disabled' : ''}`}
        onClick={handlePrevious}
        disabled={isFirstStep}
        title={isFirstStep ? 'This is the first step' : 'Go to previous step'}
      >
        <span className="button-icon">←</span>
        <span className="button-text">Previous Step</span>
      </button>

      <div className="step-indicator">
        <span className="step-info">
          Step {currentIndex + 1} of {steps.length}
        </span>
        <div className="mini-progress-bar">
          <div 
            className="mini-progress-fill"
            style={{ width: `${((currentIndex + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>

      <button
        className={`nav-button next-button ${!canAdvance || isLastStep ? 'disabled' : ''}`}
        onClick={handleNext}
        disabled={!canAdvance || isLastStep}
        title={
          !canAdvance 
            ? 'Complete current step to continue' 
            : isLastStep 
            ? 'This is the last step'
            : 'Go to next step'
        }
      >
        <span className="button-text">Next Step</span>
        <span className="button-icon">→</span>
      </button>
    </div>
  );
};
