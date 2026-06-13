import React, { useState } from 'react';

export default function SetCard({ set, onClick, onMarkAsDone }) {
  const [isHovered, setIsHovered] = useState(false);

  const getThemeClass = (theme) => {
    switch (theme) {
      case 'City': return 'badge-city';
      case 'Friends': return 'badge-friends';
      case 'Creator': return 'badge-creator';
      case 'Adult Sets': return 'badge-adult';
      case 'Classic': return 'badge-classic';
      default: return 'badge-misc';
    }
  };

  return (
    <div 
      className="glass-panel"
      style={{
        height: '100%',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        boxShadow: isHovered ? '0 12px 40px 0 rgba(0,0,0,0.45)' : 'var(--glass-shadow)',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >


      <div style={{ height: '200px', width: '100%', marginBottom: '1rem', overflow: 'hidden', borderRadius: '8px' }}>
        <img 
          src={set.thumbnail ? `${import.meta.env.BASE_URL}${set.thumbnail.replace(/^\//, '')}` : ''} 
          alt={set.name} 
          style={{ 
            width: '100%', 
            height: '100%', 
            objectFit: 'contain',
            transition: 'transform 0.5s ease',
            transform: isHovered ? 'scale(1.05)' : 'scale(1)'
          }} 
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem', width: '100%' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span className={`badge ${getThemeClass(set.theme)}`}>{set.theme}</span>
          <span className="badge" style={{ background: 'var(--bg-surface-hover)', color: 'var(--text-secondary)', border: '1px solid var(--glass-border)' }}>{set.age}</span>
        </div>
        {set.status === 'Done' && (
          <span className="badge" style={{ backgroundColor: 'var(--accent-green)', color: '#fff', border: 'none', marginLeft: 'auto' }}>
            DONE
          </span>
        )}
      </div>

      <h3 style={{ 
        fontSize: '1.25rem', 
        marginBottom: '0.25rem',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
      }}>
        {set.name}
      </h3>
      <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>#{set.id} • {set.pieces} pieces</span>
        <a 
          href={`https://www.lego.com/en-us/product/-${set.id}`} 
          target="_blank" 
          rel="noreferrer"
          style={{
            background: 'transparent',
            color: '#E3000B',
            textDecoration: 'underline',
            fontSize: '0.8rem',
            fontWeight: 700,
            transition: 'opacity 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.target.style.opacity = '0.8';
          }}
          onMouseLeave={(e) => {
            e.target.style.opacity = '1';
          }}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            window.open(`https://www.lego.com/en-us/product/-${set.id}`, '_blank');
          }}
        >
          More Info
        </a>
      </div>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
            style={{
              flex: 1,
              padding: '0.75rem 0.5rem',
              borderRadius: '8px',
              backgroundColor: 'var(--bg-surface-hover)',
              color: 'var(--text-primary)',
              border: '1px solid var(--glass-border)',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = 'var(--bg-surface)'}
            onMouseLeave={(e) => e.target.style.backgroundColor = 'var(--bg-surface-hover)'}
          >
            View Details
          </button>
          
          <button 
            onClick={(e) => {
              e.stopPropagation();
              onMarkAsDone();
            }}
            style={{
              flex: 1,
              padding: '0.75rem 0.5rem',
              borderRadius: '8px',
              backgroundColor: 'var(--accent-blue)',
              color: '#fff',
              border: 'none',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'var(--accent-blue-hover)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'var(--accent-blue)';
            }}
          >
            Log Build
          </button>
        </div>
      </div>
    </div>
  );
}
