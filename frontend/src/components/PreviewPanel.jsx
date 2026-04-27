import React from 'react';

const PreviewPanel = ({ html, title, isLoading }) => {
  if (isLoading) {
    return (
      <div className="glass-card p-6 flex items-center justify-center min-h-[400px]">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!html) {
    return (
      <div className="glass-card p-6 flex flex-col items-center justify-center min-h-[400px]" style={{ color: 'var(--text-muted)' }}>
        <p>Générez un aperçu pour voir le rendu de votre document.</p>
      </div>
    );
  }

  return (
    <div className="glass-card p-0 overflow-hidden" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '15px 20px', borderBottom: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.02)' }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-primary)' }}>Aperçu: {title}</h3>
      </div>
      <div 
        style={{ 
          padding: '20px', 
          flex: 1, 
          overflowY: 'auto',
          backgroundColor: '#ffffff', // White background for the preview content to mimic a document
          color: '#333333' // Dark text for readability on white background
        }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
};

export default PreviewPanel;
