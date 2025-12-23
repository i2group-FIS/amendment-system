import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { amendmentAPI, referenceAPI, employeeAPI } from '../services/api';
import './AmendmentDetail.css';

function AmendmentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [amendment, setAmendment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [saving, setSaving] = useState(false);

  // Reference data
  const [types, setTypes] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [devStatuses, setDevStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [forces, setForces] = useState([]);
  const [employees, setEmployees] = useState([]);

  // Progress modal
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [progressData, setProgressData] = useState({
    description: '',
    notes: '',
    start_date: new Date().toISOString().slice(0, 16)
  });

  const loadAmendment = useCallback(async () => {
    try {
      setLoading(true);
      const response = await amendmentAPI.getById(id);
      setAmendment(response.data);
      setFormData(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load amendment');
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadReferenceData = useCallback(async () => {
    try {
      const [typesRes, statusesRes, devStatusesRes, prioritiesRes, forcesRes, employeesRes] = await Promise.all([
        referenceAPI.getTypes(),
        referenceAPI.getStatuses(),
        referenceAPI.getDevelopmentStatuses(),
        referenceAPI.getPriorities(),
        referenceAPI.getForces(),
        employeeAPI.getAll({ active_only: true }),
      ]);

      setTypes(typesRes.data);
      setStatuses(statusesRes.data);
      setDevStatuses(devStatusesRes.data);
      setPriorities(prioritiesRes.data);
      setForces(forcesRes.data);
      setEmployees(employeesRes.data);
    } catch (err) {
      console.error('Failed to load reference data:', err);
    }
  }, []);

  useEffect(() => {
    loadAmendment();
    loadReferenceData();
  }, [loadAmendment, loadReferenceData]);

  const handleEdit = () => {
    setEditing(true);
  };

  const handleCancel = () => {
    setEditing(false);
    setFormData(amendment);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await amendmentAPI.update(id, formData);
      await loadAmendment();
      setEditing(false);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save amendment');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this amendment?')) {
      try {
        await amendmentAPI.delete(id);
        navigate('/amendments');
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to delete amendment');
      }
    }
  };

  const handleAddProgress = async () => {
    try {
      await amendmentAPI.addProgress(id, progressData);
      setShowProgressModal(false);
      setProgressData({
        description: '',
        notes: '',
        start_date: new Date().toISOString().slice(0, 16)
      });
      await loadAmendment();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add progress');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return <div className="loading">Loading amendment...</div>;
  }

  if (error && !amendment) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/amendments')}>Back to List</button>
      </div>
    );
  }

  return (
    <div className="amendment-detail">
      <div className="detail-header">
        <div>
          <h1>{amendment.amendment_reference}</h1>
          <div className="status-badges">
            <span className={`badge status-${amendment.amendment_status.toLowerCase().replace(' ', '-')}`}>
              {amendment.amendment_status}
            </span>
            <span className={`badge dev-status-${amendment.development_status.toLowerCase().replace(' ', '-')}`}>
              {amendment.development_status}
            </span>
            <span className={`badge priority-${amendment.priority.toLowerCase()}`}>
              {amendment.priority}
            </span>
          </div>
        </div>
        <div className="detail-actions">
          {!editing ? (
            <>
              <button className="btn btn-primary" onClick={handleEdit}>Edit</button>
              <button className="btn btn-success" onClick={() => setShowProgressModal(true)}>Add Progress</button>
              <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
            </>
          ) : (
            <>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button className="btn btn-secondary" onClick={handleCancel}>Cancel</button>
            </>
          )}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="detail-content">
        <div className="detail-section">
          <h2>Details</h2>
          <div className="detail-grid">
            <div className="detail-field">
              <label>Type</label>
              {editing ? (
                <select name="amendment_type" value={formData.amendment_type} onChange={handleChange}>
                  {types.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              ) : (
                <div>{amendment.amendment_type}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Status</label>
              {editing ? (
                <select name="amendment_status" value={formData.amendment_status} onChange={handleChange}>
                  {statuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              ) : (
                <div>{amendment.amendment_status}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Development Status</label>
              {editing ? (
                <select name="development_status" value={formData.development_status} onChange={handleChange}>
                  {devStatuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              ) : (
                <div>{amendment.development_status}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Priority</label>
              {editing ? (
                <select name="priority" value={formData.priority} onChange={handleChange}>
                  {priorities.map(priority => (
                    <option key={priority} value={priority}>{priority}</option>
                  ))}
                </select>
              ) : (
                <div>{amendment.priority}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Force</label>
              {editing ? (
                <select name="force" value={formData.force || ''} onChange={handleChange}>
                  <option value="">None</option>
                  {forces.map(force => (
                    <option key={force} value={force}>{force}</option>
                  ))}
                </select>
              ) : (
                <div>{amendment.force || 'N/A'}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Application</label>
              {editing ? (
                <input
                  type="text"
                  name="application"
                  value={formData.application || ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{amendment.application || 'N/A'}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Reported By</label>
              {editing ? (
                <input
                  type="text"
                  name="reported_by"
                  value={formData.reported_by || ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{amendment.reported_by || 'N/A'}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Assigned To</label>
              {editing ? (
                <input
                  type="text"
                  name="assigned_to"
                  value={formData.assigned_to || ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{amendment.assigned_to || 'N/A'}</div>
              )}
            </div>

            <div className="detail-field">
              <label>Date Reported</label>
              {editing ? (
                <input
                  type="datetime-local"
                  name="date_reported"
                  value={formData.date_reported ? new Date(formData.date_reported).toISOString().slice(0, 16) : ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{formatDate(amendment.date_reported)}</div>
              )}
            </div>
          </div>

          <div className="detail-field full-width">
            <label>Description</label>
            {editing ? (
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="4"
              />
            ) : (
              <div className="text-content">{amendment.description}</div>
            )}
          </div>

          <div className="detail-field full-width">
            <label>Notes</label>
            {editing ? (
              <textarea
                name="notes"
                value={formData.notes || ''}
                onChange={handleChange}
                rows="4"
              />
            ) : (
              <div className="text-content">{amendment.notes || 'N/A'}</div>
            )}
          </div>

          <div className="detail-field full-width">
            <label>Release Notes</label>
            {editing ? (
              <textarea
                name="release_notes"
                value={formData.release_notes || ''}
                onChange={handleChange}
                rows="4"
              />
            ) : (
              <div className="text-content">{amendment.release_notes || 'N/A'}</div>
            )}
          </div>

          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                name="database_changes"
                checked={editing ? formData.database_changes : amendment.database_changes}
                onChange={handleChange}
                disabled={!editing}
              />
              Database Changes
            </label>
            <label>
              <input
                type="checkbox"
                name="db_upgrade_changes"
                checked={editing ? formData.db_upgrade_changes : amendment.db_upgrade_changes}
                onChange={handleChange}
                disabled={!editing}
              />
              DB Upgrade Changes
            </label>
          </div>
        </div>

        <div className="detail-section">
          <h2>QA Information</h2>
          <div className="detail-grid">
            <div className="detail-field">
              <label>QA Assigned</label>
              {editing ? (
                <select
                  name="qa_assigned_id"
                  value={formData.qa_assigned_id || ''}
                  onChange={handleChange}
                >
                  <option value="">Not Assigned</option>
                  {employees.map(emp => (
                    <option key={emp.employee_id} value={emp.employee_id}>
                      {emp.employee_name}
                    </option>
                  ))}
                </select>
              ) : (
                <div>
                  {amendment.qa_assigned_id
                    ? employees.find(e => e.employee_id === amendment.qa_assigned_id)?.employee_name || 'Unknown'
                    : 'Not Assigned'}
                </div>
              )}
            </div>

            <div className="detail-field">
              <label>QA Assigned Date</label>
              {editing ? (
                <input
                  type="datetime-local"
                  name="qa_assigned_date"
                  value={formData.qa_assigned_date ? new Date(formData.qa_assigned_date).toISOString().slice(0, 16) : ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{formatDate(amendment.qa_assigned_date)}</div>
              )}
            </div>

            <div className="detail-field">
              <label>QA Signature</label>
              {editing ? (
                <input
                  type="text"
                  name="qa_signature"
                  value={formData.qa_signature || ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{amendment.qa_signature || 'N/A'}</div>
              )}
            </div>

            <div className="detail-field">
              <label>QA Completed Date</label>
              {editing ? (
                <input
                  type="datetime-local"
                  name="qa_completed_date"
                  value={formData.qa_completed_date ? new Date(formData.qa_completed_date).toISOString().slice(0, 16) : ''}
                  onChange={handleChange}
                />
              ) : (
                <div>{formatDate(amendment.qa_completed_date)}</div>
              )}
            </div>
          </div>

          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                name="qa_test_plan_check"
                checked={editing ? formData.qa_test_plan_check : amendment.qa_test_plan_check}
                onChange={handleChange}
                disabled={!editing}
              />
              Test Plan Checked
            </label>
            <label>
              <input
                type="checkbox"
                name="qa_test_release_notes_check"
                checked={editing ? formData.qa_test_release_notes_check : amendment.qa_test_release_notes_check}
                onChange={handleChange}
                disabled={!editing}
              />
              Release Notes Checked
            </label>
            <label>
              <input
                type="checkbox"
                name="qa_completed"
                checked={editing ? formData.qa_completed : amendment.qa_completed}
                onChange={handleChange}
                disabled={!editing}
              />
              QA Completed
            </label>
          </div>

          <div className="detail-field full-width">
            <label>QA Test Plan Link</label>
            {editing ? (
              <input
                type="text"
                name="qa_test_plan_link"
                value={formData.qa_test_plan_link || ''}
                onChange={handleChange}
                placeholder="https://"
              />
            ) : (
              <div>
                {amendment.qa_test_plan_link ? (
                  <a href={amendment.qa_test_plan_link} target="_blank" rel="noopener noreferrer">
                    {amendment.qa_test_plan_link}
                  </a>
                ) : (
                  'N/A'
                )}
              </div>
            )}
          </div>

          <div className="detail-field full-width">
            <label>QA Notes</label>
            {editing ? (
              <textarea
                name="qa_notes"
                value={formData.qa_notes || ''}
                onChange={handleChange}
                rows="4"
              />
            ) : (
              <div className="text-content">{amendment.qa_notes || 'N/A'}</div>
            )}
          </div>
        </div>

        <div className="detail-section">
          <h2>Progress History</h2>
          {amendment.progress_entries && amendment.progress_entries.length > 0 ? (
            <div className="progress-list">
              {amendment.progress_entries.map(entry => (
                <div key={entry.amendment_progress_id} className="progress-entry">
                  <div className="progress-header">
                    <strong>{entry.description}</strong>
                    <span className="progress-date">{formatDate(entry.created_on)}</span>
                  </div>
                  {entry.notes && <div className="progress-notes">{entry.notes}</div>}
                  {entry.created_by && <div className="progress-meta">By: {entry.created_by}</div>}
                </div>
              ))}
            </div>
          ) : (
            <p>No progress entries yet.</p>
          )}
        </div>

        <div className="detail-section">
          <h2>Metadata</h2>
          <div className="detail-grid">
            <div className="detail-field">
              <label>Created On</label>
              <div>{formatDate(amendment.created_on)}</div>
            </div>
            <div className="detail-field">
              <label>Created By</label>
              <div>{amendment.created_by || 'N/A'}</div>
            </div>
            <div className="detail-field">
              <label>Modified On</label>
              <div>{formatDate(amendment.modified_on)}</div>
            </div>
            <div className="detail-field">
              <label>Modified By</label>
              <div>{amendment.modified_by || 'N/A'}</div>
            </div>
          </div>
        </div>
      </div>

      {showProgressModal && (
        <div className="modal-overlay" onClick={() => setShowProgressModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Add Progress Update</h2>
            <div className="modal-body">
              <div className="form-field">
                <label>Description *</label>
                <input
                  type="text"
                  value={progressData.description}
                  onChange={(e) => setProgressData({...progressData, description: e.target.value})}
                  placeholder="Brief description of progress"
                />
              </div>
              <div className="form-field">
                <label>Notes</label>
                <textarea
                  value={progressData.notes}
                  onChange={(e) => setProgressData({...progressData, notes: e.target.value})}
                  placeholder="Additional details"
                  rows="4"
                />
              </div>
              <div className="form-field">
                <label>Date</label>
                <input
                  type="datetime-local"
                  value={progressData.start_date}
                  onChange={(e) => setProgressData({...progressData, start_date: e.target.value})}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={handleAddProgress}>Add Progress</button>
              <button className="btn btn-secondary" onClick={() => setShowProgressModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AmendmentDetail;
