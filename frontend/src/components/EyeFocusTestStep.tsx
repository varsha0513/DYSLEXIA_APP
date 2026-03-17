import React, { useState } from 'react';
import { useCourse } from '../contexts/CourseContext';
import { StepHeader } from './StepHeader';
import { EyeFocusWordTracking, EyeFocusResults } from './EyeFocusWordTracking';
import './EyeFocusTestStep.css';

export interface EyeFocusTestStepProps {
  paragraph: string;
}

export const EyeFocusTestStep: React.FC<EyeFocusTestStepProps> = ({ paragraph }) => {
  const { markStepComplete, goNextStep } = useCourse();
  const [currentIteration, setCurrentIteration] = useState<1 | 2>(1);
  const [isComplete, setIsComplete] = useState(false);
  const [showIterationInfo, setShowIterationInfo] = useState(false);
  const [results, setResults] = useState<{ iteration1: EyeFocusResults | null; iteration2: EyeFocusResults | null }>({
    iteration1: null,
    iteration2: null,
  });

  React.useEffect(() => {
    console.log('EyeFocusTestStep - paragraph received:', paragraph);
  }, [paragraph]);

  const handleIterationComplete = (iterationResults: EyeFocusResults) => {
    console.log(`Eye Focus iteration ${currentIteration} completed:`, iterationResults);

    if (currentIteration === 1) {
      // Save iteration 1 results and show info box for iteration 2
      setResults(prev => ({ ...prev, iteration1: iterationResults }));
      setShowIterationInfo(true);
    } else {
      // Save iteration 2 results and complete the exercise
      setResults(prev => ({ ...prev, iteration2: iterationResults }));
      markStepComplete('eye-focus-test');
      setIsComplete(true);
    }
  };

  const handleProceedToIteration2 = () => {
    setShowIterationInfo(false);
    setCurrentIteration(2);
  };

  const handleProceedNext = () => {
    goNextStep();
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

  // Show info box between iterations
  if (showIterationInfo && results.iteration1) {
    return (
      <div className="eye-focus-test-step">
        <StepHeader
          icon="👁️"
          title="Great Work on Iteration 1!"
          subtitle="Time for the next challenge"
          description="You've completed the slower pace (1 sec/word). Now let's try a faster pace!"
        />

        <div className="eye-focus-iteration-info">
          <div className="info-box">
            <h2>✨ Iteration 1 Complete!</h2>
            
            <div className="iteration-results-preview">
              <h3>Your Performance:</h3>
              <div className="results-preview">
                <div className="result-item">
                  <span className="result-label">Accuracy:</span>
                  <span className="result-value">{results.iteration1.accuracyPercentage}%</span>
                </div>
                <div className="result-item">
                  <span className="result-label">Words Correct:</span>
                  <span className="result-value">{results.iteration1.correctCount}/{results.iteration1.totalWords}</span>
                </div>
              </div>
            </div>

            <div className="next-iteration-preview">
              <h3>📊 Iteration 2: Faster Pace (0.8 sec/word)</h3>
              <p>Now let's increase the difficulty! You'll follow words at a slightly faster pace. Stay focused and do your best!</p>
              <ul>
                <li>✓ Track each word as it highlights</li>
                <li>✓ Read aloud at your natural pace</li>
                <li>✓ Stay focused on the highlighted words</li>
              </ul>
            </div>

            <button className="btn-start-iteration2" onClick={handleProceedToIteration2}>
              Ready? Start Iteration 2 →
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show completion message after both iterations
  if (isComplete) {
    return (
      <div className="eye-focus-test-step">
        <StepHeader
          icon="👁️"
          title="Eye Focus Training Complete"
          subtitle="Great job!"
          description="You've completed both iterations of the eye focus training."
        />

        <div className="eye-focus-completion">
          <div className="completion-message">
            <h2>🎉 Outstanding Work!</h2>
            <p>You've successfully completed both iterations of the eye focus training!</p>
            
            <div className="iterations-summary">
              <div className="iteration-summary-card">
                <h3>1️⃣ Iteration 1: Slower Pace</h3>
                <p className="card-subtitle">(1 second per word)</p>
                {results.iteration1 && (
                  <div className="summary-details">
                    <p><strong>Accuracy:</strong> {results.iteration1.accuracyPercentage}%</p>
                    <p><strong>Words Correct:</strong> {results.iteration1.correctCount}/{results.iteration1.totalWords}</p>
                  </div>
                )}
              </div>

              <div className="iteration-summary-card">
                <h3>2️⃣ Iteration 2: Faster Pace</h3>
                <p className="card-subtitle">(0.8 seconds per word)</p>
                {results.iteration2 && (
                  <div className="summary-details">
                    <p><strong>Accuracy:</strong> {results.iteration2.accuracyPercentage}%</p>
                    <p><strong>Words Correct:</strong> {results.iteration2.correctCount}/{results.iteration2.totalWords}</p>
                  </div>
                )}
              </div>
            </div>

            <p className="completion-encouragement">
              Excellent effort! You've successfully trained your eyes to focus and track words at different speeds. This improved focus will help you read faster and more accurately. 📚
            </p>

            <button className="btn-proceed-training" onClick={handleProceedNext}>
              Continue to Next Training →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="eye-focus-test-step">
      <StepHeader
        icon="👁️"
        title={`Eye Focus Word Tracking - Iteration ${currentIteration}`}
        subtitle="Train your visual focus on each word"
        description={currentIteration === 1 
          ? "Follow highlighted words at a slower pace (1 second per word). Read aloud and focus on tracking each word." 
          : "Follow highlighted words at a faster pace (0.8 seconds per word). Your speed and accuracy matter!"}
      />

      <div className="eye-focus-iterations">
        <div className="iteration-indicator">
          <span className={`iteration-badge active`}>
            Iteration {currentIteration}/2
          </span>
          <span className="iteration-label">
            {currentIteration === 1 ? '1 sec per word (Slower Pace)' : '0.8 sec per word (Faster Pace)'}
          </span>
        </div>

        <EyeFocusWordTracking 
          paragraph={paragraph} 
          onComplete={handleIterationComplete}
          timePerWordMs={currentIteration === 1 ? 1000 : 800}
        />
      </div>
    </div>
  );
};
