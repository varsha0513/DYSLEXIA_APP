import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { ResultsDisplay } from './ResultsDisplay';
import { AssessmentResponse } from '../types';
import './ResultAnalysisStep.css';

export interface ResultAnalysisStepProps {
  results: AssessmentResponse;
}

export const ResultAnalysisStep: React.FC<ResultAnalysisStepProps> = ({ results }) => {
  const { markStepComplete, goNextStep } = useCourse();

  const handleContinue = () => {
    goNextStep();
  };

  React.useEffect(() => {
    markStepComplete('result-analysis');
  }, [markStepComplete]);

  return (
    <div className="result-analysis-step">
      <StepHeader
        icon="📊"
        title="Your Assessment Results"
        subtitle="Let's analyze your reading performance"
        description="Here's a detailed breakdown of your reading assessment, including accuracy, speed, and personalized recommendations."
      />

      <div className="result-analysis-container">
        <ResultsDisplay results={results} onRestart={() => {}} hideRestartButton={true} />
      </div>

      <div className="result-next-steps">
        <h3 className="next-steps-title">What's Next?</h3>
        <p className="next-steps-text">
          Based on these results, we'll work on pronunciation training and reading speed improvement.
          Let's continue to the next step!
        </p>
        <button className="btn btn-continue" onClick={handleContinue}>
          Continue to Pronunciation Training →
        </button>
      </div>
    </div>
  );
};
