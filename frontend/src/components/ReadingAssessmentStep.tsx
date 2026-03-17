import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { ReadingTask } from './ReadingTask';
import './ReadingAssessmentStep.css';

export interface ReadingAssessmentStepProps {
  age: number;
  paragraph: string;
  onComplete: (audioBlob: Blob, recognizedText: string) => void;
}

export const ReadingAssessmentStep: React.FC<ReadingAssessmentStepProps> = ({
  age,
  paragraph,
  onComplete,
}) => {
  const { markStepComplete, goNextStep } = useCourse();

  const handleComplete = (audioBlob: Blob, recognizedText: string) => {
    markStepComplete('reading-assessment');
    onComplete(audioBlob, recognizedText);
    goNextStep();
  };

  return (
    <div className="reading-assessment-step">
      <StepHeader
        icon="📖"
        title="Reading Assessment"
        subtitle="Let's assess your reading skills"
        description="Please read the paragraph below clearly and at your own pace. The system will record your voice and analyze your reading."
      />

      <div className="reading-assessment-container">
        <ReadingTask age={age} paragraph={paragraph} onComplete={handleComplete} />
      </div>

      <div className="reading-tips">
        <div className="tip-item">
          <span className="tip-icon">🎙️</span>
          <span className="tip-text">Make sure your microphone is working</span>
        </div>
        <div className="tip-item">
          <span className="tip-icon">📍</span>
          <span className="tip-text">Find a quiet place to minimize background noise</span>
        </div>
        <div className="tip-item">
          <span className="tip-icon">⏱️</span>
          <span className="tip-text">Read at a comfortable, natural pace</span>
        </div>
      </div>
    </div>
  );
};
