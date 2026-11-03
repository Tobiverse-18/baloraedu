import { ArrowRight, CheckCircle2, School, Settings2, LayoutDashboard } from 'lucide-react';
import { Link } from 'react-router-dom';

import './HowItWorksSection.css';

const steps = [
  {
    number: '01',
    icon: School,
    title: 'Create your school account',
    description:
      'Get started by registering your school on Balora Edu. Provide your basic school information and create your administrator account.',
    details: ['Simple registration', 'Secure school account'],
  },
  {
    number: '02',
    icon: Settings2,
    title: 'Set up your school',
    description:
      'Configure your school environment, add staff members, organise classes and prepare your academic structure.',
    details: ['Organise your classes', 'Add staff and students'],
  },
  {
    number: '03',
    icon: LayoutDashboard,
    title: 'Manage everything in one place',
    description:
      'Bring your school operations together. Manage attendance, academics, fees, communication and performance from one platform.',
    details: ['Access your school dashboard', 'Stay on top of daily activities'],
  },
];

function HowItWorksSection() {
  return (
    <section className="how-it-works-section" id="how-it-works">
      <div className="how-it-works-container">
        <div className="how-it-works-heading">

          <h2>
            Your school, up and running
            <span> in three simple steps.</span>
          </h2>

          <p>
            Getting started with Balora Edu is straightforward.
            Set up your school and bring your everyday operations
            together in one connected platform.
          </p>
        </div>

        <div className="how-it-works-grid">
          {steps.map((step, index) => {
            const Icon = step.icon;

            return (
              <article className="how-it-works-card" key={step.number}>
                <div className="how-it-works-card-top">
                  <div className="how-it-works-icon">
                    <Icon size={23} strokeWidth={1.8} />
                  </div>

                  <span className="how-it-works-number">
                    {step.number}
                  </span>
                </div>

                <h3>{step.title}</h3>

                <p>{step.description}</p>

                <div className="how-it-works-details">
                  {step.details.map((detail) => (
                    <div className="how-it-works-detail" key={detail}>
                      <CheckCircle2 size={16} />
                      <span>{detail}</span>
                    </div>
                  ))}
                </div>

                {index !== steps.length - 1 && (
                  <div className="how-it-works-connector" />
                )}
              </article>
            );
          })}
        </div>

        <div className="how-it-works-bottom">
          <div>
            <span>READY TO GET STARTED?</span>
            <h3>Give your school a smarter way to work.</h3>
          </div>

          <Link to="/schools/register" className="how-it-works-cta">
            Register your school
            <ArrowRight size={17} />
          </Link>
        </div>
      </div>
    </section>
  );
}

export default HowItWorksSection;