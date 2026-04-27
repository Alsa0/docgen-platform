import React, { useState } from 'react';
import { ExternalLink, CheckCircle, ShieldCheck, PlusCircle } from 'lucide-react';

const SearchResults = ({ results, onAddSelected, isSearching }) => {
  const [selectedIndices, setSelectedIndices] = useState(new Set());

  if (isSearching) {
    return (
      <div className="glass-card p-6 mb-6 flex flex-col items-center justify-center min-h-[200px]">
        <div className="spinner mb-4"></div>
        <p style={{ color: 'var(--text-secondary)' }}>Recherche d'équipements sur internet via Claude AI...</p>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>Cette opération peut prendre quelques secondes.</p>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return null;
  }

  const toggleSelection = (index) => {
    const newSelected = new Set(selectedIndices);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedIndices(newSelected);
  };

  const selectAll = () => {
    if (selectedIndices.size === results.length) {
      setSelectedIndices(new Set());
    } else {
      setSelectedIndices(new Set(results.map((_, i) => i)));
    }
  };

  const handleAdd = () => {
    const selectedItems = results.filter((_, index) => selectedIndices.has(index));
    onAddSelected(selectedItems);
    setSelectedIndices(new Set());
  };

  return (
    <div className="glass-card p-6 mb-6 animate-fade-in">
      <div className="flex justify-between items-center mb-4 pb-2" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={20} color="var(--success)" />
          Résultats de la recherche ({results.length})
        </h3>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={selectAll} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            {selectedIndices.size === results.length ? 'Désélectionner tout' : 'Sélectionner tout'}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleAdd}
            disabled={selectedIndices.size === 0}
            style={{ padding: '6px 12px', fontSize: '0.8rem', opacity: selectedIndices.size === 0 ? 0.5 : 1 }}
          >
            <PlusCircle size={16} />
            Ajouter la sélection ({selectedIndices.size})
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {results.map((item, index) => {
          const isSelected = selectedIndices.has(index);
          return (
            <div 
              key={index} 
              className="glass-panel" 
              style={{ 
                padding: '16px', 
                border: isSelected ? '1px solid var(--accent-secondary)' : '1px solid var(--border-subtle)',
                backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.05)' : 'var(--bg-glass)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onClick={() => toggleSelection(index)}
            >
              <div className="flex justify-between items-start mb-2">
                <label className="checkbox-container" onClick={(e) => e.stopPropagation()}>
                  <input 
                    type="checkbox" 
                    checked={isSelected} 
                    onChange={() => toggleSelection(index)} 
                  />
                  <span className="checkmark"></span>
                </label>
                {item.confiance_prix === 'vérifié' && (
                  <span className="badge badge-success flex items-center gap-1" style={{ fontSize: '0.65rem' }}>
                    <ShieldCheck size={10} /> Prix vérifié
                  </span>
                )}
              </div>
              
              <h4 style={{ color: 'var(--text-primary)', marginBottom: '4px', fontSize: '1rem' }}>{item.nom || item.designation}</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '12px' }}>
                {item.marque} {item.modele}
              </p>
              
              <div className="flex justify-between items-center mt-auto pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontWeight: 'bold', color: 'var(--accent-secondary)' }}>
                  {(item.prix_estime || item.prix_unitaire || 0).toLocaleString()} {item.devise || 'MGA'}
                </span>
                {item.url && (
                  <a 
                    href={item.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    onClick={(e) => e.stopPropagation()}
                    style={{ color: 'var(--text-secondary)' }}
                    title="Voir la source"
                  >
                    <ExternalLink size={16} />
                  </a>
                )}
              </div>
              {item.fournisseur && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Fournisseur: {item.fournisseur}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SearchResults;
