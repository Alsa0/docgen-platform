import React, { useState, useEffect } from 'react';
import { Network, Download, Search, Settings } from 'lucide-react';
import apiClient from '../api/client';
import ConfigForm from '../components/ConfigForm';
import EquipmentTable from '../components/EquipmentTable';

const GenerateLLD = () => {
  const [template, setTemplate] = useState(null);
  const [config, setConfig] = useState({
    inclure_bom: true
  });
  const [bomItems, setBomItems] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [useAi, setUseAi] = useState(true);
  const [isSearchingDatasheet, setIsSearchingDatasheet] = useState(false);
  const [datasheetResult, setDatasheetResult] = useState(null);

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const data = await apiClient.getTemplates();
        if (data.templates && data.templates.lld) {
          setTemplate(data.templates.lld);
        }
      } catch (error) {
        console.error("Failed to load LLD template", error);
      }
    };
    fetchTemplate();
  }, []);

  const handleSearchDatasheet = async () => {
    if (!config.equipements_principaux || config.equipements_principaux.length === 0) {
      alert("Veuillez d'abord ajouter au moins un équipement principal dans la configuration.");
      return;
    }

    const firstEquipment = config.equipements_principaux[0];
    setIsSearchingDatasheet(true);
    setDatasheetResult(null);

    try {
      const result = await apiClient.searchDatasheet(firstEquipment);
      setDatasheetResult(result.result || result);
    } catch (error) {
      console.error("Datasheet search failed", error);
      alert("Erreur lors de la recherche de la datasheet.");
    } finally {
      setIsSearchingDatasheet(false);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await apiClient.generateDocument(
        'lld', 
        config, 
        useAi, 
        bomItems, 
        config.inclure_bom || false, 
        false
      );
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
        <Network size={32} color="var(--accent-primary)" />
        <div>
          <h1 className="page-title" style={{ fontSize: '2rem' }}>{template.title}</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>{template.description}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
        <div>
          <ConfigForm template={template} config={config} setConfig={setConfig} />
          
          <div className="glass-card p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="flex items-center gap-2" style={{ color: 'var(--text-primary)', margin: 0 }}>
                <Search size={20} /> Recherche de Fiches Techniques (Datasheets)
              </h2>
              <button 
                className="btn btn-secondary" 
                onClick={handleSearchDatasheet}
                disabled={isSearchingDatasheet || !config.equipements_principaux?.length}
              >
                {isSearchingDatasheet ? <div className="spinner" style={{ width: '16px', height: '16px' }}></div> : <Search size={16} />}
                Rechercher
              </button>
            </div>
            
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '16px' }}>
              Testez la recherche de spécifications techniques pour le premier équipement de votre liste : 
              <strong> {config.equipements_principaux?.[0] || 'Aucun équipement'}</strong>
            </p>

            {datasheetResult && (
              <div className="p-4 rounded" style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-subtle)' }}>
                <h4 style={{ color: 'var(--accent-secondary)', marginBottom: '8px' }}>
                  {datasheetResult.marque} {datasheetResult.modele}
                </h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  {datasheetResult.specifications?.description || JSON.stringify(datasheetResult)}
                </p>
                {datasheetResult.datasheet_url && (
                  <a href={datasheetResult.datasheet_url} target="_blank" rel="noreferrer" style={{ display: 'inline-block', marginTop: '8px', fontSize: '0.85rem' }}>
                    Voir le PDF original
                  </a>
                )}
              </div>
            )}
          </div>

          {config.inclure_bom && (
            <div className="animate-fade-in">
              <EquipmentTable 
                items={bomItems} 
                setItems={setBomItems} 
                currency={config.devise || 'MGA'} 
              />
            </div>
          )}
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
                  Utiliser l'IA + Web Search pour générer l'architecture complète
                </span>
              </label>
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
                  Générer le Document DOCX
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GenerateLLD;
