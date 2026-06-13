import { useState, useEffect } from 'react';

// Instead of importing the static JSON file directly (which is read-only at runtime without full reloads),
// we fetch it dynamically so it always reflects the latest state saved to disk.
export function useLegoData() {
  const [sets, setSets] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSets = async () => {
    try {
      const response = await fetch('/src/data/sets.json?t=' + Date.now());
      const jsonData = await response.json();
      setSets(jsonData);
    } catch (e) {
      console.error("Failed to load sets", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSets();
  }, []);

  const saveSets = async (newSets) => {
    setSets(newSets); // Optimistic UI update
    try {
      await fetch('/api/updateSets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSets)
      });
    } catch (err) {
      console.error("Failed to save sets", err);
    }
  };

  const updateStatus = (setId, status) => {
    const newSets = sets.map(s => s.id === setId ? { ...s, status } : s);
    saveSets(newSets);
  };

  const addHistoryRecord = (setId, record) => {
    const newSets = sets.map(s => {
      if (s.id === setId) {
        return {
          ...s,
          status: 'Done', // auto mark as done
          history: [...s.history, record].sort((a, b) => new Date(a.date) - new Date(b.date))
        };
      }
      return s;
    });
    saveSets(newSets);
  };

  const editHistoryRecord = (setId, index, updatedRecord) => {
    const newSets = sets.map(s => {
      if (s.id === setId) {
        const newHistory = [...s.history];
        newHistory[index] = updatedRecord;
        return {
          ...s,
          history: newHistory.sort((a, b) => new Date(a.date) - new Date(b.date))
        };
      }
      return s;
    });
    saveSets(newSets);
  };

  const deleteHistoryRecord = (setId, index) => {
    const newSets = sets.map(s => {
      if (s.id === setId) {
        const newHistory = [...s.history];
        newHistory.splice(index, 1);
        return {
          ...s,
          status: newHistory.length === 0 ? 'Not Started' : 'Done',
          history: newHistory
        };
      }
      return s;
    });
    saveSets(newSets);
  };

  return {
    sets,
    loading,
    updateStatus,
    addHistoryRecord,
    editHistoryRecord,
    deleteHistoryRecord,
  };
}
