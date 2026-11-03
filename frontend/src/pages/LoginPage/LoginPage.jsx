import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Eye,
  EyeOff,
  ArrowRight,
  LoaderCircle,
  LockKeyhole,
  CheckCircle2,
} from 'lucide-react';

import AuthLayout from '../../layouts/AuthLayout/AuthLayout';
import { useAuth } from '../../hooks/useAuth';

import './LoginPage.css';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const successMessage = location.state?.message || '';

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    if (error) {
      setError('');
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    const email = formData.email.trim().toLowerCase();
    const password = formData.password;

    if (!email || !password) {
      setError('Please enter your email address and password.');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    try {
      setLoading(true);

      await login({
        email,
        password,
      });

      const destination = location.state?.from?.pathname || '/schools';

      navigate(destination, { replace: true });
    } catch (err) {
      const responseData = err.response?.data;

      const message =
        responseData?.detail ||
        responseData?.non_field_errors?.[0] ||
        responseData?.email?.[0] ||
        responseData?.password?.[0] ||
        'Unable to sign in. Please check your details and try again.';

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to access your BaloraEdu account and school workspace."
    >
      <form className="login-form" onSubmit={handleSubmit} noValidate>
        {successMessage && (
          <div className="login-success" role="status">
            <CheckCircle2 size={18} />
            <span>{successMessage}</span>
          </div>
        )}

        {error && (
          <div className="login-error" role="alert">
            <span className="login-error-indicator" />
            {error}
          </div>
        )}

        <div className="login-field">
          <label htmlFor="login-email">Email address</label>

          <input
            id="login-email"
            type="email"
            name="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            autoComplete="email"
            required
            disabled={loading}
          />
        </div>

        <div className="login-field">
          <div className="login-label-row">
            <label htmlFor="login-password">Password</label>

            <Link to="/forgot-password" className="login-forgot-link">
              Forgot password?
            </Link>
          </div>

          <div className="login-password-wrapper">
            <input
              id="login-password"
              type={showPassword ? 'text' : 'password'}
              name="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="current-password"
              required
              disabled={loading}
            />

            <button
              type="button"
              className="login-password-toggle"
              onClick={() => setShowPassword((previous) => !previous)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              disabled={loading}
            >
              {showPassword ? (
                <EyeOff size={18} />
              ) : (
                <Eye size={18} />
              )}
            </button>
          </div>
        </div>

        <button
          type="submit"
          className="login-submit-button"
          disabled={loading}
        >
          {loading ? (
            <>
              <LoaderCircle size={19} className="login-spinner" />
              Signing you in...
            </>
          ) : (
            <>
              Sign in to your account
              <ArrowRight size={18} />
            </>
          )}
        </button>

        <div className="login-security-note">
          <LockKeyhole size={15} />
          <span>Your account is protected with secure authentication.</span>
        </div>

        <div className="login-register-prompt">
          Don't have an account?
          <Link to="/register">Create an account</Link>
        </div>
      </form>
    </AuthLayout>
  );
}

export default LoginPage;