/**
 * CommentReactions - Emoji reactions for QA comments
 *
 * Features:
 * - Display reactions with counts
 * - Toggle reactions (add/remove)
 * - Emoji picker
 * - Supported emojis: 👍 👎 ❤️ 🎉 😄 🚀
 */

import React, { useState, useEffect } from 'react';
import apiClient from '../../services/api';
import './CommentReactions.css';

const CommentReactions = ({ commentId, initialReactions = {} }) => {
  const [reactions, setReactions] = useState(initialReactions);
  const [showPicker, setShowPicker] = useState(false);
  const [userReactions, setUserReactions] = useState(new Set());
  const [loading, setLoading] = useState(false);

  const availableEmojis = ['👍', '👎', '❤️', '🎉', '😄', '🚀'];

  useEffect(() => {
    loadReactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [commentId]);

  const loadReactions = async () => {
    try {
      const response = await apiClient.get(`/comments/${commentId}/reactions/summary`);
      setReactions(response.data.reactions || {});

      // Load user's reactions
      const userReactionsResponse = await apiClient.get(`/comments/${commentId}/reactions`);
      let currentUser = null;
      try {
        currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      } catch {
        currentUser = {};
      }
      const myReactions = userReactionsResponse.data
        .filter(r => r.employee_id === currentUser.employee_id)
        .map(r => r.emoji);
      setUserReactions(new Set(myReactions));
    } catch (error) {
      console.error('Error loading reactions:', error);
    }
  };

  const toggleReaction = async (emoji) => {
    if (loading) return;

    setLoading(true);
    try {
      await apiClient.post(`/comments/${commentId}/reactions`, null, {
        params: { emoji },
      });
      await loadReactions();
      setShowPicker(false);
    } catch (error) {
      console.error('Error toggling reaction:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="comment-reactions">
      <div className="reactions-display">
        {Object.entries(reactions).map(([emoji, count]) => {
          const isUserReaction = userReactions.has(emoji);
          return (
            <button
              key={emoji}
              className={`reaction-button ${isUserReaction ? 'user-reacted' : ''}`}
              onClick={() => toggleReaction(emoji)}
              disabled={loading}
              title={isUserReaction ? 'Remove your reaction' : 'Add reaction'}
            >
              <span className="reaction-emoji">{emoji}</span>
              <span className="reaction-count">{count}</span>
            </button>
          );
        })}
      </div>

      <div className="add-reaction-container">
        <button
          className="add-reaction-btn"
          onClick={() => setShowPicker(!showPicker)}
          disabled={loading}
          title="Add reaction"
        >
          😊 +
        </button>

        {showPicker && (
          <div className="emoji-picker">
            <div className="emoji-picker-header">
              <span>Add reaction</span>
              <button
                className="close-picker"
                onClick={() => setShowPicker(false)}
              >
                ×
              </button>
            </div>
            <div className="emoji-options">
              {availableEmojis.map(emoji => {
                const isUserReaction = userReactions.has(emoji);
                return (
                  <button
                    key={emoji}
                    onClick={() => toggleReaction(emoji)}
                    className={`emoji-option ${isUserReaction ? 'selected' : ''}`}
                    disabled={loading}
                    title={isUserReaction ? `Remove ${emoji}` : `Add ${emoji}`}
                  >
                    {emoji}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommentReactions;
