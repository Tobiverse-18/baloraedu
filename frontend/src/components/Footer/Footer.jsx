import { ArrowUpRight, Mail, MapPin, Phone } from 'lucide-react';
import { Link } from 'react-router-dom';

import logo from '../../assets/balora_logo.png';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">

        <div className="footer-main">

          <div className="footer-brand-section">
            <Link to="/" className="footer-logo">
              <img src={logo} alt="Balora Edu" />
            </Link>

            <p className="footer-description">
              Bringing schools, teachers, parents and students together
              through a smarter, simpler approach to school management.
            </p>

            <div className="footer-socials">
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noreferrer"
                aria-label="Facebook"
              >
                Facebook
              </a>

              <a
                href="https://instagram.com"
                target="_blank"
                rel="noreferrer"
                aria-label="Instagram"
              >
                Instagram
              </a>

              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noreferrer"
                aria-label="LinkedIn"
              >
                LinkedIn
              </a>
            </div>
          </div>

          <div className="footer-column">
            <h3>Platform</h3>
            <a href="/#features">Features</a>
            <a href="/#how-it-works">How it works</a>
            <a href="/#about">About Balora Edu</a>
          </div>

          <div className="footer-column">
            <h3>Get started</h3>
            <Link to="/register">Create an account</Link>
            <Link to="/login">Sign in</Link>
            <Link to="/schools/register">Register your school</Link>
          </div>

          <div className="footer-column footer-contact">
            <h3>Get in touch</h3>

            <a href="mailto:verifybagteam@gmail.com">
              <Mail size={16} />
              <span>verifybagteam@gmail.com</span>
            </a>

            <a href="tel:+2349039008012">
              <Phone size={16} />
              <span>Contact Balora</span>
            </a>

            <div className="footer-location">
              <MapPin size={16} />
              <span>Built for schools everywhere.</span>
            </div>
          </div>

          <div className="footer-column">
            <h3>Legal</h3>
            <Link to="/terms">Terms and Conditions</Link>
            <Link to="/privacy">Privacy Policy</Link>
            <Link to="/refund-policy">Refund Policy</Link>
          </div>

        </div>

        <div className="footer-divider" />

        <div className="footer-bottom">
          <p>
            © {currentYear} Balora Edu. All rights reserved.
          </p>

          <p className="footer-credit">
            Designed &amp; Developed by <span>Balora</span>
          </p>

          <a href="/#home" className="footer-back-top">
            Back to top <ArrowUpRight size={15} />
          </a>
        </div>

      </div>
    </footer>
  );
}

export default Footer;