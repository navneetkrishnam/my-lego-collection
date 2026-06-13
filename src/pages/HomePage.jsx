import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import SummaryCards from '../components/SummaryCards';
import FilterSidebar from '../components/FilterSidebar';
import SetCard from '../components/SetCard';

export default function HomePage({ sets, loading }) {
  const [filters, setFilters] = useState({
    status: [],
    theme: [],
    age: [],
    pieces: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOption, setSortOption] = useState('Name (A-Z)');
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [isMobileReportOpen, setIsMobileReportOpen] = useState(false);
  const [isSortMenuOpen, setIsSortMenuOpen] = useState(false);

  const navigate = useNavigate();

  // Dynamically compute available themes and ages from the dataset
  const themeOptions = useMemo(() => {
    return Array.from(new Set(sets.map(s => s.theme || 'Misc'))).sort();
  }, [sets]);

  const ageOptions = useMemo(() => {
    const normalizedAges = sets.map(s => {
      let age = s.age || 'N/A';
      if (age === '1½+') return '1.5+';
      if (age.includes('-')) return age.split('-')[0] + '+';
      return age;
    });
    const ages = Array.from(new Set(normalizedAges));
    return ages.sort((a, b) => {
      const numA = parseFloat(a.replace(/[^\d.]/g, '')) || 0;
      const numB = parseFloat(b.replace(/[^\d.]/g, '')) || 0;
      return numA - numB;
    });
  }, [sets]);

  const filteredSets = useMemo(() => {
    let result = sets.filter(s => {
      // Status intersection
      if (filters.status.length > 0) {
        const mappedStatus = s.status === 'Done' ? 'Completed' : s.status;
        if (!filters.status.includes(mappedStatus)) return false;
      }
      
      // Theme intersection
      if (filters.theme.length > 0) {
        if (!filters.theme.includes(s.theme)) return false;
      }

      // Age intersection
      if (filters.age.length > 0) {
        let normalizedAge = s.age || 'N/A';
        if (normalizedAge === '1½+') normalizedAge = '1.5+';
        if (normalizedAge.includes('-')) normalizedAge = normalizedAge.split('-')[0] + '+';
        
        if (!filters.age.includes(normalizedAge)) return false;
      }

      // Pieces intersection
      if (filters.pieces.length > 0) {
        const p = s.pieces || 0;
        const matchesPiece = filters.pieces.some(pf => {
          if (pf === '< 500 pcs' && p < 500) return true;
          if (pf === '500-1000 pcs' && p >= 500 && p <= 1000) return true;
          if (pf === '1000-2000 pcs' && p > 1000 && p <= 2000) return true;
          if (pf === '2000+ pcs' && p > 2000) return true;
          return false;
        });
        if (!matchesPiece) return false;
      }

      // Search Query
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        if (!s.name.toLowerCase().includes(q) && !s.id.includes(q)) return false;
      }

      return true;
    });

    // Sort
    result.sort((a, b) => {
      if (sortOption === 'Name (A-Z)') return a.name.localeCompare(b.name);
      if (sortOption === 'Pieces (Low-High)') return (a.pieces || 0) - (b.pieces || 0);
      if (sortOption === 'Pieces (High-Low)') return (b.pieces || 0) - (a.pieces || 0);
      return 0;
    });

    return result;
  }, [sets, filters, searchQuery, sortOption]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <h2 className="animate-fade-in">Loading Collection...</h2>
      </div>
    );
  }

  return (
    <>
      <div className="desktop-only">
        <SummaryCards sets={sets} />
      </div>

      <div className="page-layout">
        {/* Desktop Sidebar */}
        <div className="desktop-only">
          <FilterSidebar 
            filters={filters} 
            setFilters={setFilters} 
            themeOptions={themeOptions}
            ageOptions={ageOptions}
          />
        </div>

        {/* Mobile Report Drawer */}
        <div className={`mobile-filter-overlay mobile-only ${isMobileReportOpen ? 'open' : ''}`} style={{ justifyContent: 'flex-start' }} onClick={(e) => { if (e.target.classList.contains('mobile-filter-overlay')) setIsMobileReportOpen(false); }}>
          <div className="mobile-report-drawer">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.5rem' }}>Collection Report</h3>
              <button onClick={() => setIsMobileReportOpen(false)} style={{ background: 'var(--bg-surface-hover)', borderRadius: '50%', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
            <SummaryCards sets={sets} />
          </div>
        </div>

        {/* Mobile Filter Drawer */}
        <div className={`mobile-filter-overlay mobile-only ${isMobileFilterOpen ? 'open' : ''}`} onClick={(e) => { if (e.target.classList.contains('mobile-filter-overlay')) setIsMobileFilterOpen(false); }}>
          <div className="mobile-filter-drawer">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.5rem' }}>Filters</h3>
              <button onClick={() => setIsMobileFilterOpen(false)} style={{ background: 'var(--bg-surface-hover)', borderRadius: '50%', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
            
            <FilterSidebar 
              filters={filters} 
              setFilters={setFilters} 
              themeOptions={themeOptions}
              ageOptions={ageOptions}
            />

            <button 
              className="btn btn-primary" 
              style={{ width: '100%', marginTop: '2rem', padding: '1rem', fontSize: '1.125rem' }}
              onClick={() => setIsMobileFilterOpen(false)}
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div style={{ flexGrow: 1 }}>
          {/* Top Row: Search and Sort */}
          <div className="top-controls">
            {/* Search */}
              <div style={{ position: 'relative', flexGrow: 1, minWidth: '300px' }}>
                <svg style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                <input 
                  type="text" 
                  className="form-control"
                  placeholder="Search sets by name or ID..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ paddingLeft: '2.5rem', paddingRight: searchQuery ? '2.5rem' : '1rem', borderRadius: '999px' }}
                />
                {searchQuery && (
                  <button 
                    onClick={() => setSearchQuery('')}
                    style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'var(--bg-surface-hover)', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', cursor: 'pointer', border: 'none' }}
                    title="Clear search"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                  </button>
                )}
              </div>

              {/* Desktop Sort Dropdown */}
              <div className="desktop-only" style={{ position: 'relative', minWidth: '180px' }}>
                <select 
                  className="form-control"
                  value={sortOption}
                  onChange={(e) => setSortOption(e.target.value)}
                  style={{ appearance: 'none', cursor: 'pointer', borderRadius: '999px' }}
                >
                <option value="Name (A-Z)">Name (A-Z)</option>
                <option value="Pieces (Low-High)">Pieces (Low-High)</option>
                <option value="Pieces (High-Low)">Pieces (High-Low)</option>
              </select>
              <svg style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-tertiary)' }} width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            
            {/* Mobile Action Buttons */}
            <div className="mobile-filter-btn" style={{ width: '100%', display: 'flex', gap: '0.5rem' }}>
              <button 
                className="btn btn-secondary"
                onClick={() => setIsMobileReportOpen(true)}
                style={{ flex: 1 }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                Report
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => setIsMobileFilterOpen(true)}
                style={{ flex: 1 }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
                Filters {(Object.values(filters).reduce((acc, arr) => acc + arr.length, 0) > 0) && `(${Object.values(filters).reduce((acc, arr) => acc + arr.length, 0)})`}
              </button>
              <div style={{ position: 'relative', flexShrink: 0 }}>
                <button 
                  className="btn btn-secondary" 
                  style={{ height: '100%', padding: '0 1rem' }}
                  onClick={() => setIsSortMenuOpen(!isSortMenuOpen)}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="7" y1="4" x2="7" y2="20"></line>
                    <polyline points="3 16 7 20 11 16"></polyline>
                    <line x1="17" y1="20" x2="17" y2="4"></line>
                    <polyline points="21 8 17 4 13 8"></polyline>
                  </svg>
                </button>

                {isSortMenuOpen && (
                  <>
                    <div style={{ position: 'fixed', inset: 0, zIndex: 90 }} onClick={() => setIsSortMenuOpen(false)}></div>
                    <div className="glass-panel" style={{ position: 'absolute', top: '100%', right: 0, marginTop: '0.5rem', zIndex: 100, minWidth: '180px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      {['Name (A-Z)', 'Pieces (Low-High)', 'Pieces (High-Low)'].map(option => (
                        <button 
                          key={option}
                          style={{ padding: '0.75rem 1rem', textAlign: 'left', background: sortOption === option ? 'var(--bg-surface-hover)' : 'transparent', color: sortOption === option ? 'var(--accent-blue)' : 'var(--text-primary)', fontWeight: sortOption === option ? 600 : 400, borderBottom: '1px solid var(--glass-border)' }}
                          onClick={() => { setSortOption(option); setIsSortMenuOpen(false); }}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span>Showing {filteredSets.length} of {sets.length} sets</span>
            {(Object.values(filters).some(arr => arr.length > 0) || searchQuery.trim() !== '') && (
              <button 
                onClick={() => {
                  setFilters({ status: [], theme: [], age: [], pieces: [] });
                  setSearchQuery('');
                }}
                style={{ background: 'none', border: 'none', color: 'var(--accent-blue)', fontSize: '0.875rem', cursor: 'pointer', fontWeight: 600, padding: 0 }}
              >
                Clear Filters
              </button>
            )}
          </div>

          {filteredSets.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-tertiary)', background: 'var(--bg-surface)', borderRadius: '12px', border: '1px dashed var(--glass-border)' }}>
              <h3 style={{ marginBottom: '0.5rem' }}>No sets match your criteria.</h3>
              <p>Try adjusting your filters on the left.</p>
            </div>
          ) : (
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
              gap: '2rem' 
            }}>
              {filteredSets.map(set => (
                <div key={set.id} className="animate-fade-in" style={{ height: '100%' }}>
                  <SetCard 
                    set={set} 
                    onClick={() => navigate(`/set/${set.id}`)}
                    onMarkAsDone={() => navigate(`/set/${set.id}`)} 
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
