import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

const SearchForm = ({ onSubmit, isLoading }) => {
  const [companyName, setCompanyName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (companyName.trim()) {
      onSubmit(companyName.trim());
    }
  };

  return (
    <div className="glass-card">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <label htmlFor="companyName">Target Company</label>
          <input
            id="companyName"
            type="text"
            className="input-field"
            placeholder="e.g., OpenAI, Stripe, Vercel..."
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            disabled={isLoading}
            autoComplete="off"
            required
          />
        </div>
        <button type="submit" className="submit-btn" disabled={isLoading || !companyName.trim()}>
          {isLoading ? (
            <>
              <Loader2 size={20} className="spin" />
              Enriching Record...
            </>
          ) : (
            <>
              <Search size={20} />
              Enrich Company
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;
