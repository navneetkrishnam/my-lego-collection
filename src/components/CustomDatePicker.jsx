import React, { useState, useEffect, useRef } from 'react';

export default function CustomDatePicker({ date, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(() => {
    return date ? new Date(date + 'T12:00:00') : new Date();
  });
  const dropdownRef = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Sync internal month with selected date when opened
  useEffect(() => {
    if (isOpen && date) {
      setCurrentMonth(new Date(date + 'T12:00:00'));
    }
  }, [isOpen, date]);

  // Date math
  const getDaysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
  const getFirstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();

  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);

  const days = [];
  // Padding for previous month
  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }
  // Actual days
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const handleDayClick = (day) => {
    // Format YYYY-MM-DD reliably
    const selectedDate = new Date(year, month, day, 12, 0, 0); // Noon to avoid timezone shifts
    const dateStr = selectedDate.toISOString().split('T')[0];
    onChange(dateStr);
    setIsOpen(false);
  };

  const handleTodayClick = () => {
    const today = new Date();
    // Format local today as YYYY-MM-DD
    const tzOffset = today.getTimezoneOffset() * 60000;
    const localISOTime = (new Date(today.getTime() - tzOffset)).toISOString().split('T')[0];
    onChange(localISOTime);
    setIsOpen(false);
  };

  const prevMonth = () => setCurrentMonth(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentMonth(new Date(year, month + 1, 1));

  // Display formatting
  const displayDate = date 
    ? new Date(date + 'T12:00:00').toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })
    : 'Select Date';

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

  return (
    <div style={{ position: 'relative', width: '100%' }} ref={dropdownRef}>
      {/* Input Display */}
      <div 
        className="form-control"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          padding: '0.75rem 1rem',
          boxShadow: isOpen ? '0 0 0 3px rgba(10,132,255,0.2)' : 'none',
          borderColor: isOpen ? 'var(--accent-blue)' : 'var(--glass-border)'
        }}
      >
        <span style={{ fontSize: '1rem' }}>{displayDate}</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
      </div>

      {/* Dropdown Calendar */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 8px)',
          left: 0,
          zIndex: 50,
          width: '100%',
          minWidth: '280px',
          background: 'var(--bg-base)',
          border: '1px solid var(--glass-border)',
          borderRadius: '12px',
          padding: '1rem',
          boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
          animation: 'fadeIn 0.2s ease'
        }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); prevMonth(); }} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
              {monthNames[month]} {year}
            </div>
            <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); nextMonth(); }} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>

          {/* Days Header */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', marginBottom: '0.5rem', textAlign: 'center' }}>
            {weekDays.map(day => (
              <div key={day} style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-tertiary)' }}>{day}</div>
            ))}
          </div>

          {/* Days Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', marginBottom: '1rem' }}>
            {days.map((d, i) => {
              if (!d) return <div key={`empty-${i}`} />;
              
              // Check if selected
              const thisDayStr = `${year}-${String(month+1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
              const isSelected = date === thisDayStr;
              
              // Check if today
              const today = new Date();
              const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();

              return (
                <button
                  key={d}
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDayClick(d); }}
                  style={{
                    padding: '8px 0',
                    background: isSelected ? 'var(--accent-blue)' : 'transparent',
                    color: isSelected ? '#fff' : (isToday ? 'var(--accent-blue)' : 'var(--text-primary)'),
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    fontWeight: isSelected || isToday ? 700 : 400,
                    transition: 'all 0.1s'
                  }}
                  onMouseEnter={(e) => { if (!isSelected) e.target.style.background = 'var(--bg-surface-hover)'; }}
                  onMouseLeave={(e) => { if (!isSelected) e.target.style.background = 'transparent'; }}
                >
                  {d}
                </button>
              );
            })}
          </div>

          {/* Footer - Today Button */}
          <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1rem' }}>
            <button
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleTodayClick(); }}
              style={{
                width: '100%',
                padding: '0.5rem',
                background: 'var(--bg-surface)',
                border: '1px solid var(--glass-border)',
                borderRadius: '6px',
                color: 'var(--accent-blue)',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => e.target.style.background = 'var(--bg-surface-hover)'}
              onMouseLeave={(e) => e.target.style.background = 'var(--bg-surface)'}
            >
              Select Today
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
