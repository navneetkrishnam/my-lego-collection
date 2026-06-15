import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';

export default function PartsPage() {
  const [shapes, setShapes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [visibleCount, setVisibleCount] = useState(100);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/parts-index.json`)
      .then(res => res.json())
      .then(data => {
        setShapes(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load parts index", err);
        setLoading(false);
      });
  }, []);

  const filteredShapes = useMemo(() => {
    if (!searchQuery) return shapes;
    const lowerQuery = searchQuery.toLowerCase();
    return shapes.filter(s => 
      s.name.toLowerCase().includes(lowerQuery) || 
      // Also match by specific variant ID if the user searches for an exact color piece
      s.variants.some(v => v.id.toLowerCase().includes(lowerQuery))
    );
  }, [shapes, searchQuery]);

  const visibleShapes = filteredShapes.slice(0, visibleCount);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
        <div style={{ display: 'inline-block', width: '40px', height: '40px', border: '4px solid var(--glass-border)', borderTopColor: 'var(--accent-blue)', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '1rem' }} />
        <h2>Loading Global Shape Database...</h2>
      </div>
    );
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Parts Database</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Viewing {filteredShapes.length} unique shapes/molds across your collection.
          </p>
        </div>
        
        <div style={{ position: 'relative', width: '100%', maxWidth: '400px' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }}><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            type="text" 
            placeholder="Search by part name or exact ID..." 
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setVisibleCount(100);
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
        gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
        gap: '1.5rem'
      }}>
        {visibleShapes.map((shape) => (
          <Link 
            key={shape.name}
            to={`/part/${encodeURIComponent(shape.name)}`}
            style={{ textDecoration: 'none' }}
          >
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--glass-border)',
              borderRadius: '16px',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
              transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s',
              boxShadow: '0 4px 6px rgba(0,0,0,0.02)',
              cursor: 'pointer'
            }}
            onMouseEnter={e => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 12px 20px rgba(0,0,0,0.08)';
              e.currentTarget.style.borderColor = 'var(--accent-blue)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = 'none';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.02)';
              e.currentTarget.style.borderColor = 'var(--glass-border)';
            }}
            >
              <div style={{ height: '140px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem', background: 'var(--img-bg)', borderRadius: '8px' }}>
                {/* Just show the first variant's image as the hero image for this shape */}
                <img 
                  src={shape.variants[0].imageUrl} 
                  alt={shape.name} 
                  style={{ maxWidth: '80%', maxHeight: '80%', objectFit: 'contain', mixBlendMode: 'multiply' }}
                  loading="lazy"
                />
                
                {shape.variants.length > 1 && (
                  <div style={{ position: 'absolute', top: '0.5rem', right: '0.5rem', background: 'rgba(0,0,0,0.7)', color: '#fff', fontSize: '0.75rem', fontWeight: 600, padding: '0.2rem 0.5rem', borderRadius: '12px', backdropFilter: 'blur(4px)' }}>
                    +{shape.variants.length - 1} colors
                  </div>
                )}
              </div>
              
              <div style={{ flexGrow: 1 }}>
                <h4 style={{ fontSize: '1.125rem', color: 'var(--text-primary)', margin: '0 0 0.5rem 0', lineHeight: 1.3, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }} title={shape.name}>
                  {shape.name}
                </h4>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--glass-border)', paddingTop: '1rem', marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                  {shape.totalSetsCount} Sets
                </span>
                <span style={{ fontSize: '0.875rem', color: 'var(--accent-blue)', fontWeight: 600 }}>
                  View details &rarr;
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {visibleCount < filteredShapes.length && (
        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
          <button 
            className="btn btn-secondary"
            onClick={() => setVisibleCount(c => c + 100)}
            style={{ padding: '0.75rem 2rem', fontSize: '1rem', borderRadius: '24px' }}
          >
            Load More Shapes
          </button>
        </div>
      )}
      
      {filteredShapes.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem', opacity: 0.5 }}><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <h3>No shapes found</h3>
          <p>Try a different search term or part ID.</p>
        </div>
      )}
    </div>
  );
}
