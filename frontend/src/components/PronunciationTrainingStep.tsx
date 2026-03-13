import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { PronunciationTrainingWidget } from './PronunciationTrainingWidget';
import { AssessmentResponse } from '../types';
import './PronunciationTrainingStep.css';

export interface PronunciationTrainingStepProps {
  assessmentResults: AssessmentResponse;
}

export const PronunciationTrainingStep: React.FC<PronunciationTrainingStepProps> = ({
  assessmentResults,
}) => {
  const { markStepComplete } = useCourse();

  const handleComplete = () => {
    markStepComplete('pronunciation-training');
  };

  // Extract words to practice from assessment results
  const wordsToPractice: string[] = [];
  
  // Add correct words from wrong_words array
  if (assessmentResults.assistance?.wrong_words && assessmentResults.assistance.wrong_words.length > 0) {
    assessmentResults.assistance.wrong_words.forEach(([_, correct]) => {
      if (!wordsToPractice.includes(correct)) {
        wordsToPractice.push(correct);
      }
    });
  }
  
  // Add missing words
  if (assessmentResults.assistance?.missing_words && assessmentResults.assistance.missing_words.length > 0) {
    assessmentResults.assistance.missing_words.forEach(word => {
      if (!wordsToPractice.includes(word)) {
        wordsToPractice.push(word);
      }
    });
  }

  // If no words to practice, provide a placeholder
  if (wordsToPractice.length === 0) {
    wordsToPractice.push(...assessmentResults.reference_text.split(/\s+/).slice(0, 5));
  }

  return (
    <div className="pronunciation-training-step">
      <StepHeader
        icon="🗣️"
        title="Pronunciation Training"
        subtitle="Master the words you found challenging"
        description="Let's work on the words you pronounced differently. Listen, repeat, and improve your pronunciation with instant feedback!"
      />

      <div className="pronunciation-training-container">
        <PronunciationTrainingWidget
          words={wordsToPractice}
          onComplete={handleComplete}
        />
      </div>

      <div className="pronunciation-tips">
        <h3 className="tips-title">💡 Tips for Better Pronunciation</h3>
        <ul className="tips-list">
          <li>Speak clearly and at a normal pace</li>
          <li>Listen carefully to the correct pronunciation</li>
          <li>Try to mimic the exact sound and rhythm</li>
          <li>Don't rush - take your time with each word</li>
          <li>Practice makes perfect!</li>
        </ul>
      </div>
    </div>
  );
};
