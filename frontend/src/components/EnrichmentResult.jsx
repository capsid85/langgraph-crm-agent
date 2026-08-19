import React from 'react';
import { Building2, Globe, Users, Briefcase, Database } from 'lucide-react';

const EnrichmentResult = ({ result }) => {
  if (!result || !result.data) return null;

  const { data, company_name, hubspot_company_id, status } = result;

  return (
    <div className="glass-card result-card">
      <div className="result-header">
        <h2>
          <Building2 size={24} color="var(--primary-color)" />
          {company_name}
        </h2>
        {hubspot_company_id ? (
          <span className="badge" title={`ID: ${hubspot_company_id}`}>
            Synced to HubSpot
          </span>
        ) : (
          <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#fca5a5' }}>
            {status === 'mock_mode' ? 'Mock CRM Write' : 'Sync Failed'}
          </span>
        )}
      </div>

      <div className="data-grid">
        <div className="data-item">
          <span className="data-label">
            <Globe size={14} style={{ display: 'inline', marginRight: '4px' }} />
            Domain
          </span>
          <span className="data-value">{data.domain || 'N/A'}</span>
        </div>

        <div className="data-item">
          <span className="data-label">
            <Briefcase size={14} style={{ display: 'inline', marginRight: '4px' }} />
            Industry
          </span>
          <span className="data-value">{data.industry || 'N/A'}</span>
        </div>

        <div className="data-item">
          <span className="data-label">
            <Users size={14} style={{ display: 'inline', marginRight: '4px' }} />
            Company Size
          </span>
          <span className="data-value">{data.size || 'N/A'}</span>
        </div>
      </div>

      <div className="news-section" style={{ borderTop: 'none', paddingTop: '0', marginTop: '1.5rem' }}>
        <div className="data-item">
          <span className="data-label">
            <Database size={14} style={{ display: 'inline', marginRight: '4px' }} />
            Tech Stack
          </span>
          <div className="tech-stack">
            {data.tech_stack && data.tech_stack.length > 0 ? (
              data.tech_stack.map((tech, index) => (
                <span key={index} className="tech-tag">{tech}</span>
              ))
            ) : (
              <span className="data-value" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Not identified</span>
            )}
          </div>
        </div>
      </div>

      {data.recent_news && (
        <div className="news-section">
          <span className="data-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Recent News & Signals</span>
          <p>{data.recent_news}</p>
        </div>
      )}
    </div>
  );
};

export default EnrichmentResult;
