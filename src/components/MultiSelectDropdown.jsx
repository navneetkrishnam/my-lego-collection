import React, { useState, useEffect, useRef } from 'react';

export default function MultiSelectDropdown({ options, selected, onChange, placeholder = "Select options" }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleOption = (option) => {
    if (selected.includes(option)) {
      onChange(selected.filter(item => item !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <div 
        className="form-control" 
        onClick={() => setIsOpen(!isOpen)}
        style={{ 
          cursor: 'pointer', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          minHeight: '2.5rem'
        }}
      >
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: selected.length === 0 ? 'var(--text-tertiary)' : 'inherit' }}>
          {selected.length > 0 ? selected.join(', ') : placeholder}
        </span>
        <svg 
          style={{ 
            color: 'var(--text-tertiary)', 
            transform: isOpen ? 'rotate(180deg)' : 'none', 
            transition: 'transform 0.2s ease',
            flexShrink: 0,
            marginLeft: '0.5rem'
          }} 
          width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
      
      {isOpen && (
        <div 
          className="animate-fade-in"
          style={{
            position: 'absolute', 
            top: '100%', 
            left: 0, 
            right: 0, 
            marginTop: '0.25rem',
            background: 'var(--bg-surface)', 
            border: '1px solid var(--glass-border)',
            borderRadius: '8px', 
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)', 
            zIndex: 100,
            maxHeight: '200px', 
            overflowY: 'auto', 
            padding: '0.5rem'
          }}
        >
          {options.map(option => (
            <label 
              key={option} 
              style={{
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem', 
                padding: '0.5rem',
                cursor: 'pointer', 
                borderRadius: '4px', 
                transition: 'background 0.2s ease',
                fontSize: '0.875rem'
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-surface-hover)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <input 
                type="checkbox" 
                checked={selected.includes(option)}
                onChange={() => toggleOption(option)}
                style={{ cursor: 'pointer', width: '16px', height: '16px' }}
              />
              {option}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
