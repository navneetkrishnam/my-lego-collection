import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

export default function PartDetailPage({ sets }) {
  const { name } = useParams();
  const navigate = useNavigate();
  const decodedName = decodeURIComponent(name);

  const [shape, setShape] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/parts-index.json`)
      .then(res => res.json())
      .then(data => {
        const found = data.find(s => s.name === decodedName);
        setShape(found);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load parts index", err);
        setLoading(false);
      });
  }, [decodedName]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
        <div style={{ display: 'inline-block', width: '40px', height: '40px', border: '4px solid var(--glass-border)', borderTopColor: 'var(--accent-blue)', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '1rem' }} />
        <h2>Loading Part Details...</h2>
      </div>
    );
  }

  if (!shape) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Shape Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>We couldn't find a piece with the name "{decodedName}".</p>
        <button onClick={() => navigate('/parts')} className="btn btn-primary">Back to Parts Database</button>
      </div>
    );
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      <button 
        onClick={() => navigate('/parts')}
        style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1rem', padding: '0', marginBottom: '2rem', fontWeight: 500 }}
        onMouseEnter={e => e.currentTarget.style.color = 'var(--text-primary)'}
        onMouseLeave={e => e.currentTarget.style.color = 'var(--text-secondary)'}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
        Back to Database
      </button>

      <div style={{ marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>{shape.name}</h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)' }}>
          Available in <strong>{shape.variants.length}</strong> color {shape.variants.length === 1 ? 'variant' : 'variants'} across your collection.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {shape.variants.map((variant) => (
          <div key={variant.id} style={{ 
            background: 'var(--bg-surface)', 
            border: '1px solid var(--glass-border)', 
            borderRadius: '16px', 
            padding: '2rem',
            display: 'flex',
            gap: '2rem',
            alignItems: 'flex-start',
            flexWrap: 'wrap'
          }}>
            {/* Variant Image & ID */}
            <div style={{ 
              background: 'var(--img-bg)', 
              borderRadius: '12px', 
              padding: '1.5rem',
              width: '200px',
              flexShrink: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              border: '1px solid var(--glass-border)'
            }}>
              <img 
                src={variant.imageUrl} 
                alt={`${shape.name} - ${variant.id}`} 
                style={{ width: '100%', height: '140px', objectFit: 'contain', mixBlendMode: 'multiply', marginBottom: '1rem' }} 
              />
              <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--accent-blue)', background: 'var(--glass-bg)', padding: '0.25rem 0.75rem', borderRadius: '12px' }}>
                ID: {variant.id}
              </span>
            </div>

            {/* Sets that use this exact variant */}
            <div style={{ flexGrow: 1, minWidth: '280px' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                Found in {variant.sets.length} {variant.sets.length === 1 ? 'Set' : 'Sets'}
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {variant.sets.map(setId => {
                  const setInfo = sets.find(s => s.id === setId);
                  return (
                    <Link 
                      key={setId} 
                      to={`/set/${setId}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        background: 'var(--glass-bg)',
                        border: '1px solid var(--glass-border)',
                        padding: '0.75rem',
                        borderRadius: '12px',
                        textDecoration: 'none',
                        color: 'var(--text-primary)',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={e => {
                        e.currentTarget.style.background = 'var(--bg-surface-hover)';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.borderColor = 'var(--accent-blue)';
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.background = 'var(--glass-bg)';
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.borderColor = 'var(--glass-border)';
                      }}
                    >
                      {setInfo?.thumbnail ? (
                        <img 
                          src={`${import.meta.env.BASE_URL}${setInfo.thumbnail.replace(/^\//, '')}`} 
                          alt={setInfo.name} 
                          style={{ width: '48px', height: '48px', objectFit: 'cover', borderRadius: '6px' }}
                        />
                      ) : (
                        <div style={{ width: '48px', height: '48px', background: 'var(--bg-base)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                        </div>
                      )}
                      
                      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-blue)' }}>Set #{setId}</span>
                        <span style={{ fontSize: '0.875rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {setInfo ? setInfo.name : 'Loading...'}
                        </span>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
