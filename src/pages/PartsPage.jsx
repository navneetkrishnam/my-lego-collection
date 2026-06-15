import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';

export default function PartsPage() {
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [visibleCount, setVisibleCount] = useState(100);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/parts-index.json`)
      .then(res => res.json())
      .then(data => {
        setParts(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load parts index", err);
        setLoading(false);
      });
  }, []);

  const filteredParts = useMemo(() => {
    if (!searchQuery) return parts;
    const lowerQuery = searchQuery.toLowerCase();
    return parts.filter(p => 
      p.id.toLowerCase().includes(lowerQuery) || 
      p.name.toLowerCase().includes(lowerQuery)
    );
  }, [parts, searchQuery]);

  const visibleParts = filteredParts.slice(0, visibleCount);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
        <div style={{ display: 'inline-block', width: '40px', height: '40px', border: '4px solid var(--glass-border)', borderTopColor: 'var(--accent-blue)', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '1rem' }} />
        <h2>Loading Global Parts Database...</h2>
      </div>
    );
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Parts Database</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Viewing {filteredParts.length} unique pieces across your entire collection.
          </p>
        </div>
        
        <div style={{ position: 'relative', width: '100%', maxWidth: '400px' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }}><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            type="text" 
            placeholder="Search by part name or ID..." 
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setVisibleCount(100); // Reset pagination on search
            }}
            className="search-input"
            style={{
              width: '100%',
              padding: '1rem 1rem 1rem 3rem',
              borderRadius: '24px',
              border: '1px solid var(--glass-border)',
              background: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              fontSize: '1rem',
              outline: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              transition: 'all 0.2s'
            }}
            onFocus={e => e.target.style.border = '1px solid var(--accent-blue)'}
            onBlur={e => e.target.style.border = '1px solid var(--glass-border)'}
          />
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '1.5rem'
      }}>
        {visibleParts.map((part) => (
          <div key={part.id} style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--glass-border)',
            borderRadius: '16px',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            transition: 'transform 0.2s, box-shadow 0.2s',
            boxShadow: '0 4px 6px rgba(0,0,0,0.02)'
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 12px 20px rgba(0,0,0,0.08)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = 'none';
            e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.02)';
          }}
          >
            <div style={{ height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <img 
                src={part.imageUrl} 
                alt={part.name} 
                style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', mixBlendMode: 'multiply' }}
                loading="lazy"
              />
            </div>
            
            <div style={{ flexGrow: 1 }}>
              <span style={{ fontSize: '0.875rem', color: 'var(--accent-blue)', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
                #{part.id}
              </span>
              <h4 style={{ fontSize: '1rem', color: 'var(--text-primary)', margin: '0 0 1rem 0', lineHeight: 1.3, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }} title={part.name}>
                {part.name}
              </h4>
            </div>

            <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1rem', marginTop: 'auto' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>USED IN SETS:</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {part.sets.map(setId => (
                  <Link 
                    key={setId} 
                    to={`/set/${setId}`}
                    style={{
                      background: 'var(--glass-bg)',
                      border: '1px solid var(--glass-border)',
                      color: 'var(--text-primary)',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                      textDecoration: 'none',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background = 'var(--accent-blue)';
                      e.currentTarget.style.color = '#fff';
                      e.currentTarget.style.borderColor = 'var(--accent-blue)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = 'var(--glass-bg)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                      e.currentTarget.style.borderColor = 'var(--glass-border)';
                    }}
                  >
                    {setId}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {visibleCount < filteredParts.length && (
        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
          <button 
            className="btn btn-secondary"
            onClick={() => setVisibleCount(c => c + 100)}
            style={{ padding: '0.75rem 2rem', fontSize: '1rem', borderRadius: '24px' }}
          >
            Load More Pieces
          </button>
        </div>
      )}
      
      {filteredParts.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem', opacity: 0.5 }}><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <h3>No parts found</h3>
          <p>Try a different search term or part ID.</p>
        </div>
      )}
    </div>
  );
}
