import React from 'react';
import './StepHeader.css';

export interface StepHeaderProps {
  title: string;
  subtitle?: string;
  icon?: string;
  description?: string;
}

export const StepHeader: React.FC<StepHeaderProps> = ({
  title,
  subtitle,
  icon,
  description,
}) => {
  return (
    <div className="step-header">
      {icon && <div className="step-icon">{icon}</div>}
      <div className="step-header-content">
        <h1 className="step-header-title">{title}</h1>
        {subtitle && <p className="step-header-subtitle">{subtitle}</p>}
        {description && <p className="step-header-description">{description}</p>}
      </div>
    </div>
  );
};
