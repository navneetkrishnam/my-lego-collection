import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import CustomDatePicker from '../components/CustomDatePicker';
import MultiSelectDropdown from '../components/MultiSelectDropdown';
import { calculateETA } from '../utils/eta';

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

  const [parts, setParts] = useState(null);
  const [partsLoading, setPartsLoading] = useState(true);

  const [isPartsExpanded, setIsPartsExpanded] = useState(false);
  const [isHistoryExpanded, setIsHistoryExpanded] = useState(true);

  React.useEffect(() => {
    if (set) {
      setPartsLoading(true);
      fetch(`${import.meta.env.BASE_URL}data/parts/${set.id}.json`)
        .then(res => {
          if (!res.ok) throw new Error("Not found");
          return res.json();
        })
        .then(data => {
          setParts(data);
          setPartsLoading(false);
        })
        .catch(() => {
          setParts(null);
          setPartsLoading(false);
        });
    }
  }, [set]);

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

      <div className="glass-panel set-detail-grid">
        {/* Left Side: Images */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div 
            className="image-wrapper" 
            onMouseEnter={() => setIsHoverZooming(true)}
            onMouseLeave={() => setIsHoverZooming(false)}
            onMouseMove={handleMouseMove}
          >
            <img 
              src={displayImages.length > 0 ? `${import.meta.env.BASE_URL}${displayImages[selectedImageIndex].replace(/^\//, '')}` : (set.thumbnail ? `${import.meta.env.BASE_URL}${set.thumbnail.replace(/^\//, '')}` : '')} 
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
                src={img ? `${import.meta.env.BASE_URL}${img.replace(/^\//, '')}` : ''} 
                alt={`Preview ${i}`} 
                onClick={() => setSelectedImageIndex(i)}
                style={{ 
                  width: '100%', 
                  aspectRatio: '1', 
                  objectFit: 'contain', 
                  borderRadius: '8px',
                  cursor: 'pointer',
                  border: selectedImageIndex === i ? '2px solid var(--accent-blue)' : '2px solid transparent',
                  background: 'var(--img-bg)',
                  opacity: selectedImageIndex === i ? 1 : 0.6,
                  transition: 'opacity 0.2s ease'
                }} 
              />
            ))}
          </div>
        </div>

        {/* Right Side: Details & History */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '0.5rem' }}>
              <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{set.name}</h2>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
                {/* Product Page Button (Icon Only) */}
                <a 
                  href={`https://www.lego.com/en-us/product/-${set.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ 
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: 'var(--accent-yellow)',
                    padding: '0.6rem', borderRadius: '50%', 
                    border: '1px solid var(--accent-yellow)',
                    textDecoration: 'none', transition: 'all 0.2s ease',
                    background: 'transparent'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = 'rgba(255, 213, 0, 0.1)';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                  title="View product details on Lego.com"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                </a>

                {/* Parts Button (Icon Only) */}
                <a 
                  href={`https://www.lego.com/en-in/service/replacement-parts/missing/${set.id}/pieces?search=*`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ 
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: '#bf5af2',
                    padding: '0.6rem', borderRadius: '50%', 
                    border: '1px solid #bf5af2',
                    textDecoration: 'none', transition: 'all 0.2s ease',
                    background: 'transparent'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = 'rgba(191, 90, 242, 0.1)';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                  title="View individual pieces on Lego.com"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>
                </a>
              </div>
            </div>
            
            <div style={{ color: 'var(--text-secondary)', fontSize: '1.125rem', marginBottom: '2rem' }}>
              Set #{set.id} • {set.pieces} pieces • {set.age} • {set.theme} • <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{calculateETA(set.pieces)}</span>
            </div>

          {/* Log a New Build Section (Moved to Top) */}
          <div style={{ background: 'var(--bg-base)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--glass-border)', marginBottom: '3rem', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
            <h4 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: 'var(--accent-blue)' }}>+</span> Log a New Build
            </h4>
            
            <div className="log-build-grid">
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
        <div 
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', marginBottom: isHistoryExpanded ? '2rem' : '0' }}
          onClick={() => setIsHistoryExpanded(!isHistoryExpanded)}
        >
          <h3 style={{ fontSize: '1.75rem', color: 'var(--text-primary)', margin: 0 }}>Build History</h3>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: isHistoryExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease' }}><polyline points="6 9 12 15 18 9"></polyline></svg>
        </div>
        
        {isHistoryExpanded && (
          <div style={{ animation: 'fadeIn 0.3s ease' }}>
            {set.history && set.history.length > 0 ? (
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: 0 }}>
            {set.history.map((record, i) => (
              <li key={i} className="history-item-layout" style={{ background: 'var(--glass-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                {editingIndex === i ? (
                  <div style={{ width: '100%' }}>
                    <div className="history-edit-grid">
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
        )}
      </div>

      {/* Parts Inventory Section */}
      {parts && parts.length > 0 && (
        <div style={{ marginTop: '2rem', paddingTop: '3rem', borderTop: '1px solid var(--glass-border)' }}>
          <div 
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', marginBottom: isPartsExpanded ? '1rem' : '0' }}
            onClick={() => setIsPartsExpanded(!isPartsExpanded)}
          >
            <div>
              <h3 style={{ fontSize: '1.75rem', color: 'var(--text-primary)', margin: 0 }}>Parts Inventory</h3>
              {isPartsExpanded && (
                <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 0 0' }}>
                  {parts.length} unique parts available for this set.
                </p>
              )}
            </div>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: isPartsExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease' }}><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>

          {isPartsExpanded && (
            <div style={{ animation: 'fadeIn 0.3s ease', marginTop: '2rem' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                gap: '1rem'
              }}>
                {parts.map((part, index) => (
                  <Link key={index} to={`/part/${encodeURIComponent(part.name)}`} style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '12px',
                    padding: '1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    textAlign: 'center',
                    transition: 'transform 0.2s, border-color 0.2s',
                    textDecoration: 'none',
                    color: 'inherit',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.borderColor = 'var(--accent-blue)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'none';
                    e.currentTarget.style.borderColor = 'var(--glass-border)';
                  }}
                  >
                    <div style={{
                      width: '100%',
                      background: 'var(--img-bg)',
                      borderRadius: '8px',
                      padding: '0.5rem',
                      marginBottom: '0.75rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <img 
                        src={part.imageUrl} 
                        alt={part.name} 
                        style={{ width: '100%', height: '80px', objectFit: 'contain', mixBlendMode: 'multiply' }}
                        loading="lazy"
                      />
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
                      {part.id}
                    </span>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)', lineHeight: 1.2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }} title={part.name}>
                      {part.name}
                    </span>
                  </Link>
                ))}
            </div>
          </div>
        )}
      </div>
    )}
    </div>
  );
}
