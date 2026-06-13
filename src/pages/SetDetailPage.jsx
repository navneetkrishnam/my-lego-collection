import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CustomDatePicker from '../components/CustomDatePicker';
import MultiSelectDropdown from '../components/MultiSelectDropdown';

export default function SetDetailPage({ sets, onAddHistory, onEditHistory, onDeleteHistory }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const set = sets.find(s => s.id === id);
  const displayImages = set && set.images && set.images.length > 0 ? set.images.slice(0, 4) : [];

  const [builder, setBuilder] = useState([]);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isHoverZooming, setIsHoverZooming] = useState(false);
  const [zoomOrigin, setZoomOrigin] = useState({ x: 50, y: 50 });

  const handleMouseMove = (e) => {
    const { left, top, width, height } = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - left) / width) * 100;
    const y = ((e.clientY - top) / height) * 100;
    setZoomOrigin({ x, y });
  };

  const prevImage = (e) => {
    e.stopPropagation();
    if (displayImages.length === 0) return;
    setSelectedImageIndex((prev) => (prev === 0 ? displayImages.length - 1 : prev - 1));
  };

  const nextImage = (e) => {
    e.stopPropagation();
    if (displayImages.length === 0) return;
    setSelectedImageIndex((prev) => (prev === displayImages.length - 1 ? 0 : prev + 1));
  };

  const [editingIndex, setEditingIndex] = useState(null);
  const [editDate, setEditDate] = useState('');
  const [editBuilder, setEditBuilder] = useState([]);

  const handleEditClick = (index, record) => {
    setEditingIndex(index);
    setEditBuilder(record.builder ? record.builder.split(',').map(s => s.trim()) : []);
    setEditDate(record.date);
  };

  const handleSaveEdit = (index) => {
    if (editBuilder.length > 0) {
      onEditHistory(set.id, index, { builder: editBuilder.join(', '), date: editDate });
      setEditingIndex(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
  };

  const handleDelete = (index) => {
    if (window.confirm("Are you sure you want to delete this build record?")) {
      onDeleteHistory(set.id, index);
      if (editingIndex === index) setEditingIndex(null);
    }
  };

  const handleLogBuild = () => {
    if (builder.length > 0) {
      onAddHistory(set.id, { date, builder: builder.join(', ') });
      setBuilder([]);
    }
  };

  if (!set) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem' }}>
        <h2>Set not found</h2>
        <button onClick={() => navigate('/')} style={{ marginTop: '1rem', padding: '0.75rem 1.5rem', background: 'var(--accent-blue)', color: 'white', borderRadius: '8px' }}>
          Back to Collection
        </button>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ paddingBottom: '4rem' }}>

      <button 
        className="btn btn-secondary"
        onClick={() => navigate('/')}
        style={{ marginBottom: '2rem' }}
      >
        ← Back to Collection
      </button>

      <div 
        className="glass-panel"
        style={{
          width: '100%',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '3rem',
          padding: '3rem',
        }}
      >
        {/* Left Side: Images */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div 
            className="image-wrapper" 
            onMouseEnter={() => setIsHoverZooming(true)}
            onMouseLeave={() => setIsHoverZooming(false)}
            onMouseMove={handleMouseMove}
          >
            <img 
              src={displayImages.length > 0 ? displayImages[selectedImageIndex] : set.thumbnail} 
              alt={set.name} 
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'contain',
                transform: isHoverZooming ? 'scale(2.5)' : 'scale(1)',
                transformOrigin: `${zoomOrigin.x}% ${zoomOrigin.y}%`,
                pointerEvents: 'none' // Ensures the mouse events always fire on the wrapper
              }} 
            />
            {displayImages.length > 1 && (
              <>
                <div 
                  className="image-nav-btn image-nav-left" 
                  onClick={prevImage}
                  onMouseEnter={() => setIsHoverZooming(false)}
                  onMouseLeave={() => setIsHoverZooming(true)}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
                </div>
                <div 
                  className="image-nav-btn image-nav-right" 
                  onClick={nextImage}
                  onMouseEnter={() => setIsHoverZooming(false)}
                  onMouseLeave={() => setIsHoverZooming(true)}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </div>
              </>
            )}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem' }}>
            {displayImages.map((img, i) => (
              <img 
                key={i} 
                src={img} 
                alt={`Preview ${i}`} 
                onClick={() => setSelectedImageIndex(i)}
                style={{ 
                  width: '100%', 
                  aspectRatio: '1', 
                  objectFit: 'contain', 
                  borderRadius: '8px',
                  cursor: 'pointer',
                  border: selectedImageIndex === i ? '2px solid var(--accent-blue)' : '2px solid transparent',
                  opacity: selectedImageIndex === i ? 1 : 0.6,
                  transition: 'opacity 0.2s ease'
                }} 
              />
            ))}
          </div>
        </div>

        {/* Right Side: Details & History */}
        <div>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{set.name}</h2>
          <div style={{ color: 'var(--text-secondary)', fontSize: '1.125rem', marginBottom: '2rem' }}>
            Set #{set.id} • {set.pieces} pieces • {set.age} • {set.theme}
          </div>

          {/* Log a New Build Section (Moved to Top) */}
          <div style={{ background: 'var(--bg-base)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--glass-border)', marginBottom: '3rem', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
            <h4 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: 'var(--accent-blue)' }}>+</span> Log a New Build
            </h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>Builders</label>
                <MultiSelectDropdown 
                  options={['Navneet', 'Miti', 'Anirud Krishna', 'Avyukt']}
                  selected={builder}
                  onChange={setBuilder}
                  placeholder="Select Builder(s)"
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '0.5rem' }}>
                  <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Date</label>
                </div>
                <CustomDatePicker 
                  date={date} 
                  onChange={setDate} 
                />
              </div>
            </div>

            <button 
              className="btn btn-primary"
              onClick={handleLogBuild}
              disabled={builder.length === 0}
              style={{ width: '100%', padding: '1rem', fontSize: '1.125rem' }}
            >
              Log Build to History
            </button>
          </div>

        </div>
      </div>

      {/* Build History Section (Moved completely below the main grid layout) */}
      <div style={{ marginTop: '4rem', paddingTop: '3rem', borderTop: '1px solid var(--glass-border)' }}>
        <h3 style={{ marginBottom: '2rem', fontSize: '1.75rem', color: 'var(--text-primary)' }}>Build History</h3>
        
        {set.history && set.history.length > 0 ? (
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: 0 }}>
            {set.history.map((record, i) => (
              <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '1.25rem', background: 'var(--glass-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                {editingIndex === i ? (
                  <div style={{ width: '100%' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Builders</label>
                        <MultiSelectDropdown 
                          options={['Navneet', 'Miti', 'Anirud Krishna', 'Avyukt']}
                          selected={editBuilder}
                          onChange={setEditBuilder}
                          placeholder="Select Builder(s)"
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Date</label>
                        <CustomDatePicker date={editDate} onChange={setEditDate} />
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                      <button className="btn btn-sm btn-secondary" onClick={handleCancelEdit}>Cancel</button>
                      <button className="btn btn-sm btn-primary" onClick={() => handleSaveEdit(i)}>Save Changes</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div style={{ background: 'var(--accent-blue)', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold', flexShrink: 0 }}>
                      {record.builder.charAt(0).toUpperCase()}
                    </div>
                    <div style={{ flexGrow: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '1.125rem', color: 'var(--text-primary)' }}>{record.builder}</div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Completed on {new Date(record.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button 
                        onClick={() => handleEditClick(i, record)} 
                        style={{ background: 'var(--bg-surface)', border: '1px solid var(--glass-border)', color: 'var(--text-secondary)', borderRadius: '6px', padding: '0.5rem', cursor: 'pointer', transition: 'all 0.2s' }} 
                        title="Edit"
                        onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.background = 'var(--bg-surface-hover)'; }}
                        onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.background = 'var(--bg-surface)'; }}
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                      </button>
                      <button 
                        onClick={() => handleDelete(i)} 
                        style={{ background: 'var(--bg-surface)', border: '1px solid var(--glass-border)', color: '#ff453a', borderRadius: '6px', padding: '0.5rem', cursor: 'pointer', transition: 'all 0.2s' }} 
                        title="Delete"
                        onMouseEnter={e => { e.currentTarget.style.background = '#ff453a'; e.currentTarget.style.color = '#fff'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-surface)'; e.currentTarget.style.color = '#ff453a'; }}
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <div style={{ color: 'var(--text-tertiary)', padding: '2rem', textAlign: 'center', background: 'var(--bg-base)', borderRadius: '8px', border: '1px dashed var(--glass-border)' }}>
            No builds recorded yet. Be the first to build!
          </div>
        )}
      </div>
    </div>
  );
}
