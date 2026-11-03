import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Eye,
  EyeOff,
  LoaderCircle,
} from 'lucide-react';

import AuthLayout from '../../layouts/AuthLayout/AuthLayout';
import authService from '../../services/authService';

import './RegisterPage.css';

function RegisterPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    password: '',
    password_confirmation: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setErrors((previous) => ({
      ...previous,
      [name]: '',
      general: '',
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required.';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required.';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email address is required.';
    } else if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())
    ) {
      newErrors.email = 'Enter a valid email address.';
    }

    if (!formData.phone_number.trim()) {
      newErrors.phone_number = 'Phone number is required.';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required.';
    }

    if (!formData.password_confirmation) {
      newErrors.password_confirmation = 'Please confirm your password.';
    } else if (formData.password !== formData.password_confirmation) {
      newErrors.password_confirmation = 'Passwords do not match.';
    }

    if (!acceptedTerms) {
      newErrors.terms = 'Please accept the terms to continue.';
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) return;

    try {
      setLoading(true);

      await authService.register({
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim().toLowerCase(),
        phone_number: formData.phone_number.trim(),
        password: formData.password,
        password_confirmation: formData.password_confirmation,
      });

      navigate('/login', {
        replace: true,
        state: {
          message: 'Your account has been created successfully. You can now sign in.',
        },
      });
    } catch (error) {
      const responseData = error.response?.data;

      if (responseData && typeof responseData === 'object') {
        const backendErrors = {};

        Object.entries(responseData).forEach(([field, messages]) => {
          backendErrors[field] = Array.isArray(messages)
            ? messages.join(' ')
            : String(messages);
        });

        setErrors({
          ...backendErrors,
          general: backendErrors.detail || backendErrors.non_field_errors || '',
        });
      } else {
        setErrors({
          general: 'Unable to create your account. Please try again.',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Join BaloraEdu and get started with a smarter school management experience."
    >
      <form className="register-form" onSubmit={handleSubmit} noValidate>
        {errors.general && (
          <div className="register-error" role="alert">
            {errors.general}
          </div>
        )}

        <div className="register-name-grid">
          <div className="register-field">
            <label htmlFor="register-first-name">First name</label>
            <input
              id="register-first-name"
              type="text"
              name="first_name"
              placeholder="First name"
              value={formData.first_name}
              onChange={handleChange}
              autoComplete="given-name"
              disabled={loading}
              required
            />
            {errors.first_name && (
              <span className="register-field-error">{errors.first_name}</span>
            )}
          </div>

          <div className="register-field">
            <label htmlFor="register-last-name">Last name</label>
            <input
              id="register-last-name"
              type="text"
              name="last_name"
              placeholder="Last name"
              value={formData.last_name}
              onChange={handleChange}
              autoComplete="family-name"
              disabled={loading}
              required
            />
            {errors.last_name && (
              <span className="register-field-error">{errors.last_name}</span>
            )}
          </div>
        </div>

        <div className="register-field">
          <label htmlFor="register-email">Email address</label>
          <input
            id="register-email"
            type="email"
            name="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            autoComplete="email"
            disabled={loading}
            required
          />
          {errors.email && (
            <span className="register-field-error">{errors.email}</span>
          )}
        </div>

        <div className="register-field">
          <label htmlFor="register-phone">Phone number</label>
          <input
            id="register-phone"
            type="tel"
            name="phone_number"
            placeholder="e.g. 08012345678"
            value={formData.phone_number}
            onChange={handleChange}
            autoComplete="tel"
            disabled={loading}
            required
          />
          {errors.phone_number && (
            <span className="register-field-error">{errors.phone_number}</span>
          )}
        </div>

        <div className="register-field">
          <label htmlFor="register-password">Password</label>

          <div className="register-password-wrapper">
            <input
              id="register-password"
              type={showPassword ? 'text' : 'password'}
              name="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="new-password"
              disabled={loading}
              required
            />

            <button
              type="button"
              className="register-password-toggle"
              onClick={() => setShowPassword((previous) => !previous)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              disabled={loading}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {errors.password && (
            <span className="register-field-error">{errors.password}</span>
          )}
        </div>

        <div className="register-field">
          <label htmlFor="register-confirm-password">Confirm password</label>

          <div className="register-password-wrapper">
            <input
              id="register-confirm-password"
              type={showConfirmation ? 'text' : 'password'}
              name="password_confirmation"
              placeholder="Enter your password again"
              value={formData.password_confirmation}
              onChange={handleChange}
              autoComplete="new-password"
              disabled={loading}
              required
            />

            <button
              type="button"
              className="register-password-toggle"
              onClick={() => setShowConfirmation((previous) => !previous)}
              aria-label={showConfirmation ? 'Hide password' : 'Show password'}
              disabled={loading}
            >
              {showConfirmation ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {errors.password_confirmation && (
            <span className="register-field-error">
              {errors.password_confirmation}
            </span>
          )}
        </div>

        <div className="register-terms">
          <label>
            <input
              type="checkbox"
              checked={acceptedTerms}
              onChange={(event) => {
                setAcceptedTerms(event.target.checked);
                setErrors((previous) => ({
                  ...previous,
                  terms: '',
                }));
              }}
              disabled={loading}
            />

            <span>
              I agree to the BaloraEdu terms and conditions and privacy policy.
            </span>
          </label>

          {errors.terms && (
            <span className="register-field-error">{errors.terms}</span>
          )}
        </div>

        <button
          type="submit"
          className="register-submit-button"
          disabled={loading}
        >
          {loading ? (
            <>
              <LoaderCircle size={19} className="register-spinner" />
              Creating your account...
            </>
          ) : (
            <>
              Create account
              <ArrowRight size={18} />
            </>
          )}
        </button>

        <div className="register-login-prompt">
          Already have an account?
          <Link to="/login">Sign in</Link>
        </div>
      </form>
    </AuthLayout>
  );
}

export default RegisterPage;