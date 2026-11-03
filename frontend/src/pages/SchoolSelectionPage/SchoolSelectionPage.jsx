import { useCallback, useEffect, useState } from 'react';
import {
  ArrowRight,
  Building2,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  Clock3,
  GraduationCap,
  LoaderCircle,
  LogOut,
  Mail,
  MapPin,
  Plus,
  School,
  ShieldCheck,
  X,
} from 'lucide-react';

import { useAuth } from '../../hooks/useAuth';
import schoolService from '../../services/schoolService';

import './SchoolSelectionPage.css';
import logo from '../../assets/balora_logo.png';

const initialFormData = {
  name: '',
  email: '',
  phone_number: '',
  address: '',
  website: '',
};

const schoolStatusConfig = {
  pending: {
    label: 'Pending approval',
    className: 'school-status-pending',
    icon: Clock3,
  },
  active: {
    label: 'Active',
    className: 'school-status-active',
    icon: CheckCircle2,
  },
  suspended: {
    label: 'Suspended',
    className: 'school-status-suspended',
    icon: CircleAlert,
  },
  archived: {
    label: 'Archived',
    className: 'school-status-archived',
    icon: CircleAlert,
  },
};

const roleLabels = {
  school_owner: 'School Owner',
  school_admin: 'School Admin',
  principal: 'Principal',
  accountant: 'Accountant',
  teacher: 'Teacher',
  parent: 'Parent',
  student: 'Student',
};

function getErrorMessage(error) {
  const data = error.response?.data;

  if (!data) {
    return 'Something went wrong. Please check your connection and try again.';
  }

  if (data.detail) {
    return data.detail;
  }

  const firstError = Object.values(data).flat()[0];

  return typeof firstError === 'string'
    ? firstError
    : 'Unable to complete your request. Please try again.';
}

function SchoolSelectionPage() {
  const { user, logout } = useAuth();

  const [schools, setSchools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState('');
  const [formError, setFormError] = useState('');

  const [showRegistration, setShowRegistration] = useState(false);
  const [registering, setRegistering] = useState(false);

  const [formData, setFormData] = useState(initialFormData);

  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const loadSchools = useCallback(async () => {
    try {
      setLoading(true);
      setPageError('');

      const response = await schoolService.getMySchools();

      const results = Array.isArray(response)
        ? response
        : response.results || [];

      setSchools(results);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSchools();
  }, [loadSchools]);

  const handleFormChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setFormError('');
  };

  const handleRegisterSchool = async (event) => {
    event.preventDefault();
    setFormError('');

    const name = formData.name.trim();

    if (name.length < 2) {
      setFormError('School name must contain at least 2 characters.');
      return;
    }

    let normalizedWebsite = formData.website.trim();

    if (normalizedWebsite) {
    if (!/^https?:\/\//i.test(normalizedWebsite)) {
        normalizedWebsite = `https://${normalizedWebsite}`;
    }

    try {
        const websiteUrl = new URL(normalizedWebsite);

        if (
        !['http:', 'https:'].includes(websiteUrl.protocol) ||
        !websiteUrl.hostname.includes('.') ||
        !websiteUrl.hostname.split('.').every(Boolean)
        ) {
        throw new Error('Invalid website');
        }

        normalizedWebsite = websiteUrl.toString();
    } catch {
        setFormError(
        'Enter a valid website address, e.g. www.graceacademy.com.'
        );
        return;
    }
    }

    const schoolData = {
      name,
      email: formData.email.trim(),
      phone_number: formData.phone_number.trim(),
      address: formData.address.trim(),
      website: normalizedWebsite,
    };

    try {
      setRegistering(true);

      await schoolService.registerSchool(schoolData);

      setFormData(initialFormData);
      setShowRegistration(false);

      await loadSchools();
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setRegistering(false);
    }
  };

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
    'there';

  const formatDate = (dateString) => {
    if (!dateString) return 'Recently joined';

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return 'Recently joined';
    }

    return date.toLocaleDateString('en-NG', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="school-selection-page">
      <header className="school-topbar">
        <div className="school-topbar-inner">
            <img src={logo} alt="Balora Edu" />
          

          <div className="school-account-area">
            <div className="school-account-info">
              <span className="school-account-name">
                {displayName}
              </span>

              <span className="school-account-email">
                {user?.email}
              </span>
            </div>

            <div className="school-account-menu-wrapper">
              <button
                type="button"
                className="school-account-button"
                onClick={() =>
                  setShowAccountMenu((previous) => !previous)
                }
                aria-label="Account menu"
                aria-expanded={showAccountMenu}
              >
                <span className="school-account-avatar">
                  {displayName.charAt(0).toUpperCase()}
                </span>

                <ChevronDown size={16} />
              </button>

              {showAccountMenu && (
                <div className="school-account-dropdown">
                  <div className="school-dropdown-user">
                    <strong>{displayName}</strong>
                    <span>{user?.email}</span>
                  </div>

                  <button
                    type="button"
                    onClick={handleLogout}
                    disabled={loggingOut}
                  >
                    {loggingOut ? (
                      <LoaderCircle
                        size={17}
                        className="school-spinner"
                      />
                    ) : (
                      <LogOut size={17} />
                    )}

                    {loggingOut ? 'Signing out...' : 'Sign out'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="school-main">
        <section className="school-welcome-section">
          <div>
            <div className="school-eyebrow">
              <span />
              YOUR EDUCATION WORKSPACE
            </div>

            <h1>
              Welcome back, {displayName}.
            </h1>

            <p>
              Select a school to continue or register a new school
              on BaloraEdu.
            </p>
          </div>

          <div className="school-welcome-decoration">
            <div className="school-decoration-circle">
              <GraduationCap size={37} />
            </div>
          </div>
        </section>

        <section className="school-content-section">
          <div className="school-section-heading">
            <div>
              <h2>Your schools</h2>
              <p>
                Schools where you have an active membership.
              </p>
            </div>

            <button
              type="button"
              className="school-add-button"
              onClick={() => {
                setShowRegistration(true);
                setFormError('');
              }}
            >
              <Plus size={18} />
              Register a school
            </button>
          </div>

          {pageError && (
            <div className="school-page-error" role="alert">
              <CircleAlert size={19} />
              <span>{pageError}</span>

              <button
                type="button"
                onClick={loadSchools}
              >
                Try again
              </button>
            </div>
          )}

          {loading ? (
            <div className="school-loading-state">
              <LoaderCircle
                size={30}
                className="school-spinner"
              />
              <p>Loading your schools...</p>
            </div>
          ) : schools.length === 0 ? (
            <div className="school-empty-state">
              <div className="school-empty-icon">
                <Building2 size={34} />
              </div>

              <h3>You haven't joined a school yet</h3>

              <p>
                Register your school to get started with BaloraEdu,
                or wait for an invitation from a school administrator.
              </p>

              <button
                type="button"
                className="school-empty-button"
                onClick={() => setShowRegistration(true)}
              >
                <Plus size={18} />
                Register your first school
              </button>
            </div>
          ) : (
            <div className="school-card-grid">
              {schools.map((membership) => {
                const school = membership.school;

                const status =
                  schoolStatusConfig[school.status] ||
                  schoolStatusConfig.pending;

                const StatusIcon = status.icon;

                return (
                  <article
                    className="school-card"
                    key={membership.id}
                  >
                    <div className="school-card-top">
                      <div className="school-card-icon">
                        <School size={25} />
                      </div>

                      <span
                        className={`school-status ${status.className}`}
                      >
                        <StatusIcon size={14} />
                        {status.label}
                      </span>
                    </div>

                    <div className="school-card-details">
                      <h3>{school.name}</h3>

                      <span className="school-card-role">
                        {roleLabels[membership.role] ||
                          membership.role}
                      </span>

                      {school.email && (
                        <div className="school-card-meta">
                          <Mail size={15} />
                          <span>{school.email}</span>
                        </div>
                      )}

                      {membership.joined_at && (
                        <div className="school-card-meta">
                          <CalendarDays size={15} />
                          <span>
                            Joined {formatDate(membership.joined_at)}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="school-card-footer">
                      <span>
                        {membership.status === 'active'
                          ? 'Membership active'
                          : membership.status}
                      </span>

                      <span className="school-card-reference">
                        {school.slug}
                      </span>
                    </div>

                    <div className="school-card-note">
                      {school.status === 'pending' ? (
                        <>
                          <Clock3 size={15} />
                          <span>
                            Your school is awaiting approval. Setup
                            access depends on your role.
                          </span>
                        </>
                      ) : school.status === 'active' ? (
                        <>
                          <ShieldCheck size={15} />
                          <span>
                            Your school is active on BaloraEdu.
                          </span>
                        </>
                      ) : (
                        <>
                          <CircleAlert size={15} />
                          <span>
                            Workspace access is currently unavailable.
                          </span>
                        </>
                      )}
                    </div>

                    <div className="school-card-action">
                      <button
                        type="button"
                        disabled={
                          school.status === 'suspended' ||
                          school.status === 'archived'
                        }
                        onClick={() => {
                          window.location.href =
                            `/schools/${school.id}`;
                        }}
                      >
                        {school.status === 'pending'
                          ? 'Continue setup'
                          : 'Open workspace'}

                        <ArrowRight size={17} />
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        <section className="school-help-strip">
          <div className="school-help-icon">
            <ShieldCheck size={21} />
          </div>

          <div>
            <strong>Your schools, securely managed.</strong>
            <p>
              Your access and permissions are managed separately
              for each school.
            </p>
          </div>
        </section>
      </main>

      {showRegistration && (
        <div
          className="school-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !registering) {
              setShowRegistration(false);
              setFormError('');
            }
          }}
        >
          <section
            className="school-registration-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="school-registration-title"
          >
            <div className="school-modal-header">
              <div>
                <span className="school-modal-eyebrow">
                  GET STARTED
                </span>

                <h2 id="school-registration-title">
                  Register your school
                </h2>

                <p>
                  Enter your school's details to create its
                  BaloraEdu workspace.
                </p>
              </div>

              <button
                type="button"
                className="school-modal-close"
                onClick={() => {
                  setShowRegistration(false);
                  setFormError('');
                }}
                disabled={registering}
                aria-label="Close registration form"
              >
                <X size={20} />
              </button>
            </div>

            <form
              className="school-registration-form"
              onSubmit={handleRegisterSchool}
            >
              {formError && (
                <div className="school-form-error" role="alert">
                  <CircleAlert size={17} />
                  <span>{formError}</span>
                </div>
              )}

              <div className="school-form-field">
                <label htmlFor="school-name">
                  School name <span>*</span>
                </label>

                <input
                  id="school-name"
                  type="text"
                  name="name"
                  placeholder="e.g. Grace Academy"
                  value={formData.name}
                  onChange={handleFormChange}
                  maxLength={255}
                  required
                  disabled={registering}
                />
              </div>

              <div className="school-form-row">
                <div className="school-form-field">
                  <label htmlFor="school-email">
                    School email
                  </label>

                  <input
                    id="school-email"
                    type="email"
                    name="email"
                    placeholder="school@example.com"
                    value={formData.email}
                    onChange={handleFormChange}
                    disabled={registering}
                  />
                </div>

                <div className="school-form-field">
                  <label htmlFor="school-phone">
                    Phone number
                  </label>

                  <input
                    id="school-phone"
                    type="tel"
                    name="phone_number"
                    placeholder="+234..."
                    value={formData.phone_number}
                    onChange={handleFormChange}
                    maxLength={20}
                    disabled={registering}
                  />
                </div>
              </div>

              <div className="school-form-field">
                <label htmlFor="school-address">
                  School address
                </label>

                <textarea
                  id="school-address"
                  name="address"
                  placeholder="Enter the school's full address"
                  value={formData.address}
                  onChange={handleFormChange}
                  rows={3}
                  disabled={registering}
                />
              </div>

              <div className="school-form-field">
                <label htmlFor="school-website">
                  School website
                </label>

                <input
                  id="school-website"
                  type="text"
                  name="website"
                  placeholder="e.g. www.graceacademy.com"
                  value={formData.website}
                  onChange={handleFormChange}
                  disabled={registering}
                />
              </div>

              <div className="school-registration-note">
                <ShieldCheck size={17} />
                <span>
                  You will automatically become the School Owner
                  of this school.
                </span>
              </div>

              <div className="school-modal-actions">
                <button
                  type="button"
                  className="school-cancel-button"
                  onClick={() => {
                    setShowRegistration(false);
                    setFormError('');
                  }}
                  disabled={registering}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="school-create-button"
                  disabled={registering}
                >
                  {registering ? (
                    <>
                      <LoaderCircle
                        size={18}
                        className="school-spinner"
                      />
                      Registering...
                    </>
                  ) : (
                    <>
                      Register school
                      <ArrowRight size={17} />
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}

export default SchoolSelectionPage;