import React from 'react';
import { useCourse } from '../contexts/CourseContext';
import { ProgressTracker } from './ProgressTracker';
import { CourseNavigation, CourseNavigationProps } from './CourseNavigation';
import './CourseLayout.css';

export interface CourseLayoutProps {
  children: React.ReactNode;
  navigationProps?: CourseNavigationProps;
  showNavigation?: boolean;
  onEndSession?: () => void;
}

export const CourseLayout: React.FC<CourseLayoutProps> = ({
  children,
  navigationProps,
  showNavigation = true,
  onEndSession,
}) => {
  const { stepCompletion, currentStep } = useCourse();
  
  // Show end session button only when user is on the 5th step (phrase-training) AND it's complete
  const showEndSessionButton = currentStep === 'phrase-training' && stepCompletion['phrase-training'];

  return (
    <div className="course-layout">
      <aside className="course-sidebar">
        <ProgressTracker />
      </aside>

      <main className="course-main-content">
        <div className="course-content-wrapper">
          {children}
        </div>

        {showEndSessionButton && onEndSession ? (
          <div className="course-completion">
            <button 
              className="end-session-button"
              onClick={onEndSession}
            >
              ✅ End Session & Return to Dashboard
            </button>
          </div>
        ) : (
          showNavigation && <CourseNavigation {...navigationProps} />
        )}
      </main>
    </div>
  );
};
