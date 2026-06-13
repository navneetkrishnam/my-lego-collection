import React, { useState } from 'react';

export default function SetDetailsModal({ set, onClose, onAddHistory }) {
  const [builder, setBuilder] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  if (!set) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '2rem'
    }} onClick={onClose}>
      <div 
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '900px',
          maxHeight: '90vh',
          overflowY: 'auto',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          padding: '2rem',
          position: 'relative'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'var(--bg-surface-hover)',
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10
          }}
        >
          ✕
        </button>

        {/* Left Side: Images */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <img src={set.thumbnail} alt={set.name} style={{ width: '100%', borderRadius: '12px', objectFit: 'cover' }} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem' }}>
            {set.images && set.images.map((img, i) => (
              <img key={i} src={img} alt={`Preview ${i}`} style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', borderRadius: '8px' }} />
            ))}
          </div>
        </div>

        {/* Right Side: Details & History */}
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{set.name}</h2>
          <div style={{ color: 'var(--text-secondary)', fontSize: '1.125rem', marginBottom: '1.5rem' }}>
            Set #{set.id} • {set.pieces} pieces • {set.age} • {set.theme}
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.5rem' }}>Build History</h3>
            
            {set.history && set.history.length > 0 ? (
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {set.history.map((record, i) => (
                  <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                    <div style={{ background: 'var(--accent-blue)', width: '10px', height: '10px', borderRadius: '50%', marginTop: '6px' }}></div>
                    <div>
                      <div style={{ fontWeight: 600 }}>{record.date}</div>
                      <div style={{ color: 'var(--text-secondary)' }}>Built by: {record.builder}</div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div style={{ color: 'var(--text-tertiary)' }}>No builds recorded yet.</div>
            )}
          </div>

          <div style={{ background: 'var(--bg-surface)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
            <h4 style={{ marginBottom: '1rem' }}>Log a New Build</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Date</label>
                <input 
                  type="date" 
                  value={date}
                  onChange={e => setDate(e.target.value)}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-base)', color: 'white' }} 
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Builder Name(s)</label>
                <input 
                  type="text" 
                  value={builder}
                  onChange={e => setBuilder(e.target.value)}
                  placeholder="e.g. Navneet and Anirud"
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-base)', color: 'white' }} 
                />
              </div>
              <button 
                onClick={() => {
                  if (builder) {
                    onAddHistory(set.id, { date, builder });
                    setBuilder('');
                  }
                }}
                disabled={!builder}
                style={{
                  padding: '0.75rem',
                  borderRadius: '8px',
                  backgroundColor: builder ? 'var(--accent-blue)' : 'var(--bg-surface-hover)',
                  color: builder ? '#fff' : 'var(--text-tertiary)',
                  fontWeight: 600,
                  marginTop: '0.5rem'
                }}
              >
                Log Build
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
