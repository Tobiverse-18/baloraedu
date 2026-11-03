import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  GraduationCap,
  MoreHorizontal,
  Users,
} from 'lucide-react';

import './HeroSection.css';

function HeroSection() {
  return (
    <section className="hero-section" id="home">
      <div className="hero-background-glow" />

      <div className="hero-container">
        {/* Hero Content */}
        <div className="hero-content">
          <h1>
            School management,
            <span> made beautifully simple.</span>
          </h1>

          <p className="hero-description">
            Bring your entire school together in one place. Manage students,
            teachers, attendance, academics, fees and communication without
            the everyday complexity.
          </p>

          <div className="hero-actions">
            <a href="/register" className="hero-primary-button">
              Get started
              <ArrowRight size={18} />
            </a>

            <a href="#features" className="hero-secondary-button">
              Explore the platform
              <span className="hero-play-icon">
                <ArrowRight size={15} />
              </span>
            </a>
          </div>

          <div className="hero-trust">
            <div className="hero-trust-avatars">
              <span className="trust-avatar avatar-one">A</span>
              <span className="trust-avatar avatar-two">T</span>
              <span className="trust-avatar avatar-three">S</span>
              <span className="trust-avatar avatar-four">+</span>
            </div>

            <div className="hero-trust-copy">
              <strong>Everything in one place</strong>
              <span>One connected platform for your school.</span>
            </div>
          </div>
        </div>

        {/* Hero Dashboard Preview */}
        <div className="hero-visual">
          <div className="hero-visual-decoration decoration-one" />
          <div className="hero-visual-decoration decoration-two" />

          <div className="hero-dashboard">
            {/* Dashboard Sidebar */}
            <aside className="dashboard-sidebar">
              <div className="dashboard-sidebar-brand">
                <div className="dashboard-brand-icon">
                  <GraduationCap size={19} />
                </div>
                <span>balora<span>edu.</span></span>
              </div>

              <div className="dashboard-school">
                <div className="dashboard-school-avatar">W</div>
                <div>
                  <strong>Westfield Academy</strong>
                  <span>School workspace</span>
                </div>
                <ChevronDown size={14} />
              </div>

              <span className="dashboard-menu-label">WORKSPACE</span>

              <div className="dashboard-menu-item active">
                <span><BookOpen size={16} /></span>
                Overview
              </div>

              <div className="dashboard-menu-item">
                <span><Users size={16} /></span>
                Students
              </div>

              <div className="dashboard-menu-item">
                <span><GraduationCap size={16} /></span>
                Teachers
              </div>

              <div className="dashboard-menu-item">
                <span><CalendarDays size={16} /></span>
                Attendance
              </div>

              <div className="dashboard-menu-item">
                <span><BookOpen size={16} /></span>
                Academics
              </div>

              <div className="dashboard-sidebar-bottom">
                <div className="dashboard-sidebar-profile">
                  <div className="dashboard-profile-avatar">AD</div>
                  <div>
                    <strong>School Admin</strong>
                    <span>Administrator</span>
                  </div>
                  <MoreHorizontal size={16} />
                </div>
              </div>
            </aside>

            {/* Dashboard Main */}
            <div className="dashboard-main">
              <div className="dashboard-topbar">
                <div>
                  <span className="dashboard-breadcrumb">Workspace /</span>
                  <strong>Overview</strong>
                </div>

                <div className="dashboard-topbar-right">
                  <span className="dashboard-date">
                    <CalendarDays size={13} />
                    Today
                  </span>
                  <div className="dashboard-notification">
                    <span />
                    <MoreHorizontal size={18} />
                  </div>
                  <div className="dashboard-user-avatar">AD</div>
                </div>
              </div>

              <div className="dashboard-welcome">
                <div>
                  <span>MONDAY, 12 OCTOBER 2026</span>
                  <h3>Good morning, Admin <span>✦</span></h3>
                  <p>Here's what's happening in your school today.</p>
                </div>

                <button type="button" className="dashboard-export">
                  Overview <ChevronDown size={13} />
                </button>
              </div>

              {/* Statistics */}
              <div className="dashboard-stats">
                <div className="dashboard-stat-card">
                  <div className="stat-card-heading">
                    <span>Total students</span>
                    <span className="stat-icon stat-blue">
                      <Users size={15} />
                    </span>
                  </div>
                  <strong>1,248</strong>
                  <div className="stat-card-footer">
                    <span className="stat-positive">+8.2%</span>
                    <span>from last term</span>
                  </div>
                </div>

                <div className="dashboard-stat-card">
                  <div className="stat-card-heading">
                    <span>Teaching staff</span>
                    <span className="stat-icon stat-purple">
                      <GraduationCap size={15} />
                    </span>
                  </div>
                  <strong>86</strong>
                  <div className="stat-card-footer">
                    <span className="stat-neutral">Active</span>
                    <span>across departments</span>
                  </div>
                </div>

                <div className="dashboard-stat-card">
                  <div className="stat-card-heading">
                    <span>Attendance</span>
                    <span className="stat-icon stat-green">
                      <CheckCircle2 size={15} />
                    </span>
                  </div>
                  <strong>94.6%</strong>
                  <div className="stat-card-footer">
                    <span className="stat-positive">+2.4%</span>
                    <span>from yesterday</span>
                  </div>
                </div>
              </div>

              {/* Dashboard Lower Content */}
              <div className="dashboard-lower">
                <div className="dashboard-attendance">
                  <div className="dashboard-section-heading">
                    <div>
                      <strong>Attendance overview</strong>
                      <span>Student attendance for today</span>
                    </div>
                    <MoreHorizontal size={18} />
                  </div>

                  <div className="attendance-chart">
                    <div className="attendance-chart-info">
                      <strong>94.6%</strong>
                      <span>Attendance rate</span>
                    </div>

                    <div className="attendance-chart-visual">
                      <div className="attendance-ring">
                        <div className="attendance-ring-inner">
                          <strong>94.6%</strong>
                          <span>Present</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="attendance-legend">
                    <span><i className="legend-present" /> Present <strong>1,180</strong></span>
                    <span><i className="legend-absent" /> Absent <strong>68</strong></span>
                  </div>
                </div>

                <div className="dashboard-activity">
                  <div className="dashboard-section-heading">
                    <div>
                      <strong>Recent activity</strong>
                      <span>Latest school updates</span>
                    </div>
                    <MoreHorizontal size={18} />
                  </div>

                  <div className="activity-item">
                    <div className="activity-icon activity-blue">
                      <Users size={14} />
                    </div>
                    <div>
                      <strong>New student registered</strong>
                      <span>John A. · JSS 2</span>
                    </div>
                    <small>9:42</small>
                  </div>

                  <div className="activity-item">
                    <div className="activity-icon activity-green">
                      <CheckCircle2 size={14} />
                    </div>
                    <div>
                      <strong>Attendance completed</strong>
                      <span>Primary 5 · Mrs. James</span>
                    </div>
                    <small>9:15</small>
                  </div>

                  <div className="activity-item">
                    <div className="activity-icon activity-purple">
                      <BookOpen size={14} />
                    </div>
                    <div>
                      <strong>Assessment uploaded</strong>
                      <span>Mathematics · JSS 3</span>
                    </div>
                    <small>8:50</small>
                  </div>
                </div>
              </div>

              <div className="dashboard-bottom-line">
                <span><i /> All systems operational</span>
                <span>Balora Edu workspace</span>
              </div>
            </div>
          </div>

          {/* Floating Attendance Card */}
          <div className="hero-floating-card floating-attendance">
            <div className="floating-card-icon">
              <CheckCircle2 size={17} />
            </div>
            <div>
              <span>Attendance marked</span>
              <strong>94.6% <small>today</small></strong>
            </div>
          </div>

          {/* Floating Student Card */}
          <div className="hero-floating-card floating-students">
            <div className="floating-students-icon">
              <Users size={17} />
            </div>
            <div>
              <span>Growing together</span>
              <strong>1,248 students</strong>
            </div>
            <ArrowUpRight size={16} />
          </div>
        </div>
      </div>

      <div className="hero-bottom-fade" />
    </section>
  );
}

export default HeroSection;