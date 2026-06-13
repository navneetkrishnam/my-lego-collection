import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useLegoData } from './hooks/useLegoData';
import HomePage from './pages/HomePage';
import SetDetailPage from './pages/SetDetailPage';

function App() {
  const { sets, loading, addHistoryRecord, editHistoryRecord, deleteHistoryRecord } = useLegoData();

  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
        <header style={{ marginBottom: '3rem' }}>
          <h1 className="header-title">My Lego Collection</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.125rem' }}>Track, manage, and celebrate your builds.</p>
        </header>

        <Routes>
          <Route path="/" element={<HomePage sets={sets} loading={loading} />} />
          <Route path="/set/:id" element={<SetDetailPage sets={sets} onAddHistory={addHistoryRecord} onEditHistory={editHistoryRecord} onDeleteHistory={deleteHistoryRecord} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
