import React from 'react';

export default function SummaryCards({ sets }) {
  const uniqueSets = sets.length;
  // Assuming all sets have quantity 1 for now unless tracked otherwise. 
  // If user wants to track quantity, we'd sum it. We'll just use length for now.
  const physicalBoxes = sets.length; 
  const completed = sets.filter(s => s.status === 'Done').length;
  const notStarted = sets.filter(s => s.status === 'Not Started').length;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Unique Sets</div>
        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{uniqueSets}</div>
      </div>
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Physical Boxes</div>
        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{physicalBoxes}</div>
      </div>
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Completed</div>
        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent-green)' }}>{completed}</div>
      </div>
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Not Started</div>
        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-secondary)' }}>{notStarted}</div>
      </div>
    </div>
  );
}
