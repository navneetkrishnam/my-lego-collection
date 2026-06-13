import React from 'react';

export default function FilterSidebar({ filters, setFilters, themeOptions = [], ageOptions = [] }) {
  const SECTIONS = [
    {
      id: 'status',
      title: 'Status',
      options: ['Not Started', 'Completed']
    },
    {
      id: 'theme',
      title: 'Theme',
      options: themeOptions
    },
    {
      id: 'age',
      title: 'Age',
      options: ageOptions
    },
    {
      id: 'pieces',
      title: 'Pieces',
      options: ['< 500 pcs', '500-1000 pcs', '1000-2000 pcs', '2000+ pcs']
    }
  ];

  const toggleFilter = (sectionId, option) => {
    setFilters(prev => {
      const current = prev[sectionId];
      if (current.includes(option)) {
        return { ...prev, [sectionId]: current.filter(o => o !== option) };
      } else {
        return { ...prev, [sectionId]: [...current, option] };
      }
    });
  };

  const resetAll = (e) => {
    e.preventDefault();
    setFilters({
      status: [],
      theme: [],
      age: [],
      pieces: []
    });
  };

  const selectAll = (e, sectionId, options) => {
    e.preventDefault();
    setFilters(prev => ({ ...prev, [sectionId]: [...options] }));
  };

  const clearSection = (e, sectionId) => {
    e.preventDefault();
    setFilters(prev => ({ ...prev, [sectionId]: [] }));
  };

  const hasAnyFilter = Object.values(filters).some(arr => arr.length > 0);

  return (
    <div style={{
      width: '250px',
      flexShrink: 0,
      display: 'flex',
      flexDirection: 'column',
      gap: '2.5rem',
      paddingRight: '1.5rem',
      borderRight: '1px solid var(--glass-border)',
      height: 'fit-content'
    }}>

      {SECTIONS.map(section => (
        <div key={section.id}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>
              {section.title}
            </h4>
            {filters[section.id].length === section.options.length ? (
              <button 
                onClick={(e) => clearSection(e, section.id)}
                style={{ background: 'none', border: 'none', color: 'var(--accent-blue)', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
              >
                Clear
              </button>
            ) : (
              <button 
                onClick={(e) => selectAll(e, section.id, section.options)}
                style={{ background: 'none', border: 'none', color: 'var(--accent-blue)', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
              >
                Select All
              </button>
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {section.options.map(option => {
              const isChecked = filters[section.id].includes(option);
              return (
                <label 
                  key={option} 
                  onClick={(e) => {
                    e.preventDefault();
                    toggleFilter(section.id, option);
                  }}
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.75rem', 
                    cursor: 'pointer', 
                    fontSize: '0.95rem', 
                    fontWeight: isChecked ? 600 : 400,
                    color: isChecked ? 'var(--text-primary)' : 'var(--text-secondary)',
                    transition: 'color 0.2s'
                  }}
                  onMouseEnter={(e) => { if (!isChecked) e.target.style.color = 'var(--text-primary)'; }}
                  onMouseLeave={(e) => { if (!isChecked) e.target.style.color = 'var(--text-secondary)'; }}
                >
                  <div 
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '6px',
                      border: isChecked ? 'none' : '2px solid var(--glass-border)',
                      background: isChecked ? 'var(--accent-blue)' : 'var(--bg-surface)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s',
                      boxShadow: isChecked ? '0 2px 8px rgba(10,132,255,0.3)' : 'none'
                    }}
                  >
                    {isChecked && (
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    )}
                  </div>
                  {option}
                </label>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
