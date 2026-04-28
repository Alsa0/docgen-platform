import React, { useState, useEffect } from 'react';
import { Mail, Search, Layers, FileText, Download, CheckCircle2, ChevronRight, Info, AlertCircle } from 'lucide-react';
import apiClient from '../api/client';
import EquipmentTable from '../components/EquipmentTable';

const UnifiedGenerator = () => {
  const [emailContent, setEmailContent] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [selectedProposalId, setSelectedProposalId] = useState(null);
  const [items, setItems] = useState([]);
  const [config, setConfig] = useState({
    projet_titre: '',
    client_nom: '',
    projet_description: '',
    type_projet: 'infrastructure réseau',
    devise: 'MGA',
    budget_total: 0
  });
  const [isGenerating, setIsGenerating] = useState({ bom: false, sow: false });
  const [exportFormat, setExportFormat] = useState('docx'); // docx or xlsx

  // Update items when proposal changes
  useEffect(() => {
    if (analysis && selectedProposalId !== null) {
      const proposal = analysis.proposals.find(p => p.id === selectedProposalId);
      if (proposal) {
        setItems(proposal.bom_items.map((item, idx) => ({
          ...item,
          reference: item.reference || `REF-${(idx + 1).toString().padStart(3, '0')}`,
          prix_total: (item.quantite || 1) * (item.prix_unitaire || 0)
        })));

        setConfig(prev => ({
          ...prev,
          projet_titre: analysis.project_info.title || prev.projet_titre,
          client_nom: analysis.project_info.client || prev.client_nom,
          projet_description: analysis.project_info.description || prev.projet_description,
          type_projet: analysis.project_info.type || prev.type_projet,
          budget_total: proposal.total_estimated,
          devise: proposal.currency || 'MGA'
        }));
      }
    }
  }, [analysis, selectedProposalId]);

  const handleAnalyze = async () => {
    if (!emailContent.trim()) return;
    setIsAnalyzing(true);
    try {
      const data = await apiClient.analyzeRFP(emailContent);
      setAnalysis(data);
      if (data.proposals?.length > 0) setSelectedProposalId(data.proposals[0].id);
    } catch (error) {
      console.error("Analysis failed", error);
      alert("L'analyse a échoué. Vérifiez que le backend est lancé et que la clé API Gemini est valide dans le fichier .env");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerate = async (type) => {
    setIsGenerating(prev => ({ ...prev, [type]: true }));
    try {
      // Préparer la config complète avec les infos du projet
      const fullConfig = {
        ...config,
        projet_description: config.projet_description ||
          analysis?.project_info?.description || '',
        type_projet: config.type_projet ||
          analysis?.project_info?.type || 'infrastructure réseau',
      };

      // Force XLSX for BOM, use selected format for SOW
      const finalFormat = type === 'bom' ? 'xlsx' : exportFormat;

      await apiClient.generateDocument(
        type,
        fullConfig,
        true,          // use_ai
        items,         // bom_items
        type === 'sow', // include_bom
        false,         // include_sow
        finalFormat
      );
    } catch (error) {
      console.error(`${type} generation failed`, error);
      alert(`Erreur lors de la génération du ${type.toUpperCase()}. Vérifiez le terminal backend.`);
    } finally {
      setIsGenerating(prev => ({ ...prev, [type]: false }));
    }
  };

  return (
    <div className="animate-fade-in pb-20 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-10">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
          <Layers size={32} className="text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Générateur Unifié BOM & SOW</h1>
          <p className="text-gray-400">Générez vos listes d'équipements et vos périmètres de travaux en un seul endroit.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {/* Section 1: RFP Input */}
        <section className="glass-card overflow-hidden">
          <div className="p-6 border-b border-white/5 bg-white/5 flex items-center justify-between">
            <h2 className="flex items-center gap-2 font-semibold text-lg text-white">
              <Mail size={20} className="text-indigo-400" /> 1. Analyse de la Demande (Email / RFP)
            </h2>
            {analysis && (
              <span className="badge badge-success flex items-center gap-1">
                <CheckCircle2 size={12} /> Analysé
              </span>
            )}
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-400 mb-4">Collez l'email reçu du client pour que l'IA identifie les équipements et les tâches nécessaires.</p>
            <textarea
              className="input w-full min-h-[150px] mb-4 bg-black/20 border-white/10 focus:border-indigo-500 transition-all"
              placeholder="Cher partenaire, nous souhaitons..."
              value={emailContent}
              onChange={(e) => setEmailContent(e.target.value)}
            />
            <div className="flex justify-end">
              <button
                className="btn btn-primary px-8 py-3 rounded-xl shadow-lg shadow-indigo-500/30"
                onClick={handleAnalyze}
                disabled={isAnalyzing || !emailContent.trim()}
              >
                {isAnalyzing ? <div className="spinner w-5 h-5 mr-2"></div> : <Search size={18} className="mr-2" />}
                {analysis ? 'Ré-analyser la demande' : 'Lancer l\'Analyse IA'}
              </button>
            </div>
          </div>
        </section>

        {/* Section 2: Proposals (Conditional) */}
        {analysis && (
          <section className="animate-slide-up">
            <div className="flex items-center gap-2 mb-4 px-2">
              <ChevronRight size={20} className="text-indigo-500" />
              <h2 className="font-semibold text-white">2. Choisissez une Solution Technique</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {analysis.proposals.map((proposal) => (
                <div
                  key={proposal.id}
                  onClick={() => setSelectedProposalId(proposal.id)}
                  className={`glass-card p-6 cursor-pointer border-2 transition-all duration-300 relative ${selectedProposalId === proposal.id
                      ? 'border-indigo-500 bg-indigo-500/10 scale-[1.02]'
                      : 'border-transparent hover:border-white/20'
                    }`}
                >
                  {selectedProposalId === proposal.id && (
                    <div className="absolute top-4 right-4 text-indigo-500">
                      <CheckCircle2 size={24} />
                    </div>
                  )}
                  <h3 className="font-bold text-xl mb-2 text-white">{proposal.label}</h3>
                  <p className="text-sm text-gray-400 mb-6 line-clamp-3">{proposal.summary}</p>
                  <div className="flex flex-col mt-auto">
                    <span className="text-xs uppercase tracking-wider text-gray-500 mb-1">Estimation totale</span>
                    <span className="text-2xl font-black text-indigo-400">
                      {proposal.total_estimated.toLocaleString()} {proposal.currency}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Section 3: Configuration & Items */}
        <section className={`glass-card ${!analysis && 'opacity-50 pointer-events-none'}`}>
          <div className="p-6 border-b border-white/5 bg-white/5">
            <h2 className="flex items-center gap-2 font-semibold text-lg text-white">
              <Info size={20} className="text-blue-400" /> 3. Détails du Projet & Équipements (BOM)
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-gray-500 uppercase ml-1">Titre du Projet</label>
                <input
                  className="input"
                  value={config.projet_titre}
                  onChange={e => setConfig({ ...config, projet_titre: e.target.value })}
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-gray-500 uppercase ml-1">Client</label>
                <input
                  className="input"
                  value={config.client_nom}
                  onChange={e => setConfig({ ...config, client_nom: e.target.value })}
                />
              </div>
            </div>

            <EquipmentTable items={items} setItems={setItems} currency={config.devise} />
          </div>
        </section>

        {/* Section 4: Generation Footer */}
        <div className={`flex flex-col md:flex-row gap-6 ${!items.length && 'opacity-50 pointer-events-none'}`}>
          <div className="flex-1 glass-card p-6 flex items-center justify-between hover:bg-indigo-500/5 transition-colors border-l-4 border-indigo-500">
            <div>
              <h3 className="font-bold text-white flex items-center gap-2">
                <Layers size={18} className="text-indigo-400" /> Bill of Materials
              </h3>
              <p className="text-sm text-gray-500">Génération directe en Excel (.xlsx)</p>
            </div>
            <button
              className="btn btn-primary px-6"
              onClick={() => handleGenerate('bom')}
              disabled={isGenerating.bom}
            >
              {isGenerating.bom ? <div className="spinner w-5 h-5 mr-2"></div> : <Download size={18} className="mr-2" />}
              Générer Excel
            </button>
          </div>

          <div className="flex-1 glass-card p-6 flex flex-col gap-4 hover:bg-emerald-500/5 transition-colors border-l-4 border-emerald-500">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white flex items-center gap-2">
                  <FileText size={18} className="text-emerald-400" /> Scope of Work
                </h3>
                <p className="text-sm text-gray-500">Détails des tâches et responsabilités</p>
              </div>
              <button
                className="btn bg-emerald-600 hover:bg-emerald-500 text-white flex items-center px-6 py-2 rounded-xl transition-all"
                onClick={() => handleGenerate('sow')}
                disabled={isGenerating.sow}
              >
                {isGenerating.sow ? <div className="spinner w-5 h-5 mr-2"></div> : <Download size={18} className="mr-2" />}
                Générer SOW
              </button>
            </div>
            
            {/* SOW Format Toggle */}
            <div className="flex gap-2 p-1 bg-black/20 rounded-lg self-end">
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
          </div>
        </div>

        {!analysis && (
          <div className="flex items-center justify-center gap-3 p-8 rounded-3xl bg-white/5 border border-dashed border-white/10 text-gray-400">
            <AlertCircle size={20} />
            Commencez par analyser un email en haut de la page pour activer les sections suivantes.
          </div>
        )}
      </div>
    </div>
  );
};

export default UnifiedGenerator;
