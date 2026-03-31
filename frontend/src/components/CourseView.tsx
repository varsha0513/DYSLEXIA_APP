import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { ReadingAssessmentStep } from './ReadingAssessmentStep';
import { ResultAnalysisStep } from './ResultAnalysisStep';
import { PronunciationTrainingStep } from './PronunciationTrainingStep';
import { EyeFocusTestStep } from './EyeFocusTestStep';
import { PhraseTrainingStep } from './PhraseTrainingStep';
import { AssessmentResponse } from '../types';
import { Loading } from './Loading';
import { ErrorDisplay } from './ErrorDisplay';

export interface CourseViewProps {
  age: number;
  paragraph: string;
  assessmentResults: AssessmentResponse | null;
  isLoading: boolean;
  error: string;
  onAgeSubmit: (age: number) => void;
  onReadingComplete: (audioBlob: Blob, recognizedText: string) => void;
  onRetry: () => void;
  onRestart: () => void;
}

export const CourseView: React.FC<CourseViewProps> = ({
  age,
  paragraph,
  assessmentResults,
  isLoading,
  error,
  onAgeSubmit,
  onReadingComplete,
  onRetry,
  onRestart,
}) => {
  const { currentStep } = useCourse();

  if (isLoading) {
    return <Loading />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={onRetry} />;
  }

  switch (currentStep) {
    case 'reading-assessment':
      return (
        <ReadingAssessmentStep
          age={age}
          paragraph={paragraph}
          onComplete={onReadingComplete}
        />
      );

    case 'result-analysis':
      return assessmentResults ? (
        <ResultAnalysisStep results={assessmentResults} />
      ) : (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>No assessment results available. Please go back and complete the reading assessment.</p>
        </div>
      );

    case 'pronunciation-training':
      return assessmentResults ? (
        <PronunciationTrainingStep assessmentResults={assessmentResults} />
      ) : (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>No assessment results available. Please go back and complete the reading assessment.</p>
        </div>
      );

    case 'eye-focus-test':
      return <EyeFocusTestStep paragraph={paragraph} />;

    case 'phrase-training':
      return <PhraseTrainingStep paragraph={paragraph} />;

    default:
      return null;
  }
};
