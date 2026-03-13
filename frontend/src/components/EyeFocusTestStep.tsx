import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { EyeFocusWordTracking, EyeFocusResults } from './EyeFocusWordTracking';
import './EyeFocusTestStep.css';

export interface EyeFocusTestStepProps {
  paragraph: string;
}

export const EyeFocusTestStep: React.FC<EyeFocusTestStepProps> = ({ paragraph }) => {
  const { markStepComplete } = useCourse();

  React.useEffect(() => {
    console.log('EyeFocusTestStep - paragraph received:', paragraph);
  }, [paragraph]);

  const handleComplete = (results: EyeFocusResults) => {
    console.log('Eye Focus training completed:', results);
    markStepComplete('eye-focus-test');
  };

  if (!paragraph || paragraph.trim().length === 0) {
    return (
      <div className="eye-focus-test-step">
        <StepHeader
          icon="👁️"
          title="Eye Focus Word Tracking"
          subtitle="Train your visual focus on each word"
          description="Improve your eye tracking ability by following highlighted words while reading aloud."
        />
        <div className="eye-focus-container" style={{ textAlign: 'center', padding: '40px' }}>
          <p>⚠️ No text available for eye focus training. Please complete the reading assessment first.</p>
          <button 
            className="btn btn-primary"
            onClick={() => markStepComplete('eye-focus-test')}
            style={{ marginTop: '20px' }}
          >
            Skip This Step
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="eye-focus-test-step">
      <StepHeader
        icon="👁️"
        title="Eye Focus Word Tracking"
        subtitle="Train your visual focus on each word"
        description="Improve your eye tracking ability by following highlighted words while reading aloud. This helps develop consistent reading rhythm and maintains focus on the text."
      />

      <EyeFocusWordTracking paragraph={paragraph} onComplete={handleComplete} />
    </div>
  );
};
