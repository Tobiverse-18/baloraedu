import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  ShieldCheck,
} from 'lucide-react';

import AuthLayout from '../../layouts/AuthLayout/AuthLayout';
import authService from '../../services/authService';

import './ResetPasswordPage.css';

function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const uid = searchParams.get('uid') || '';
  const token = searchParams.get('token') || '';

  const [formData, setFormData] = useState({
    new_password: '',
    password_confirmation: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const [fieldErrors, setFieldErrors] = useState({});

  const linkIsValid = Boolean(uid && token);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setError('');

    setFieldErrors((previous) => ({
      ...previous,
      [name]: '',
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError('');
    setFieldErrors({});

    if (!linkIsValid) {
      setError(
        'This password reset link is incomplete. Please request a new one.'
      );
      return;
    }

    if (!formData.new_password || !formData.password_confirmation) {
      setError('Please complete both password fields.');
      return;
    }

    if (formData.new_password !== formData.password_confirmation) {
      setFieldErrors({
        password_confirmation: 'Passwords do not match.',
      });
      return;
    }

    try {
      setLoading(true);

      await authService.confirmPasswordReset({
        uid,
        token,
        new_password: formData.new_password,
        password_confirmation: formData.password_confirmation,
      });

      setSuccess(true);
    } catch (err) {
      const responseData = err.response?.data;

      if (responseData?.new_password) {
        setFieldErrors({
          new_password: Array.isArray(responseData.new_password)
            ? responseData.new_password.join(' ')
            : responseData.new_password,
        });
      } else if (responseData?.password_confirmation) {
        setFieldErrors({
          password_confirmation: Array.isArray(
            responseData.password_confirmation
          )
            ? responseData.password_confirmation.join(' ')
            : responseData.password_confirmation,
        });
      } else {
        setError(
          responseData?.detail ||
            'Unable to reset your password. Your link may have expired. Please request a new one.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReturnToLogin = () => {
    navigate('/login', {
      replace: true,
      state: {
        message: 'Your password has been reset successfully. You can now sign in with your new password.',
      },
    });
  };

  return (
    <AuthLayout
      title={
        success
          ? 'Password updated'
          : 'Create a new password'
      }
      subtitle={
        success
          ? 'Your BaloraEdu account password has been changed successfully.'
          : 'Choose a strong password you have not used before to keep your account secure.'
      }
    >
      {success ? (
        <div className="reset-success-container">
          <div className="reset-success-icon">
            <CheckCircle2 size={30} />
          </div>

          <h3>Your password has been changed</h3>

          <p>
            You can now sign in to BaloraEdu using your new password.
            Your previous password will no longer work.
          </p>

          <button
            type="button"
            className="reset-submit-button"
            onClick={handleReturnToLogin}
          >
            Continue to sign in
            <ArrowRight size={18} />
          </button>
        </div>
      ) : !linkIsValid ? (
        <div className="reset-invalid-container">
          <div className="reset-invalid-icon">
            <LockKeyhole size={28} />
          </div>

          <h3>Invalid reset link</h3>

          <p>
            This link is incomplete or invalid. Request a new
            password reset link to continue.
          </p>

          <Link
            to="/forgot-password"
            className="reset-submit-button"
          >
            Request a new link
            <ArrowRight size={18} />
          </Link>

          <Link to="/login" className="reset-back-link">
            <ArrowLeft size={16} />
            Back to sign in
          </Link>
        </div>
      ) : (
        <form
          className="reset-form"
          onSubmit={handleSubmit}
          noValidate
        >
          {error && (
            <div className="reset-error" role="alert">
              <span className="reset-error-indicator" />
              {error}
            </div>
          )}

          <div className="reset-field">
            <label htmlFor="reset-new-password">
              New password
            </label>

            <div className="reset-password-wrapper">
              <LockKeyhole size={17} />

              <input
                id="reset-new-password"
                type={showPassword ? 'text' : 'password'}
                name="new_password"
                placeholder="Enter your new password"
                value={formData.new_password}
                onChange={handleChange}
                autoComplete="new-password"
                required
                disabled={loading}
              />

              <button
                type="button"
                className="reset-password-toggle"
                onClick={() =>
                  setShowPassword((previous) => !previous)
                }
                aria-label={
                  showPassword ? 'Hide password' : 'Show password'
                }
                disabled={loading}
              >
                {showPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>

            {fieldErrors.new_password && (
              <span className="reset-field-error">
                {fieldErrors.new_password}
              </span>
            )}

            <span className="reset-field-hint">
              Use a strong password that is difficult to guess.
            </span>
          </div>

          <div className="reset-field">
            <label htmlFor="reset-confirm-password">
              Confirm new password
            </label>

            <div className="reset-password-wrapper">
              <LockKeyhole size={17} />

              <input
                id="reset-confirm-password"
                type={showConfirmation ? 'text' : 'password'}
                name="password_confirmation"
                placeholder="Confirm your new password"
                value={formData.password_confirmation}
                onChange={handleChange}
                autoComplete="new-password"
                required
                disabled={loading}
              />

              <button
                type="button"
                className="reset-password-toggle"
                onClick={() =>
                  setShowConfirmation((previous) => !previous)
                }
                aria-label={
                  showConfirmation
                    ? 'Hide password confirmation'
                    : 'Show password confirmation'
                }
                disabled={loading}
              >
                {showConfirmation ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>

            {fieldErrors.password_confirmation && (
              <span className="reset-field-error">
                {fieldErrors.password_confirmation}
              </span>
            )}
          </div>

          <button
            type="submit"
            className="reset-submit-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <LoaderCircle
                  size={19}
                  className="reset-spinner"
                />
                Updating password...
              </>
            ) : (
              <>
                Reset my password
                <ArrowRight size={18} />
              </>
            )}
          </button>

          <div className="reset-security-note">
            <ShieldCheck size={16} />
            <span>
              Your password is securely encrypted.
            </span>
          </div>

          <div className="reset-login-prompt">
            Remember your password?
            <Link to="/login">Sign in</Link>
          </div>
        </form>
      )}
    </AuthLayout>
  );
}

export default ResetPasswordPage;