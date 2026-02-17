/**
 * WatcherButton - Watch/Unwatch amendments for notifications
 *
 * Features:
 * - Toggle watch/unwatch
 * - Display watcher count
 * - Show watching status
 */

import React, { useState, useEffect } from 'react';
import apiClient from '../../services/api';
import './WatcherButton.css';

const WatcherButton = ({ amendmentId }) => {
  const [isWatching, setIsWatching] = useState(false);
  const [watcherCount, setWatcherCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showWatchers, setShowWatchers] = useState(false);
  const [watchers, setWatchers] = useState([]);

  useEffect(() => {
    if (amendmentId) {
      checkWatchStatus();
      loadWatchers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [amendmentId]);

  const checkWatchStatus = async () => {
    try {
      const response = await apiClient.get(`/amendments/${amendmentId}/is-watching`);
      setIsWatching(response.data.is_watching);
    } catch (error) {
      console.error('Error checking watch status:', error);
    }
  };

  const loadWatchers = async () => {
    try {
      const response = await apiClient.get(`/amendments/${amendmentId}/watchers`);
      setWatchers(response.data);
      setWatcherCount(response.data.length);
    } catch (error) {
      console.error('Error loading watchers:', error);
    }
  };

  const toggleWatch = async () => {
    if (loading) return;

    setLoading(true);
    try {
      if (isWatching) {
        await apiClient.delete(`/amendments/${amendmentId}/watchers`);
        setIsWatching(false);
        await loadWatchers();
      } else {
        await apiClient.post(`/amendments/${amendmentId}/watchers`, { watch_reason: 'Manual' });
        setIsWatching(true);
        await loadWatchers();
      }
    } catch (error) {
      console.error('Error toggling watch:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="watcher-button-container">
      <button
        className={`watcher-button ${isWatching ? 'watching' : ''}`}
        onClick={toggleWatch}
        disabled={loading}
        title={isWatching ? 'Unwatch this amendment' : 'Watch this amendment for notifications'}
      >
        <span className="watcher-icon">
          {isWatching ? '🔔' : '🔕'}
        </span>
        <span className="watcher-text">
          {isWatching ? 'Watching' : 'Watch'}
        </span>
        <span
          className="watcher-count"
          onClick={(e) => {
            e.stopPropagation();
            setShowWatchers(!showWatchers);
          }}
          title={`${watcherCount} watcher${watcherCount !== 1 ? 's' : ''}`}
        >
          {watcherCount}
        </span>
      </button>

      {showWatchers && watcherCount > 0 && (
        <div className="watchers-dropdown">
          <div className="watchers-header">
            <span>Watchers ({watcherCount})</span>
            <button
              className="close-dropdown"
              onClick={() => setShowWatchers(false)}
            >
              ×
            </button>
          </div>
          <div className="watchers-list">
            {watchers.map(watcher => (
              <div key={watcher.watcher_id} className="watcher-item">
                <div className="watcher-avatar">
                  {watcher.employee_name ? watcher.employee_name.charAt(0).toUpperCase() : '?'}
                </div>
                <div className="watcher-info">
                  <div className="watcher-name">{watcher.employee_name || 'Unknown'}</div>
                  <div className="watcher-reason">{watcher.watch_reason}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WatcherButton;
