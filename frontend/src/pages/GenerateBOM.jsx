import React, { useState, useEffect } from 'react';
import { Layers, Download, Search, Settings } from 'lucide-react';
import apiClient from '../api/client';
import ConfigForm from '../components/ConfigForm';
import EquipmentTable from '../components/EquipmentTable';
import SearchResults from '../components/SearchResults';

const GenerateBOM = () => {
  const [template, setTemplate] = useState(null);
  const [config, setConfig] = useState({
    devise: 'MGA',
    validite_jours: 30
  });
  const [items, setItems] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [useAi, setUseAi] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [exportFormat, setExportFormat] = useState('xlsx'); // Default to xlsx for BOM

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const data = await apiClient.getTemplates();
        if (data.templates && data.templates.bom) {
          setTemplate(data.templates.bom);
        }
      } catch (error) {
        console.error("Failed to load BOM template", error);
      }
    };
    fetchTemplate();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery && !config.projet_description) {
      alert("Veuillez entrer une requête de recherche ou la description du projet.");
      return;
    }
    
    setIsSearching(true);
    setSearchResults([]);
    
    try {
      const query = searchQuery || `Équipements pour: ${config.projet_description}`;
      const results = await apiClient.searchEquipment(
        query, 
        config.type_projet, 
        config.budget_total ? `${config.budget_total}` : '', 
        config.devise
      );
      setSearchResults(results.results || []);
    } catch (error) {
      console.error("Search failed", error);
      alert("Erreur lors de la recherche. Vérifiez que l'API Anthropic/Tavily est bien configurée.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddSelectedItems = (selectedItems) => {
    const newItems = selectedItems.map((item, idx) => ({
      reference: `REF-${(items.length + idx + 1).toString().padStart(3, '0')}`,
      designation: item.nom || item.designation || '',
      marque: item.marque || '',
      modele: item.modele || '',
      quantite: 1,
      prix_unitaire: item.prix_estime || item.prix_unitaire || 0,
      prix_total: item.prix_estime || item.prix_unitaire || 0,
      fournisseur: item.fournisseur || '',
      url: item.url || ''
    }));
    
    setItems([...items, ...newItems]);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await apiClient.generateDocument('bom', config, useAi, items, false, false, exportFormat);
    } catch (error) {
      console.error("Generation failed", error);
      alert("Erreur lors de la génération du document.");
    } finally {
      setIsGenerating(false);
    }
  };

  if (!template) {
    return <div className="flex justify-center mt-20"><div className="spinner"></div></div>;
  }

  return (
    <div className="animate-fade-in pb-12">
      <div className="flex items-center gap-3 mb-6">
        <Layers size={32} color="var(--accent-tertiary)" />
        <div>
          <h1 className="page-title" style={{ fontSize: '2rem' }}>{template.title}</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>{template.description}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
        <div>
          <ConfigForm template={template} config={config} setConfig={setConfig} />
          
          <div className="glass-card p-6 mb-6">
            <h2 className="flex items-center gap-2" style={{ color: 'var(--text-primary)', marginBottom: '16px' }}>
              <Search size={20} /> Recherche d'équipements sur Internet
            </h2>
            <div className="flex gap-4">
              <input 
                type="text" 
                className="input flex-1" 
                placeholder="Ex: Switch Cisco 24 ports PoE+, points d'accès Ubiquiti..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button className="btn btn-primary" onClick={handleSearch} disabled={isSearching}>
                {isSearching ? <div className="spinner" style={{ width: '16px', height: '16px' }}></div> : <Search size={16} />}
                Rechercher
              </button>
            </div>
          </div>

          <SearchResults 
            results={searchResults} 
            isSearching={isSearching} 
            onAddSelected={handleAddSelectedItems} 
          />

          <EquipmentTable 
            items={items} 
            setItems={setItems} 
            currency={config.devise || 'MGA'} 
          />
        </div>

        <div className="glass-panel p-6" style={{ position: 'sticky', bottom: '20px', zIndex: 10 }}>
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <label className="checkbox-container">
                <input 
                  type="checkbox" 
                  checked={useAi} 
                  onChange={(e) => setUseAi(e.target.checked)} 
                />
                <span className="checkmark"></span>
                <span style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Settings size={16} color="var(--accent-secondary)" />
                  Utiliser l'IA pour générer les éléments manquants
                </span>
              </label>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex gap-2 p-1 bg-black/20 rounded-lg">
                <button 
                  className={`px-3 py-1 text-xs rounded-md transition-all ${exportFormat === 'docx' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-500'}`}
                  onClick={() => setExportFormat('docx')}
                >
                  Word
                </button>
                <button 
                  className={`px-3 py-1 text-xs rounded-md transition-all ${exportFormat === 'xlsx' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-500'}`}
                  onClick={() => setExportFormat('xlsx')}
                >
                  Excel
                </button>
              </div>

              <button 
                className="btn btn-primary" 
                style={{ padding: '12px 24px', fontSize: '1rem' }}
                onClick={handleGenerate}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <div className="spinner" style={{ width: '18px', height: '18px' }}></div>
                    Génération en cours...
                  </>
                ) : (
                  <>
                    <Download size={18} />
                    Générer {exportFormat === 'xlsx' ? 'Excel (.xlsx)' : 'Word (.docx)'}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GenerateBOM;
