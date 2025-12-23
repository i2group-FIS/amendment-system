import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { amendmentAPI, referenceAPI, documentAPI } from '../services/api';
import './AmendmentCreate.css';

function AmendmentCreate() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Reference data
  const [types, setTypes] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [devStatuses, setDevStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [forces, setForces] = useState([]);

  // Form data
  const [formData, setFormData] = useState({
    amendment_type: 'Bug',
    description: '',
    amendment_status: 'Open',
    development_status: 'Not Started',
    priority: 'Medium',
    force: '',
    application: '',
    notes: '',
    reported_by: '',
    assigned_to: '',
    date_reported: new Date().toISOString().slice(0, 16),
    database_changes: false,
    db_upgrade_changes: false,
    release_notes: ''
  });

  // Document attachments
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    loadReferenceData();
  }, []);

  const loadReferenceData = async () => {
    try {
      const [typesRes, statusesRes, devStatusesRes, prioritiesRes, forcesRes] = await Promise.all([
        referenceAPI.getTypes(),
        referenceAPI.getStatuses(),
        referenceAPI.getDevelopmentStatuses(),
        referenceAPI.getPriorities(),
        referenceAPI.getForces(),
      ]);

      setTypes(typesRes.data);
      setStatuses(statusesRes.data);
      setDevStatuses(devStatusesRes.data);
      setPriorities(prioritiesRes.data);
      setForces(forcesRes.data);

      // Set initial values from reference data
      if (typesRes.data.length > 0) {
        setFormData(prev => ({ ...prev, amendment_type: typesRes.data[0] }));
      }
      if (statusesRes.data.length > 0) {
        setFormData(prev => ({ ...prev, amendment_status: statusesRes.data[0] }));
      }
      if (devStatusesRes.data.length > 0) {
        setFormData(prev => ({ ...prev, development_status: devStatusesRes.data[0] }));
      }
      if (prioritiesRes.data.length > 0) {
        setFormData(prev => ({ ...prev, priority: prioritiesRes.data[0] }));
      }
    } catch (err) {
      console.error('Failed to load reference data:', err);
      setError('Failed to load form options. Please try again.');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileAdd = (e) => {
    const files = Array.from(e.target.files);
    const newDocuments = files.map(file => ({
      file,
      document_name: file.name,
      document_type: 'Other',
      description: ''
    }));
    setDocuments(prev => [...prev, ...newDocuments]);
    e.target.value = ''; // Reset input to allow adding same file again
  };

  const handleDocumentChange = (index, field, value) => {
    setDocuments(prev => prev.map((doc, i) =>
      i === index ? { ...doc, [field]: value } : doc
    ));
  };

  const handleRemoveDocument = (index) => {
    setDocuments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      // Prepare data for API
      const submitData = {
        ...formData,
        force: formData.force || null,
        application: formData.application || null,
        notes: formData.notes || null,
        reported_by: formData.reported_by || null,
        assigned_to: formData.assigned_to || null,
        date_reported: formData.date_reported || null,
        release_notes: formData.release_notes || null,
      };

      const response = await amendmentAPI.create(submitData);
      const amendmentId = response.data.amendment_id;

      // Upload any attached documents
      if (documents.length > 0) {
        const uploadPromises = documents.map(doc => {
          const formData = new FormData();
          formData.append('file', doc.file);
          formData.append('document_name', doc.document_name);
          formData.append('document_type', doc.document_type);
          if (doc.description) {
            formData.append('description', doc.description);
          }
          return documentAPI.upload(amendmentId, formData);
        });

        try {
          await Promise.all(uploadPromises);
        } catch (docErr) {
          console.error('Failed to upload some documents:', docErr);
          // Continue to navigate even if document upload fails
        }
      }

      // Navigate to the newly created amendment
      navigate(`/amendments/${amendmentId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create amendment');
      setSaving(false);
    }
  };

  const handleCancel = () => {
    navigate('/amendments');
  };

  return (
    <div className="amendment-create">
      <div className="create-header">
        <h1>Create New Amendment</h1>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="create-form">
        <div className="form-section">
          <h2>Basic Information</h2>

          <div className="form-grid">
            <div className="form-field required">
              <label>Type</label>
              <select
                name="amendment_type"
                value={formData.amendment_type}
                onChange={handleChange}
                required
              >
                {types.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="form-field required">
              <label>Status</label>
              <select
                name="amendment_status"
                value={formData.amendment_status}
                onChange={handleChange}
                required
              >
                {statuses.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>

            <div className="form-field required">
              <label>Development Status</label>
              <select
                name="development_status"
                value={formData.development_status}
                onChange={handleChange}
                required
              >
                {devStatuses.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>

            <div className="form-field required">
              <label>Priority</label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                required
              >
                {priorities.map(priority => (
                  <option key={priority} value={priority}>{priority}</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Force</label>
              <select
                name="force"
                value={formData.force}
                onChange={handleChange}
              >
                <option value="">None</option>
                {forces.map(force => (
                  <option key={force} value={force}>{force}</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Application</label>
              <input
                type="text"
                name="application"
                value={formData.application}
                onChange={handleChange}
                placeholder="e.g., MyApp v1.0"
              />
            </div>

            <div className="form-field">
              <label>Reported By</label>
              <input
                type="text"
                name="reported_by"
                value={formData.reported_by}
                onChange={handleChange}
                placeholder="Name of reporter"
              />
            </div>

            <div className="form-field">
              <label>Assigned To</label>
              <input
                type="text"
                name="assigned_to"
                value={formData.assigned_to}
                onChange={handleChange}
                placeholder="Name of assignee"
              />
            </div>

            <div className="form-field">
              <label>Date Reported</label>
              <input
                type="datetime-local"
                name="date_reported"
                value={formData.date_reported}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-field full-width required">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="4"
              placeholder="Describe the amendment..."
              required
            />
          </div>

          <div className="form-field full-width">
            <label>Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows="4"
              placeholder="Additional notes or comments..."
            />
          </div>

          <div className="form-field full-width">
            <label>Release Notes</label>
            <textarea
              name="release_notes"
              value={formData.release_notes}
              onChange={handleChange}
              rows="4"
              placeholder="Notes for the release documentation..."
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Database Changes</h2>

          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                name="database_changes"
                checked={formData.database_changes}
                onChange={handleChange}
              />
              Database Changes Required
            </label>
            <label>
              <input
                type="checkbox"
                name="db_upgrade_changes"
                checked={formData.db_upgrade_changes}
                onChange={handleChange}
              />
              DB Upgrade Changes Required
            </label>
          </div>
        </div>

        <div className="form-section">
          <h2>Attach Documents (Optional)</h2>
          <p className="section-hint">Add screenshots, specifications, or other supporting documents</p>

          <div className="form-field">
            <label>Add Files</label>
            <input
              type="file"
              multiple
              onChange={handleFileAdd}
              accept="*/*"
            />
          </div>

          {documents.length > 0 && (
            <div className="documents-preview">
              <h3>Files to Upload ({documents.length})</h3>
              {documents.map((doc, index) => (
                <div key={index} className="document-preview-item">
                  <div className="doc-preview-header">
                    <strong>{doc.file.name}</strong>
                    <span className="doc-size">{(doc.file.size / 1024).toFixed(1)} KB</span>
                    <button
                      type="button"
                      className="btn-remove"
                      onClick={() => handleRemoveDocument(index)}
                    >
                      ×
                    </button>
                  </div>
                  <div className="doc-preview-fields">
                    <input
                      type="text"
                      placeholder="Document name"
                      value={doc.document_name}
                      onChange={(e) => handleDocumentChange(index, 'document_name', e.target.value)}
                    />
                    <select
                      value={doc.document_type}
                      onChange={(e) => handleDocumentChange(index, 'document_type', e.target.value)}
                    >
                      <option value="Test Plan">Test Plan</option>
                      <option value="Screenshot">Screenshot</option>
                      <option value="Specification">Specification</option>
                      <option value="Other">Other</option>
                    </select>
                    <input
                      type="text"
                      placeholder="Description (optional)"
                      value={doc.description}
                      onChange={(e) => handleDocumentChange(index, 'description', e.target.value)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Creating...' : 'Create Amendment'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleCancel}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default AmendmentCreate;
