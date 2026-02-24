import React, { useState } from 'react';
import './AgeInput.css';

interface AgeInputProps {
  onAgeSubmit: (age: number) => void;
}

export const AgeInput: React.FC<AgeInputProps> = ({ onAgeSubmit }) => {
  const [age, setAge] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const ageNum = parseInt(age, 10);

    if (!age.trim()) {
      setError('Please enter your age');
      return;
    }

    if (isNaN(ageNum) || ageNum < 5 || ageNum > 100) {
      setError('Please enter a valid age between 5 and 100');
      return;
    }

    onAgeSubmit(ageNum);
  };

  return (
    <div className="age-input-container">
      <div className="age-input-card">
        <h1>🧠 Dyslexia Assessment</h1>
        <p className="subtitle">Personalized Reading Assessment Tool</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="age">How old are you?</label>
            <input
              id="age"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter your age"
              min="5"
              max="100"
              autoFocus
            />
            {error && <p className="error">{error}</p>}
          </div>

          <button type="submit" className="btn-submit">
            Start Assessment →
          </button>
        </form>

        <div className="info">
          <p>We'll customize a reading passage based on your age and assess your reading ability.</p>
        </div>
      </div>
    </div>
  );
};
