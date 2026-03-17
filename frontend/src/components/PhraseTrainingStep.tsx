import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { PhraseTrainingWidget, PhraseTrainingResults } from './PhraseTrainingWidget';
import './PhraseTrainingStep.css';

export interface PhraseTrainingStepProps {
  paragraph: string;
}

export const PhraseTrainingStep: React.FC<PhraseTrainingStepProps> = ({ paragraph }) => {
  const { markStepComplete, goNextStep } = useCourse();
  const [isComplete, setIsComplete] = React.useState(false);
  const [results, setResults] = React.useState<PhraseTrainingResults | null>(null);

  React.useEffect(() => {
    console.log('PhraseTrainingStep - paragraph received:', paragraph);
  }, [paragraph]);

  const handleComplete = (trainingResults: PhraseTrainingResults) => {
    console.log('Phrase training completed:', trainingResults);
    setResults(trainingResults);
    setIsComplete(true);
    markStepComplete('phrase-training');
  };

  const handleProceedNext = () => {
    goNextStep();
  };

  if (!paragraph || paragraph.trim().length === 0) {
    return (
      <div className="phrase-training-step">
        <StepHeader
          icon="📖"
          title="Chunk Reading (Phrase Training)"
          subtitle="Train your visual focus on phrases"
          description="Learn to read meaningful chunks of words instead of individual words."
        />
        <div className="phrase-training-container" style={{ textAlign: 'center', padding: '40px' }}>
          <p>⚠️ No text available for phrase training. Please complete the reading assessment first.</p>
          <button
            className="btn btn-primary"
            onClick={() => markStepComplete('phrase-training')}
            style={{ marginTop: '20px' }}
          >
            Skip This Step
          </button>
        </div>
      </div>
    );
  }

  // Show completion celebration
  if (isComplete && results) {
    return (
      <div className="phrase-training-step">
        <StepHeader
          icon="📖"
          title="Phrase Training Complete!"
          subtitle="Excellent work!"
          description="You've successfully trained on chunk reading."
        />

        <div className="phrase-training-completion">
          <div className="completion-card">
            <h2>🎉 Amazing Effort!</h2>
            
            <div className="completion-stats">
              <div className="stat-bubble">
                <span className="stat-number">{results.accuracyPercentage}%</span>
                <span className="stat-name">Accuracy</span>
              </div>
              <div className="stat-bubble">
                <span className="stat-number">{results.correctCount}/{results.totalPhrases}</span>
                <span className="stat-name">Phrases Read</span>
              </div>
            </div>

            <p className="completion-message">
              You've successfully learned to read in meaningful chunks! This skill will help you:
            </p>

            <ul className="benefits-list">
              <li>📚 Process text faster and more efficiently</li>
              <li>🎯 Improve reading comprehension</li>
              <li>💪 Read with more natural fluency</li>
              <li>⚡ Reduce cognitive load while reading</li>
            </ul>

            {results.incorrectPhrases.length > 0 && (
              <div className="encouragement">
                <p>
                  You had <strong>{results.incorrectCount}</strong> phrases to work on. Keep practicing these phrases to build confidence!
                </p>
              </div>
            )}

            {results.accuracyPercentage >= 85 && (
              <div className="praise">
                <p>⭐ Outstanding performance! Your phrase reading is excellent!</p>
              </div>
            )}

            <button className="btn-proceed-completion" onClick={handleProceedNext}>
              Continue to Reading Speed Training →
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Training in progress
  return (
    <div className="phrase-training-step">
      <StepHeader
        icon="📖"
        title="Chunk Reading (Phrase Training)"
        subtitle="Train your visual focus on phrases"
        description="Learn to read meaningful chunks of 2–4 words together. This natural grouping improves your reading comprehension and fluency. Read aloud as each phrase is highlighted, and the system will evaluate your accuracy."
      />

      <div className="phrase-training-widget-container">
        <PhraseTrainingWidget paragraph={paragraph} onComplete={handleComplete} />
      </div>

      <div className="training-tips">
        <h3 className="tips-title">📚 Why Phrase Reading?</h3>
        <p>
          Reading in phrases, rather than word-by-word, mirrors natural reading. It helps your brain process meaning faster and improves overall reading comprehension. You'll notice the text is grouped into meaningful chunks for you to follow.
        </p>
      </div>
    </div>
  );
};
