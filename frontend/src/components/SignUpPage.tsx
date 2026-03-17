import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './AuthPages.css';

interface SignUpPageProps {
  onNavigate?: (page: 'login' | 'dashboard') => void;
}

const SignUpPage: React.FC<SignUpPageProps> = ({ onNavigate }) => {
  const { signup, error, isLoading, clearError } = useAuth();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: '',
    password: '',
    passwordConfirm: '',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const validateForm = () => {
    const errors: Record<string, string> = {};

    // Validate name
    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      errors.email = 'Invalid email format';
    }

    // Validate age
    const ageNum = parseInt(formData.age);
    if (!formData.age) {
      errors.age = 'Age is required';
    } else if (isNaN(ageNum) || ageNum < 5 || ageNum > 100) {
      errors.age = 'Age must be between 5 and 100';
    }

    // Validate password
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = 'Password must contain at least one uppercase letter';
    } else if (!/[0-9]/.test(formData.password)) {
      errors.password = 'Password must contain at least one number';
    }

    // Validate password confirmation
    if (formData.passwordConfirm !== formData.password) {
      errors.passwordConfirm = 'Passwords do not match';
    }

    return errors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // Clear validation error for this field when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const updated = { ...prev };
        delete updated[name];
        return updated;
      });
    }

    // Clear API error
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);

    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    try {
      clearError();
      await signup(formData.name, formData.email, parseInt(formData.age), formData.password, formData.passwordConfirm);
      // Redirect to dashboard on successful signup
      onNavigate?.('dashboard');
    } catch {
      // Error is handled and displayed via the error state
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Create Account 🎓</h1>
          <p>Join us on your dyslexia training journey</p>
        </div>

        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Name Field */}
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter your full name"
              disabled={isLoading}
            />
            {validationErrors.name && (
              <span className="field-error">{validationErrors.name}</span>
            )}
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              disabled={isLoading}
            />
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
            )}
          </div>

          {/* Age Field */}
          <div className="form-group">
            <label htmlFor="age">Age</label>
            <input
              id="age"
              name="age"
              type="number"
              value={formData.age}
              onChange={handleChange}
              placeholder="Enter your age"
              min="5"
              max="100"
              disabled={isLoading}
            />
            {validationErrors.age && (
              <span className="field-error">{validationErrors.age}</span>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              disabled={isLoading}
            />
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
            <p className="password-requirements">
              Password must contain: at least 6 characters, one uppercase letter, one number
            </p>
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="passwordConfirm">Confirm Password</label>
            <input
              id="passwordConfirm"
              name="passwordConfirm"
              type="password"
              value={formData.passwordConfirm}
              onChange={handleChange}
              placeholder="Confirm your password"
              disabled={isLoading}
            />
            {validationErrors.passwordConfirm && (
              <span className="field-error">{validationErrors.passwordConfirm}</span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? '⏳ Creating Account...' : '✓ Create Account'}
          </button>
        </form>

        {/* Login Link */}
        <p className="auth-footer">
          Already have an account?{' '}
          <button
            onClick={() => onNavigate?.('login')}
            className="auth-link"
            style={{
              background: 'none',
              border: 'none',
              color: 'inherit',
              textDecoration: 'underline',
              cursor: 'pointer',
              padding: 0,
              font: 'inherit'
            }}
          >
            Sign in here
          </button>
        </p>
      </div>
    </div>
  );
};

export default SignUpPage;
