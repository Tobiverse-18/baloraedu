
import { useCallback, useEffect, useState } from 'react';
import {
  Activity,
  ArrowLeft,
  Bell,
  BookOpen,
  Building2,
  CalendarDays,
  ChevronDown,
  CircleAlert,
  CreditCard,
  GraduationCap,
  LayoutDashboard,
  LoaderCircle,
  LogOut,
  Menu,
  Settings,
  ShieldCheck,
  Users,
  Wallet,
  X,
} from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';
import schoolService from '../../services/schoolService';

import logo from '../../assets/balora_logo.png';

import './SchoolWorkspacePage.css';

const navigationItems = [
  {
    label: 'Overview',
    icon: LayoutDashboard,
    path: '',
    description: 'School dashboard',
  },
  {
    label: 'Students',
    icon: GraduationCap,
    path: 'students',
    description: 'Student records',
  },
  {
    label: 'Parents',
    icon: Users,
    path: 'parents',
    description: 'Parent records',
  },
  {
    label: 'Staff',
    icon: Users,
    path: 'staff',
    description: 'Teachers and staff',
  },
  {
    label: 'Academics',
    icon: BookOpen,
    path: 'academics',
    description: 'Classes and subjects',
  },
  {
    label: 'Timetable',
    icon: CalendarDays,
    path: 'timetable',
    description: 'School schedules',
  },
  {
    label: 'Attendance',
    icon: Activity,
    path: 'attendance',
    description: 'Attendance records',
  },
  {
    label: 'Finance',
    icon: Wallet,
    path: 'finance',
    description: 'Fees and payments',
  },
  {
    label: 'Subscriptions',
    icon: CreditCard,
    path: 'subscription',
    description: 'School subscription',
  },
  {
    label: 'Settings',
    icon: Settings,
    path: 'settings',
    description: 'School configuration',
  },
];

const statusLabels = {
  pending: 'Pending approval',
  active: 'Active',
  suspended: 'Suspended',
  archived: 'Archived',
};

function getErrorMessage(error) {
  const data = error.response?.data;

  if (data?.detail) {
    return data.detail;
  }

  if (error.response?.status === 403) {
    return 'You do not have permission to access this school workspace.';
  }

  if (error.response?.status === 404) {
    return 'This school could not be found.';
  }

  return 'Unable to load this school workspace. Please try again.';
}

function SchoolWorkspacePage() {
  const { schoolId } = useParams();
  const navigate = useNavigate();

  const { user, logout } = useAuth();

  const [school, setSchool] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState('');

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const loadWorkspace = useCallback(async () => {
    try {
      setLoading(true);
      setPageError('');

      const response = await schoolService.getWorkspace(schoolId);

      setSchool(response);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [schoolId]);

  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  const handleLogout = async () => {
    try {
      setLoggingOut(true);
      await logout();
    } finally {
      setLoggingOut(false);
    }
  };

  const displayName =
    user?.first_name ||
    user?.full_name ||
    user?.email?.split('@')[0] ||
    'Account';

  const formatDate = (dateString) => {
    if (!dateString) return 'Not available';

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return 'Not available';
    }

    return date.toLocaleDateString('en-NG', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="workspace-loading-page">
        <LoaderCircle size={32} className="workspace-spinner" />
        <p>Preparing your school workspace...</p>
      </div>
    );
  }

  if (pageError || !school) {
    return (
      <div className="workspace-error-page">
        <img src={logo} alt="BaloraEdu" />

        <div className="workspace-error-content">
          <div className="workspace-error-icon">
            <CircleAlert size={30} />
          </div>

          <h1>Workspace unavailable</h1>

          <p>
            {pageError || 'We could not load this school workspace.'}
          </p>

          <div className="workspace-error-actions">
            <button type="button" onClick={loadWorkspace}>
              Try again
            </button>

            <button
              type="button"
              className="workspace-back-button"
              onClick={() => navigate('/schools')}
            >
              <ArrowLeft size={17} />
              Back to schools
            </button>
          </div>
        </div>
      </div>
    );
  }

  const schoolStatus = school.status || 'pending';

  return (
    <div className="workspace-page">
      {sidebarOpen && (
        <button
          type="button"
          className="workspace-sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`workspace-sidebar ${
          sidebarOpen ? 'workspace-sidebar-open' : ''
        }`}
      >
        <div className="workspace-brand">
          <img src={logo} alt="BaloraEdu" />

          <button
            type="button"
            className="workspace-mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="workspace-school-identity">
          <div className="workspace-school-avatar">
            <Building2 size={23} />
          </div>

          <div className="workspace-school-identity-text">
            <strong>{school.name}</strong>
            <span>School workspace</span>
          </div>

          <ChevronDown size={16} />
        </div>

        <div className="workspace-nav-label">
          WORKSPACE
        </div>

        <nav className="workspace-navigation">
          {navigationItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = index === 0;

            return (
              <button
                type="button"
                key={item.path || 'overview'}
                className={`workspace-nav-item ${
                  isActive ? 'workspace-nav-active' : ''
                }`}
                onClick={() => {
                  if (item.path) {
                    navigate(`/schools/${schoolId}/${item.path}`);
                  } else {
                    navigate(`/schools/${schoolId}`);
                  }

                  setSidebarOpen(false);
                }}
                title={item.description}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="workspace-sidebar-bottom">
          <div className="workspace-security-note">
            <ShieldCheck size={19} />

            <div>
              <strong>Secure workspace</strong>
              <span>Your school data is protected.</span>
            </div>
          </div>

          <button
            type="button"
            className="workspace-back-link"
            onClick={() => navigate('/schools')}
          >
            <ArrowLeft size={17} />
            All schools
          </button>
        </div>
      </aside>

      <div className="workspace-main-area">
        <header className="workspace-topbar">
          <div className="workspace-topbar-left">
            <button
              type="button"
              className="workspace-menu-button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={22} />
            </button>

            <div className="workspace-breadcrumb">
              <span>Schools</span>
              <span>/</span>
              <strong>{school.name}</strong>
            </div>
          </div>

          <div className="workspace-topbar-right">
            <button
              type="button"
              className="workspace-notification-button"
              aria-label="Notifications"
              title="Notifications"
            >
              <Bell size={19} />
            </button>

            <div className="workspace-account-wrapper">
              <button
                type="button"
                className="workspace-account-button"
                onClick={() =>
                  setAccountMenuOpen((previous) => !previous)
                }
                aria-expanded={accountMenuOpen}
              >
                <span className="workspace-account-avatar">
                  {displayName.charAt(0).toUpperCase()}
                </span>

                <span className="workspace-account-details">
                  <strong>{displayName}</strong>
                  <small>{user?.email}</small>
                </span>

                <ChevronDown size={16} />
              </button>

              {accountMenuOpen && (
                <div className="workspace-account-dropdown">
                  <button
                    type="button"
                    onClick={handleLogout}
                    disabled={loggingOut}
                  >
                    <LogOut size={17} />
                    {loggingOut ? 'Signing out...' : 'Sign out'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="workspace-content">
          <div className="workspace-page-heading">
            <div>
              <div className="workspace-eyebrow">
                <span />
                SCHOOL MANAGEMENT
              </div>

              <h1>School overview</h1>

              <p>
                Welcome to your {school.name} management workspace.
              </p>
            </div>

            <span
              className={`workspace-status-badge workspace-status-${schoolStatus}`}
            >
              <span />
              {statusLabels[schoolStatus] || schoolStatus}
            </span>
          </div>

          {schoolStatus === 'pending' && (
            <section className="workspace-pending-notice">
              <div className="workspace-notice-icon">
                <CircleAlert size={21} />
              </div>

              <div>
                <strong>School approval pending</strong>
                <p>
                  Your school registration is awaiting approval.
                  You can continue with the setup activities available
                  to your account while you wait.
                </p>
              </div>
            </section>
          )}

          {schoolStatus === 'active' && (
            <section className="workspace-welcome-banner">
              <div className="workspace-banner-icon">
                <GraduationCap size={29} />
              </div>

              <div>
                <span>YOUR SCHOOL WORKSPACE</span>
                <h2>Everything starts here.</h2>
                <p>
                  Manage your school's operations from one organised
                  workspace.
                </p>
              </div>
            </section>
          )}

          <section className="workspace-section">
            <div className="workspace-section-heading">
              <div>
                <h2>School information</h2>
                <p>Your school's registered information.</p>
              </div>
            </div>

            <div className="workspace-information-grid">
              <div className="workspace-information-item">
                <span>School name</span>
                <strong>{school.name || 'Not provided'}</strong>
              </div>

              <div className="workspace-information-item">
                <span>Email address</span>
                <strong>{school.email || 'Not provided'}</strong>
              </div>

              <div className="workspace-information-item">
                <span>Phone number</span>
                <strong>{school.phone_number || 'Not provided'}</strong>
              </div>

              <div className="workspace-information-item">
                <span>School address</span>
                <strong>{school.address || 'Not provided'}</strong>
              </div>

              <div className="workspace-information-item">
                <span>Website</span>
                <strong>
                  {school.website ? (
                    <a
                      href={school.website}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Visit website
                    </a>
                  ) : (
                    'Not provided'
                  )}
                </strong>
              </div>

              <div className="workspace-information-item">
                <span>School timezone</span>
                <strong>{school.timezone || 'Africa/Lagos'}</strong>
              </div>
            </div>
          </section>

          <section className="workspace-section">
            <div className="workspace-section-heading">
              <div>
                <h2>Workspace modules</h2>
                <p>
                  Your school's management tools will be organised here.
                </p>
              </div>
            </div>

            <div className="workspace-module-placeholder">
              <div className="workspace-module-placeholder-icon">
                <BookOpen size={25} />
              </div>

              <div>
                <strong>School management modules</strong>
                <p>
                  Student records, staff management, academics,
                  attendance and finance will be available as their
                  respective modules are implemented.
                </p>
              </div>
            </div>
          </section>

          <footer className="workspace-footer">
            <span>
              © {new Date().getFullYear()} BaloraEdu. All rights reserved.
            </span>

            <span>
              Powered by <strong>BaloraEdu</strong>
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}

export default SchoolWorkspacePage;
