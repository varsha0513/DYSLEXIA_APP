import React, { useState } from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import SpeedTrainerWidget from './SpeedTrainerWidget';
import { AssessmentResponse } from '../types';
import './ReadingSpeedTrainingStep.css';

export interface ReadingSpeedTrainingStepProps {
  age: number;
  assessmentResults: AssessmentResponse;
}

export const ReadingSpeedTrainingStep: React.FC<ReadingSpeedTrainingStepProps> = ({
  age,
  assessmentResults,
}) => {
  const { markStepComplete } = useCourse();
  const [showWidget, setShowWidget] = useState(true);

  const handleComplete = () => {
    setShowWidget(false);
    markStepComplete('reading-speed-training');
  };

  return (
    <div className="reading-speed-training-step">
      <StepHeader
        icon="⚡"
        title="Speed Improvement"
        subtitle="Improve your reading pace with chunk reading"
        description="Now let's work on improving your reading speed using chunk-based reading. Follow the highlighted phrase chunks and gradually increase your pace as you become more comfortable."
      />

      <div className="speed-training-container">
        {showWidget && (
          <SpeedTrainerWidget
            paragraph={assessmentResults.reference_text}
            isShowing={showWidget}
            onClose={handleComplete}
          />
        )}
      </div>

      <div className="speed-training-benefits">
        <h3 className="benefits-title">✨ Benefits of Speed Training</h3>
        <div className="benefits-grid">
          <div className="benefit-card">
            <span className="benefit-icon">🎯</span>
            <span className="benefit-text">Focused Reading</span>
          </div>
          <div className="benefit-card">
            <span className="benefit-icon">🧠</span>
            <span className="benefit-text">Better Comprehension</span>
          </div>
          <div className="benefit-card">
            <span className="benefit-icon">💪</span>
            <span className="benefit-text">Build Confidence</span>
          </div>
          <div className="benefit-card">
            <span className="benefit-icon">📈</span>
            <span className="benefit-text">Progressive Improvement</span>
          </div>
        </div>
      </div>
    </div>
  );
};
