import React, { useState, useEffect } from 'react';
import { FileText, Download, Settings } from 'lucide-react';
import apiClient from '../api/client';
import ConfigForm from '../components/ConfigForm';
import EquipmentTable from '../components/EquipmentTable';

const GenerateSOW = () => {
  const [template, setTemplate] = useState(null);
  const [config, setConfig] = useState({
    devise: 'MGA',
    inclure_bom: false
  });
  const [bomItems, setBomItems] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [useAi, setUseAi] = useState(true);
  const [exportFormat, setExportFormat] = useState('docx'); // Default to docx for SOW

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const data = await apiClient.getTemplates();
        if (data.templates && data.templates.sow) {
          setTemplate(data.templates.sow);
        }
      } catch (error) {
        console.error("Failed to load SOW template", error);
      }
    };
    fetchTemplate();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await apiClient.generateDocument(
        'sow', 
        config, 
        useAi, 
        bomItems, 
        config.inclure_bom || false, 
        false,
        exportFormat
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
        <FileText size={32} color="var(--success)" />
        <div>
          <h1 className="page-title" style={{ fontSize: '2rem' }}>{template.title}</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>{template.description}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
        <div>
          <ConfigForm template={template} config={config} setConfig={setConfig} />
          
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
                  Laisser l'IA générer les détails des tâches et jalons
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

export default GenerateSOW;
