import React from 'react';
import './Landing.css';

function Landing() {
  return (
    <div className="landing">
      <div className="landing-container">
        <header className="landing-header">
          <h1>🎾 CourtIQ</h1>
          <p>AI-Powered Analytics for Tennis Clubs</p>
        </header>

        <div className="landing-cards">
          <a href="/chat" className="landing-card">
            <div className="card-icon">💬</div>
            <h2>AI Assistant</h2>
            <p>Ask questions about your club data in natural language</p>
            <button>Get Started →</button>
          </a>

          <a href="/admin" className="landing-card">
            <div className="card-icon">⚙️</div>
            <h2>Admin Panel</h2>
            <p>Manage members, bookings, coaches, and courts</p>
            <button>Go to Admin →</button>
          </a>
        </div>

        <div className="landing-features">
          <div className="feature">
            <span>📊</span>
            <p>Real-time Analytics</p>
          </div>
          <div className="feature">
            <span>🤖</span>
            <p>Natural Language Queries</p>
          </div>
          <div className="feature">
            <span>📈</span>
            <p>Revenue Insights</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Landing;