import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Briefcase, Download, Settings, Database, ListChecks, ArrowRightLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import apiClient from '../api/client';
import ConfigForm from '../components/ConfigForm';

const COMPANY_NAME = 'NextHope';

const GenerateOT = () => {
  const location = useLocation();
  const stateData = location.state || {};
  
  const [template, setTemplate] = useState(null);
  const [config, setConfig] = useState({
    devise: stateData.config?.devise || 'MGA',
    validite_jours: 30,
    inclure_sow: true,
    inclure_bom: true,
    version: '1.0',
    client_nom: stateData.config?.client_nom || '',
    projet_titre: stateData.config?.projet_titre || '',
    projet_description: stateData.config?.projet_description || '',
    type_projet: stateData.config?.type_projet || '',
    budget_total: stateData.config?.budget_total || 0,
    ...stateData.config
  });
  
  const [bomItems, setBomItems] = useState(stateData.bom_items || []);
  const [sowContent, setSowContent] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [useAi, setUseAi] = useState(true);
  const [useSearch, setUseSearch] = useState(true);
  
  // Nouveaux états UI/UX
  const [selectedSolution, setSelectedSolution] = useState('');
  const [solutions, setSolutions] = useState([]);
  const [prerequisites, setPrerequisites] = useState([]);
  const [complianceData, setComplianceData] = useState([]);

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const data = await apiClient.getTemplates();
        if (data.templates && data.templates.ot) {
          setTemplate(data.templates.ot);
        }
      } catch (error) {
        console.error("Failed to load OT template", error);
      }
    };
    fetchTemplate();

    // Identifier les solutions uniques dans le BOM
    if (bomItems.length > 0) {
      const uniqueSolutions = [...new Set(bomItems.map(item => item.marque || 'Standard'))];
      setSolutions(uniqueSolutions);
      if (uniqueSolutions.length > 0) setSelectedSolution(uniqueSolutions[0]);
    }

    // Tenter de récupérer le SOW si disponible en cache via l'API
    const fetchSow = async () => {
       if (config.projet_titre && config.client_nom) {
         try {
           // On appelle generateDocument avec 'sow' et export_format='none' 
           // Le backend retournera le contenu du cache s'il existe
           const result = await apiClient.generateDocument(
             'sow', 
             config, 
             true, 
             bomItems, 
             true, 
             false, 
             'none'
           );
           if (result && result.content) {
             setSowContent(result.content);
             // Préparer les données de conformité par défaut
             generateDefaultCompliance(result.content);
           }
         } catch (e) {
           console.log("No SOW in cache yet or error", e);
         }
       }
    };
    fetchSow();
  }, []);

  const generateDefaultCompliance = (sow) => {
    // Simulation de données de conformité basées sur le type de projet
    const data = [
      { feat: "Haute disponibilité (HA)", vmware: "✅ Oui", proposed: "✅ Oui", status: "Conforme" },
      { feat: "Migration à chaud", vmware: "✅ Oui", proposed: "✅ Oui", status: "Conforme" },
      { feat: "Gestion centralisée", vmware: "✅ Oui", proposed: "✅ Oui", status: "Conforme" },
      { feat: "Répartition de charge", vmware: "✅ Oui", proposed: "⚠️ Partiel", status: "Non Conforme" },
    ];
    setComplianceData(data);
  };

  const importPrerequisites = () => {
    if (sowContent && sowContent.hypotheses) {
      setPrerequisites(sowContent.hypotheses);
    } else {
      // Prérequis par défaut si SOW non disponible
      setPrerequisites([
        "Accès administrateur aux systèmes cibles",
        "Bande passante réseau ≥ 1 Gbps entre sites",
        "Sauvegardes valides avant intervention",
        "Stabilité du stockage (RAID fonctionnel)"
      ]);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await apiClient.generateDocument(
        'ot', 
        { 
          ...config, 
          selected_solution: selectedSolution,
          prerequisites: prerequisites,
          compliance: complianceData
        }, 
        useAi, 
        bomItems, 
        config.inclure_bom || false, 
        config.inclure_sow || false,
        'docx',
        useSearch
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
    <div className="animate-fade-in pb-20 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-lg shadow-amber-500/20">
          <Briefcase size={32} className="text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Rédaction de l'Offre Technique</h1>
          <p className="text-gray-400">Finalisez votre proposition commerciale en fusionnant le BOM et le SOW.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-8">
          <section className="glass-card overflow-hidden">
            <div className="p-6 border-b border-white/5 bg-white/5 flex items-center justify-between">
              <h2 className="flex items-center gap-2 font-semibold text-lg text-white">
                <Settings size={20} className="text-amber-400" /> Configuration Générale
              </h2>
              {sowContent && (
                <span className="badge badge-success flex items-center gap-1">
                  <CheckCircle2 size={12} /> SOW Importé
                </span>
              )}
            </div>
            <div className="p-6">
              <ConfigForm template={template} config={config} setConfig={setConfig} />
            </div>
          </section>

          {/* Solution Technical Selector */}
          <section className="glass-card">
            <div className="p-6 border-b border-white/5 bg-white/5">
              <h2 className="flex items-center gap-2 font-semibold text-lg text-white">
                <Database size={20} className="text-blue-400" /> Sélecteur de Solution Technique
              </h2>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-400 mb-4">Sélectionnez la solution principale qui servira de base à l'architecture de l'OT.</p>
              <div className="flex flex-wrap gap-4">
                {solutions.length > 0 ? (
                  solutions.map(sol => (
                    <button
                      key={sol}
                      onClick={() => setSelectedSolution(sol)}
                      className={`px-6 py-3 rounded-xl border-2 transition-all ${
                        selectedSolution === sol 
                        ? 'border-amber-500 bg-amber-500/10 text-amber-500' 
                        : 'border-white/10 text-gray-400 hover:border-white/20'
                      }`}
                    >
                      {sol}
                    </button>
                  ))
                ) : (
                  <p className="text-gray-500 italic">Aucune solution détectée dans le BOM.</p>
                )}
              </div>
            </div>
          </section>

          {/* Compliance Comparison Table Preview */}
          <section className="glass-card">
            <div className="p-6 border-b border-white/5 bg-white/5">
              <h2 className="flex items-center gap-2 font-semibold text-lg text-white">
                <ArrowRightLeft size={20} className="text-purple-400" /> Aperçu de Conformité
              </h2>
            </div>
            <div className="p-6">
              <div className="table-wrapper">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Fonctionnalité</th>
                      <th>VMware (Réf)</th>
                      <th>Solution Proposée</th>
                      <th>Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    {complianceData.map((row, idx) => (
                      <tr key={idx}>
                        <td>{row.feat}</td>
                        <td>{row.vmware}</td>
                        <td className="font-semibold text-white">{row.proposed}</td>
                        <td>
                          <span className={`badge ${row.status === 'Conforme' ? 'badge-success' : 'badge-warning'}`}>
                            {row.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Prerequisites Section */}
          <section className="glass-card">
            <div className="p-6 border-b border-white/5 bg-white/5 flex items-center justify-between">
              <h2 className="flex items-center gap-2 font-semibold text-lg text-white">
                <ListChecks size={20} className="text-emerald-400" /> Prérequis
              </h2>
              <button 
                onClick={importPrerequisites}
                className="text-xs text-amber-500 hover:text-amber-400 font-medium"
              >
                Importer
              </button>
            </div>
            <div className="p-6">
              {prerequisites.length > 0 ? (
                <ul className="space-y-3">
                  {prerequisites.map((p, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle2 size={16} className="text-emerald-500 mt-0.5 shrink-0" />
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-4 text-gray-500 text-sm">
                  <p>Cliquez sur importer pour extraire les prérequis du SOW.</p>
                </div>
              )}
            </div>
          </section>

          {/* Sticky Generation Panel */}
          <div className="sticky top-8">
            <section className="glass-panel p-6 border-l-4 border-amber-500">
              <div className="flex flex-col gap-6">
                <div className="flex items-center gap-3">
                  <label className="checkbox-container">
                    <input 
                      type="checkbox" 
                      checked={useAi} 
                      onChange={(e) => setUseAi(e.target.checked)} 
                    />
                    <span className="checkmark"></span>
                    <span className="text-sm font-medium text-white">Génération IA avancée</span>
                  </label>
                  <label className="checkbox-container">
                    <input 
                      type="checkbox" 
                      checked={useSearch} 
                      onChange={(e) => setUseSearch(e.target.checked)} 
                    />
                    <span className="checkmark"></span>
                    <span className="text-sm font-medium text-amber-400">Recherche Web (Google)</span>
                  </label>
                </div>
                
                <div className="space-y-3">
                  <p className="text-xs text-gray-500">
                    L'IA fusionnera les données du BOM ({bomItems.length} items) et du SOW pour créer une offre technique de {COMPANY_NAME}.
                  </p>
                  <button 
                    className="btn btn-primary btn-action w-full"
                    onClick={handleGenerate}
                    disabled={isGenerating}
                  >
                    {isGenerating ? <div className="spinner w-5 h-5 mr-2"></div> : <Download size={18} className="mr-2" />}
                    Générer l'Offre Technique
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GenerateOT;
