import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { amendmentAPI } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await amendmentAPI.getStats();
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load statistics: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!stats) {
    return <div className="error">No statistics available</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Overview of amendment statistics</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-label">Total Amendments</div>
          <div className="stat-value">{stats.total_amendments}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">QA Completed</div>
          <div className="stat-value">{stats.qa_completed}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Database Changes</div>
          <div className="stat-value">{stats.database_changes}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">DB Upgrade Changes</div>
          <div className="stat-value">{stats.db_upgrade_changes}</div>
        </div>
      </div>

      <div className="stats-section">
        <div className="stat-group">
          <h2 className="stat-group-title">By Status</h2>
          <div className="stat-list">
            {Object.entries(stats.by_status).map(([status, count]) => (
              <div key={status} className="stat-item">
                <span className="stat-item-label">{status}</span>
                <span className={`stat-item-value status-${status.toLowerCase().replace(' ', '-')}`}>
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="stat-group">
          <h2 className="stat-group-title">By Priority</h2>
          <div className="stat-list">
            {Object.entries(stats.by_priority).map(([priority, count]) => (
              <div key={priority} className="stat-item">
                <span className="stat-item-label">{priority}</span>
                <span className={`stat-item-value priority-${priority.toLowerCase()}`}>
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="stat-group">
          <h2 className="stat-group-title">By Type</h2>
          <div className="stat-list">
            {Object.entries(stats.by_type).map(([type, count]) => (
              <div key={type} className="stat-item">
                <span className="stat-item-label">{type}</span>
                <span className="stat-item-value">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="stat-group">
          <h2 className="stat-group-title">By Development Status</h2>
          <div className="stat-list">
            {Object.entries(stats.by_development_status).map(([status, count]) => (
              <div key={status} className="stat-item">
                <span className="stat-item-label">{status}</span>
                <span className="stat-item-value">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="dashboard-actions">
        <Link to="/amendments" className="btn btn-primary">
          View All Amendments
        </Link>
        <Link to="/amendments/new" className="btn btn-secondary">
          Create New Amendment
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;
