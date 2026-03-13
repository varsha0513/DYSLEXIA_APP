import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { AgeInput } from './AgeInput';
import './AgeSelectionStep.css';

export interface AgeSelectionStepProps {
  onAgeSubmit: (age: number) => void;
}

export const AgeSelectionStep: React.FC<AgeSelectionStepProps> = ({ onAgeSubmit }) => {
  const { markStepComplete } = useCourse();

  const handleAgeSubmit = (age: number) => {
    markStepComplete('age-selection');
    onAgeSubmit(age);
  };

  return (
    <div className="age-selection-step">
      <StepHeader
        icon="👤"
        title="Welcome to Your Learning Journey"
        subtitle="Let's start with your age"
        description="This helps us personalize your reading assessment with appropriate content difficulty."
      />

      <div className="age-selection-container">
        <AgeInput onAgeSubmit={handleAgeSubmit} />
      </div>

      <div className="step-motivational-message">
        <p>📚 Don't worry! This assessment is designed to help you improve your reading skills.</p>
      </div>
    </div>
  );
};
