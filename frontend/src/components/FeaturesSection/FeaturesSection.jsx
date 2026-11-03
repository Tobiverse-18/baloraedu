import {
  ArrowUpRight,
  Users,
  CalendarCheck,
  GraduationCap,
  Wallet,
  MessageSquareText,
  ChartNoAxesCombined,
} from 'lucide-react';

import './FeaturesSection.css';

const features = [
  {
    number: '01',
    icon: Users,
    title: 'Student & Staff Management',
    description:
      'Keep student records, teacher profiles, parent information and school memberships organised in one central workspace.',
    link: 'Manage your school community',
  },
  {
    number: '02',
    icon: CalendarCheck,
    title: 'Attendance Management',
    description:
      'Record daily attendance, monitor student presence and give school administrators a clearer view of attendance patterns.',
    link: 'Stay on top of attendance',
  },
  {
    number: '03',
    icon: GraduationCap,
    title: 'Academic Management',
    description:
      'Organise classes, subjects, timetables, assessments, assignments and examination results with less administrative effort.',
    link: 'Simplify academic operations',
  },
  {
    number: '04',
    icon: Wallet,
    title: 'Fees & Financial Management',
    description:
      'Manage school fees, track payments, monitor outstanding balances and keep your financial records organised.',
    link: 'Manage school finances',
  },
  {
    number: '05',
    icon: MessageSquareText,
    title: 'Communication & Announcements',
    description:
      'Keep parents, teachers and students informed through organised school announcements and important updates.',
    link: 'Keep everyone connected',
  },
  {
    number: '06',
    icon: ChartNoAxesCombined,
    title: 'Reports & Performance Insights',
    description:
      'Access academic results, attendance summaries and useful school reports to make more informed decisions.',
    link: 'Understand school performance',
  },
];

function FeaturesSection() {
  return (
    <section className="features-section" id="features">
      <div className="features-container">

        <div className="features-intro">
          <div className="features-eyebrow">
            <span />
            EVERYTHING WORKS BETTER TOGETHER
          </div>

          <div className="features-intro-content">
            <div>
              <h2>
                Everything your school needs.
                <span> All in one place.</span>
              </h2>
            </div>

            <p>
              From everyday school administration to academic activities
              and financial records, Balora Edu brings the essential parts
              of running a school into one connected platform.
            </p>
          </div>
        </div>

        <div className="features-grid">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <article className="feature-card" key={feature.number}>
                <div className="feature-card-top">
                  <div className="feature-icon">
                    <Icon size={22} strokeWidth={1.8} />
                  </div>

                  <span className="feature-number">
                    {feature.number}
                  </span>
                </div>

                <div className="feature-card-content">
                  <h3>{feature.title}</h3>

                  <p>{feature.description}</p>
                </div>

                <div className="feature-card-bottom">
                  <span>{feature.link}</span>
                  <ArrowUpRight size={17} />
                </div>
              </article>
            );
          })}
        </div>

        <div className="features-bottom">
          <div className="features-bottom-line" />

          <p>
            One platform. Multiple school operations. A more organised
            way to work.
          </p>

          <div className="features-bottom-line" />
        </div>

      </div>
    </section>
  );
}

export default FeaturesSection;