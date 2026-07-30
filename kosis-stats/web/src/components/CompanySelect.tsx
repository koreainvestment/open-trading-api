import { useState, useEffect } from 'react';
import { getFieldValue } from '../types';
import type { Company } from '../types';
import { apiRequest } from '../api';

interface CompanySelectProps {
  onSelect: (company: Company | null) => void;
  selectedCompany: Company | null;
  placeholder?: string;
}

export function CompanySelect({ onSelect, selectedCompany, placeholder = "Search company..." }: CompanySelectProps) {
  const [query, setQuery] = useState('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Sync internal query with selected company if needed
  useEffect(() => {
    if (selectedCompany) {
      const name = getFieldValue<string>(selectedCompany as unknown as Record<string, unknown>, "CorpName", "corp_name", "name") || "";
      setQuery(name);
    } else {
       // Only clear query if we don't have an active search intent? 
       // Actually, keeping query helps if user just deselected. 
       // But if external force cleared selection, maybe we should clear query or keep it?
       // For now, let's strictly sync only when selected.
    }
  }, [selectedCompany]);

  useEffect(() => {
    const fetchCompanies = async () => {
      setLoading(true);
      try {
        const endpoint = query
          ? `/companies?search=${encodeURIComponent(query)}`
          : "/companies";
        const data = await apiRequest<{ companies: Company[] } | Company[]>(endpoint);
        const list = Array.isArray(data) ? data : data.companies || [];
        setCompanies(list);
      } catch (err) {
        console.error(err);
        setCompanies([]);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(() => {
        fetchCompanies();
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="combobox-container">
      <input
        type="text"
        className="combobox-input"
        placeholder={placeholder}
        value={query}
        onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            if (!e.target.value) onSelect(null);
        }}
        onFocus={() => setIsOpen(true)}
        // Delay blur to allow click on list item
        onBlur={() => setTimeout(() => setIsOpen(false), 200)}
      />
      {isOpen && (
        <ul className="combobox-list">
          {loading ? (
             <li className="combobox-empty">Loading...</li>
          ) : companies.length === 0 ? (
            <li className="combobox-empty">No companies found</li>
          ) : (
            companies.map((company) => {
               const code = getFieldValue<string>(company as unknown as Record<string, unknown>, "CorpCode", "corp_code", "id") || "";
               const name = getFieldValue<string>(company as unknown as Record<string, unknown>, "CorpName", "corp_name", "name") || "";
               return (
                <li
                  key={code}
                  className={`combobox-item ${selectedCompany && getFieldValue(selectedCompany as unknown as Record<string, unknown>, "CorpCode", "corp_code") === code ? 'selected' : ''}`}
                  onClick={() => {
                    onSelect(company);
                    setQuery(name);
                    setIsOpen(false);
                  }}
                >
                  {name}
                </li>
               );
            })
          )}
        </ul>
      )}
    </div>
  );
}
