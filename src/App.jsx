import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useLegoData } from './hooks/useLegoData';
import HomePage from './pages/HomePage';
import SetDetailPage from './pages/SetDetailPage';
import PartsPage from './pages/PartsPage';
import PartDetailPage from './pages/PartDetailPage';

function App() {
  const { sets, loading, addHistoryRecord, editHistoryRecord, deleteHistoryRecord } = useLegoData();
  
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark' || 
      (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDarkMode]);

  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
        <header style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 className="header-title" style={{ marginBottom: '0.5rem' }}>My Lego Collection</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '1.125rem', marginBottom: '1.5rem' }}>Track, manage, and celebrate your builds.</p>
            </div>
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              style={{ 
                background: 'var(--bg-surface)', 
                border: '1px solid var(--glass-border)', 
                borderRadius: '50%', 
                width: '44px', 
                height: '44px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: 'var(--text-primary)',
                transition: 'all 0.2s',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}
              title="Toggle Dark Mode"
            >
              {isDarkMode ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
              )}
            </button>
          </div>
          
          <nav style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' }}>
            <NavLink 
              to="/" 
              style={({ isActive }) => ({
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '1.125rem',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                borderBottom: isActive ? '2px solid var(--accent-blue)' : '2px solid transparent',
                paddingBottom: '1rem',
                marginBottom: '-1rem',
                transition: 'all 0.2s ease'
              })}
              end
            >
              My Collection
            </NavLink>
            <NavLink 
              to="/parts" 
              style={({ isActive }) => ({
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '1.125rem',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                borderBottom: isActive ? '2px solid var(--accent-blue)' : '2px solid transparent',
                paddingBottom: '1rem',
                marginBottom: '-1rem',
                transition: 'all 0.2s ease'
              })}
            >
              Parts Database
            </NavLink>
          </nav>
        </header>

        <Routes>
          <Route path="/" element={<HomePage sets={sets} loading={loading} />} />
          <Route path="/set/:id" element={<SetDetailPage sets={sets} onAddHistory={addHistoryRecord} onEditHistory={editHistoryRecord} onDeleteHistory={deleteHistoryRecord} />} />
          <Route path="/parts" element={<PartsPage />} />
          <Route path="/part/:name" element={<PartDetailPage sets={sets} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
