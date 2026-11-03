import { useEffect, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';

import logo from '../../assets/balora_logo.png';
import './Navbar.css';

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : '';

    return () => {
      document.body.style.overflow = '';
    };
  }, [menuOpen]);

  const closeMenu = () => setMenuOpen(false);

  const navigationLinks = [
    { label: 'Home', href: '#home' },
    { label: 'Features', href: '#features' },
    { label: 'How it works', href: '#how-it-works' },
    { label: 'About us', href: '#about' },
  ];

  return (
    <header className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
      <div className="navbar-container">
        <Link
          to="/"
          className="navbar-brand"
          aria-label="Balora Edu home"
          onClick={closeMenu}
        >
          <img src={logo} alt="Balora Edu" />
        </Link>

        <nav
          className={`navbar-navigation ${menuOpen ? 'navigation-open' : ''}`}
          aria-label="Main navigation"
        >
          <div className="mobile-menu-heading">
            <span>Explore Balora Edu</span>
            <span>Everything your school needs.</span>
          </div>

          <div className="navbar-links">
            {navigationLinks.map((link, index) => (
              <a
                key={link.label}
                href={`/${link.href}`}
                className="navbar-link"
                style={{ '--link-index': index }}
                onClick={closeMenu}
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="mobile-menu-actions">
            <Link
              to="/login"
              className="navbar-login mobile-login"
              onClick={closeMenu}
            >
              Log in
            </Link>

            <Link
              to="/register"
              className="navbar-cta mobile-cta"
              onClick={closeMenu}
            >
              Get started <ArrowUpRight size={17} />
            </Link>
          </div>
        </nav>

        <div className="navbar-actions">
          <Link to="/login" className="navbar-login">
            Log in
          </Link>

          <Link to="/register" className="navbar-cta">
            Get started <ArrowUpRight size={17} />
          </Link>
        </div>

        <button
          type="button"
          className={`navbar-menu-toggle ${menuOpen ? 'menu-active' : ''}`}
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={menuOpen}
          aria-controls="mobile-navigation"
          onClick={() => setMenuOpen((previous) => !previous)}
        >
          <span className="hamburger-line line-one" />
          <span className="hamburger-line line-two" />
          <span className="hamburger-line line-three" />
        </button>
      </div>

      <div
        id="mobile-navigation"
        className={`navbar-mobile-backdrop ${menuOpen ? 'backdrop-visible' : ''}`}
        onClick={closeMenu}
        aria-hidden="true"
      />
    </header>
  );
}

export default Navbar;