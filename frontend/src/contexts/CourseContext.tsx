import React, { createContext, useContext, useState, useCallback } from 'react';

export type CourseStep = 
  | 'age-selection'
  | 'reading-assessment'
  | 'result-analysis'
  | 'pronunciation-training'
  | 'eye-focus-test'
  | 'reading-speed-training';

export type StepCompletion = Record<CourseStep, boolean>;

export interface CourseContextType {
  currentStep: CourseStep;
  stepCompletion: StepCompletion;
  completionPercentage: number;
  setCurrentStep: (step: CourseStep) => void;
  markStepComplete: (step: CourseStep) => void;
  canAdvance: () => boolean;
  goNextStep: () => boolean;
  goPreviousStep: () => boolean;
  resetCourse: () => void;
  getStepNumber: (step: CourseStep) => number;
  getStepTitle: (step: CourseStep) => string;
}

const COURSE_STEPS: CourseStep[] = [
  'age-selection',
  'reading-assessment',
  'result-analysis',
  'pronunciation-training',
  'eye-focus-test',
  'reading-speed-training',
];

const STEP_TITLES: Record<CourseStep, string> = {
  'age-selection': 'Age Selection / Login',
  'reading-assessment': 'Reading Assessment',
  'result-analysis': 'Result Analysis',
  'pronunciation-training': 'Pronunciation Training',
  'eye-focus-test': 'Eye Focus & Guided Reading',
  'reading-speed-training': 'Speed Improvement',
};

const CourseContext = createContext<CourseContextType | undefined>(undefined);

export const CourseProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentStep, setCurrentStepState] = useState<CourseStep>('age-selection');
  const [stepCompletion, setStepCompletion] = useState<StepCompletion>({
    'age-selection': false,
    'reading-assessment': false,
    'result-analysis': false,
    'pronunciation-training': false,
    'eye-focus-test': false,
    'reading-speed-training': false,
  });

  // Load from localStorage on mount
  React.useEffect(() => {
    const savedStep = localStorage.getItem('courseCurrentStep') as CourseStep;
    const savedCompletion = localStorage.getItem('courseStepCompletion');
    
    if (savedStep && COURSE_STEPS.includes(savedStep)) {
      setCurrentStepState(savedStep);
    }
    
    if (savedCompletion) {
      try {
        setStepCompletion(JSON.parse(savedCompletion));
      } catch (e) {
        console.warn('Failed to load course progress:', e);
      }
    }
  }, []);

  const setCurrentStep = useCallback((step: CourseStep) => {
    setCurrentStepState(step);
    localStorage.setItem('courseCurrentStep', step);
  }, []);

  const markStepComplete = useCallback((step: CourseStep) => {
    setStepCompletion(prev => {
      const updated = { ...prev, [step]: true };
      localStorage.setItem('courseStepCompletion', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const canAdvance = useCallback(() => {
    return stepCompletion[currentStep];
  }, [currentStep, stepCompletion]);

  const goNextStep = useCallback(() => {
    const currentIndex = COURSE_STEPS.indexOf(currentStep);
    if (currentIndex < COURSE_STEPS.length - 1 && canAdvance()) {
      const nextStep = COURSE_STEPS[currentIndex + 1];
      setCurrentStep(nextStep);
      return true;
    }
    return false;
  }, [currentStep, canAdvance, setCurrentStep]);

  const goPreviousStep = useCallback(() => {
    const currentIndex = COURSE_STEPS.indexOf(currentStep);
    if (currentIndex > 0) {
      const prevStep = COURSE_STEPS[currentIndex - 1];
      setCurrentStep(prevStep);
      return true;
    }
    return false;
  }, [currentStep, setCurrentStep]);

  const resetCourse = useCallback(() => {
    setCurrentStep('age-selection');
    setStepCompletion({
      'age-selection': false,
      'reading-assessment': false,
      'result-analysis': false,
      'pronunciation-training': false,
      'reading-speed-training': false,
      'eye-focus-test': false,
    });
  }, []);

  const getStepNumber = useCallback((step: CourseStep) => {
    return COURSE_STEPS.indexOf(step) + 1;
  }, []);

  const getStepTitle = useCallback((step: CourseStep) => {
    return STEP_TITLES[step];
  }, []);

  const completedCount = Object.values(stepCompletion).filter(Boolean).length;
  const completionPercentage = (completedCount / COURSE_STEPS.length) * 100;

  const value: CourseContextType = {
    currentStep,
    stepCompletion,
    completionPercentage,
    setCurrentStep,
    markStepComplete,
    canAdvance,
    goNextStep,
    goPreviousStep,
    resetCourse,
    getStepNumber,
    getStepTitle,
  };

  return (
    <CourseContext.Provider value={value}>
      {children}
    </CourseContext.Provider>
  );
};

export const useCourse = () => {
  const context = useContext(CourseContext);
  if (!context) {
    throw new Error('useCourse must be used within a CourseProvider');
  }
  return context;
};
