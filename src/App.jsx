import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useLegoData } from './hooks/useLegoData';
import HomePage from './pages/HomePage';
import SetDetailPage from './pages/SetDetailPage';
import PartsPage from './pages/PartsPage';

function App() {
  const { sets, loading, addHistoryRecord, editHistoryRecord, deleteHistoryRecord } = useLegoData();

  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
        <header style={{ marginBottom: '2rem' }}>
          <h1 className="header-title" style={{ marginBottom: '0.5rem' }}>My Lego Collection</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.125rem', marginBottom: '1.5rem' }}>Track, manage, and celebrate your builds.</p>
          
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
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
