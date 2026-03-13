import React, { ReactNode } from 'react';
import { ProgressTracker } from './ProgressTracker';
import { CourseNavigation, CourseNavigationProps } from './CourseNavigation';
import './CourseLayout.css';

export interface CourseLayoutProps {
  children: ReactNode;
  navigationProps?: CourseNavigationProps;
  showNavigation?: boolean;
}

export const CourseLayout: React.FC<CourseLayoutProps> = ({
  children,
  navigationProps,
  showNavigation = true,
}) => {
  return (
    <div className="course-layout">
      <aside className="course-sidebar">
        <ProgressTracker />
      </aside>

      <main className="course-main-content">
        <div className="course-content-wrapper">
          {children}
        </div>

        {showNavigation && <CourseNavigation {...navigationProps} />}
      </main>
    </div>
  );
};
