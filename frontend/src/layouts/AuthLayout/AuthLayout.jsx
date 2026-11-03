import { ArrowUpRight, BookOpen, GraduationCap, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

import logo from '../../assets/balora_logo.png';
import './AuthLayout.css';

function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="auth-layout">
      <aside className="auth-brand-panel">
        <Link to="/" className="auth-brand-logo">
          <img src={logo} alt="BaloraEdu" />
        </Link>

        <div className="auth-brand-content">
          <span className="auth-brand-eyebrow">
            THE FUTURE OF SCHOOL MANAGEMENT
          </span>

          <h1>
            Everything your school needs.
            <span> All in one place.</span>
          </h1>

          <p>
            Simplify school administration, connect your school
            community and create a better experience for everyone.
          </p>

          <div className="auth-brand-features">
            <div>
              <span className="auth-feature-icon">
                <GraduationCap size={19} />
              </span>
              <span>Smarter academic management</span>
            </div>

            <div>
              <span className="auth-feature-icon">
                <BookOpen size={19} />
              </span>
              <span>Organised school operations</span>
            </div>

            <div>
              <span className="auth-feature-icon">
                <ShieldCheck size={19} />
              </span>
              <span>Secure and connected workspace</span>
            </div>
          </div>
        </div>

        <div className="auth-brand-footer">
          <span>© {new Date().getFullYear()} BaloraEdu</span>
          <span>Built for better education management.</span>
        </div>

        <div className="auth-brand-decoration decoration-one" />
        <div className="auth-brand-decoration decoration-two" />
      </aside>

      <main className="auth-form-panel">
        <div className="auth-mobile-header">
          <Link to="/" className="auth-mobile-logo">
            <img src={logo} alt="BaloraEdu" />
          </Link>

          <Link to="/" className="auth-home-link">
            Back to website <ArrowUpRight size={15} />
          </Link>
        </div>

        <div className="auth-form-container">
          <div className="auth-form-heading">
            
            <h2>{title}</h2>
            <p>{subtitle}</p>
          </div>

          {children}
        </div>

        <div className="auth-form-footer">
          <span>Secure access to your school workspace.</span>
        </div>
      </main>
    </div>
  );
}

export default AuthLayout;