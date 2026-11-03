import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  LoaderCircle,
  Mail,
  ShieldCheck,
} from 'lucide-react';

import AuthLayout from '../../layouts/AuthLayout/AuthLayout';
import authService from '../../services/authService';

import './ForgotPasswordPage.css';

function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    const normalizedEmail = email.trim().toLowerCase();

    if (!normalizedEmail) {
      setError('Please enter your email address.');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      setError('Please enter a valid email address.');
      return;
    }

    try {
      setLoading(true);

      await authService.requestPasswordReset(normalizedEmail);

      setSubmitted(true);
    } catch (err) {
      const message =
        err.response?.data?.email?.[0] ||
        err.response?.data?.detail ||
        'Unable to process your request. Please try again.';

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title={submitted ? 'Check your inbox' : 'Forgot your password?'}
      subtitle={
        submitted
          ? 'If an account exists with that email address, a password reset link will be sent shortly.'
          : 'No worries. Enter the email address associated with your account and we will send you instructions to reset your password.'
      }
    >
      {submitted ? (
        <div className="forgot-success-container">
          <div className="forgot-success-icon">
            <CheckCircle2 size={30} />
          </div>

          <h3>Reset instructions requested</h3>

          <p>
            If <strong>{email.trim().toLowerCase()}</strong> is
            registered with BaloraEdu, you will receive an email
            containing a secure password reset link.
          </p>

          <p className="forgot-expiry-note">
            The link expires after one hour. Please check your
            inbox and spam folder.
          </p>

          <button
            type="button"
            className="forgot-submit-button"
            onClick={() => {
              setSubmitted(false);
              setError('');
            }}
          >
            Try another email
            <ArrowRight size={18} />
          </button>

          <Link to="/login" className="forgot-back-link">
            <ArrowLeft size={16} />
            Back to sign in
          </Link>
        </div>
      ) : (
        <form
          className="forgot-form"
          onSubmit={handleSubmit}
          noValidate
        >
          {error && (
            <div className="forgot-error" role="alert">
              <span className="forgot-error-indicator" />
              {error}
            </div>
          )}

          <div className="forgot-field">
            <label htmlFor="forgot-email">
              Email address
            </label>

            <div className="forgot-input-wrapper">
              <Mail size={18} />

              <input
                id="forgot-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  setError('');
                }}
                autoComplete="email"
                required
                disabled={loading}
              />
            </div>
          </div>

          <button
            type="submit"
            className="forgot-submit-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <LoaderCircle
                  size={19}
                  className="forgot-spinner"
                />
                Sending instructions...
              </>
            ) : (
              <>
                Send reset instructions
                <ArrowRight size={18} />
              </>
            )}
          </button>

          <div className="forgot-security-note">
            <ShieldCheck size={16} />
            <span>
              Your account security is important to us.
            </span>
          </div>

          <div className="forgot-login-prompt">
            Remember your password?
            <Link to="/login">Sign in</Link>
          </div>
        </form>
      )}
    </AuthLayout>
  );
}

export default ForgotPasswordPage;