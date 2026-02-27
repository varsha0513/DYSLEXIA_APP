export interface SpeedMetrics {
  elapsed_time_seconds: number;
  elapsed_time_formatted: string;
  spoken_words: number;
  wpm: number;
  speed_category: string;
  speed_indicator: string;
  dyslexia_risk: string;
}

export interface AccuracyMetrics {
  total_words: number;
  correct_words: number;
  wrong_words: number;
  missing_words: number;
  extra_words: number;
  accuracy_percent: number;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: string;
  component_scores: Record<string, number>;
  indicators: string[];
  recommendations: string[];
  summary: string;
}

export interface AssistanceData {
  has_errors: boolean;
  error_count: number;
  wrong_words: Array<[string, string]>; // [spoken, correct]
  missing_words: string[];
  extra_words: string[];
  assistance_enabled: boolean;
}

export interface AssessmentResponse {
  reference_text: string;
  recognized_text: string;
  age: number;
  speed_metrics: SpeedMetrics;
  accuracy_metrics: AccuracyMetrics;
  accuracy_feedback: string;
  difficulty_assessment: string;
  risk_assessment: RiskAssessment;
  assistance?: AssistanceData;
  status: string;
}

export interface Paragraph {
  age: number;
  text: string;
  difficulty: string;
}

export type AppState = 'age-input' | 'reading' | 'results' | 'loading' | 'error';
