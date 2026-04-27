import React from 'react';
import { Link } from 'react-router-dom';
import { Layers, FileText, Briefcase, Wrench, Network, Globe, ArrowRight } from 'lucide-react';

const Home = () => {
  const cards = [
    {
      type: 'bom',
      title: 'Bill of Materials (BOM)',
      description: "Générer une liste d'équipements avec prix du marché",
      icon: <Layers size={32} className="mb-4" color="var(--accent-tertiary)" />,
      path: '/generate/bom',
      search: true
    },
    {
      type: 'sow',
      title: 'Scope of Work (SOW)',
      description: "Détailler les travaux et tâches d'un projet",
      icon: <FileText size={32} className="mb-4" color="var(--success)" />,
      path: '/generate/sow',
      search: true
    },
    {
      type: 'ot',
      title: 'Offre Technique (OT)',
      description: "Créer une offre technique complète",
      icon: <Briefcase size={32} className="mb-4" color="var(--warning)" />,
      path: '/generate/ot',
      search: false
    },
    {
      type: 'ir',
      title: "Rapport d'Intervention (IR)",
      description: "Rédiger un rapport d'intervention terrain",
      icon: <Wrench size={32} className="mb-4" color="var(--info)" />,
      path: '/generate/ir',
      search: false
    },
    {
      type: 'lld',
      title: 'Low Level Design (LLD)',
      description: "Produire un document d'architecture technique détaillé",
      icon: <Network size={32} className="mb-4" color="var(--accent-primary)" />,
      path: '/generate/lld',
      search: true
    }
  ];

  return (
    <div>
      <div className="text-center mb-12 animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <h1 className="page-title">Générateur de Documents IA</h1>
        <p className="page-subtitle">Sélectionnez le type de document que vous souhaitez générer pour votre projet.</p>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '24px',
        padding: '20px 0'
      }}>
        {cards.map((card, index) => (
          <Link 
            to={card.path} 
            key={card.type} 
            className="glass-card animate-fade-in p-6"
            style={{ 
              display: 'flex', 
              flexDirection: 'column',
              animationDelay: `${0.1 * (index + 2)}s`,
              textDecoration: 'none',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {card.search && (
              <div style={{ position: 'absolute', top: '16px', right: '16px' }} title="Utilise la recherche Web IA">
                <span className="badge badge-info flex items-center gap-2">
                  <Globe size={12} /> Web Search
                </span>
              </div>
            )}
            {card.icon}
            <h2 style={{ fontSize: '1.25rem', marginBottom: '8px', color: 'var(--text-primary)' }}>{card.title}</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', flex: 1 }}>{card.description}</p>
            <div className="flex items-center gap-2" style={{ color: 'var(--accent-secondary)', fontWeight: 500, marginTop: 'auto' }}>
              Commencer <ArrowRight size={16} />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Home;
