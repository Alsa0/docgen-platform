import React from 'react';
import { Trash2, Plus } from 'lucide-react';

const EquipmentTable = ({ items, setItems, currency = 'MGA' }) => {
  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // Auto-calculate total
    if (field === 'quantite' || field === 'prix_unitaire') {
      const q = Number(newItems[index].quantite) || 0;
      const p = Number(newItems[index].prix_unitaire) || 0;
      newItems[index].prix_total = q * p;
    }
    
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, { 
      reference: `REF-${(items.length + 1).toString().padStart(3, '0')}`,
      designation: '', 
      marque: '', 
      modele: '', 
      quantite: 1, 
      prix_unitaire: 0, 
      prix_total: 0,
      fournisseur: '',
      url: ''
    }]);
  };

  const removeItem = (index) => {
    const newItems = [...items];
    newItems.splice(index, 1);
    setItems(newItems);
  };

  const totalGlobal = items.reduce((sum, item) => sum + (Number(item.prix_total) || 0), 0);

  return (
    <div className="glass-card p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 style={{ color: 'var(--text-primary)' }}>Tableau des Équipements (BOM)</h2>
        <button className="btn btn-secondary" onClick={addItem}>
          <Plus size={16} /> Ajouter une ligne
        </button>
      </div>

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th width="5%">N°</th>
              <th width="12%">Référence</th>
              <th width="20%">Désignation</th>
              <th width="15%">Marque/Modèle</th>
              <th width="8%">Qté</th>
              <th width="12%">Prix Unitaire</th>
              <th width="12%">Prix Total</th>
              <th width="10%">Fournisseur</th>
              <th width="6%">Action</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>
                  <input className="table-input" value={item.reference || ''} onChange={(e) => handleItemChange(index, 'reference', e.target.value)} />
                </td>
                <td>
                  <input className="table-input" value={item.designation || ''} onChange={(e) => handleItemChange(index, 'designation', e.target.value)} placeholder="Nom équipement" />
                </td>
                <td>
                  <input className="table-input" value={`${item.marque || ''} ${item.modele || ''}`} onChange={(e) => {
                    const parts = e.target.value.split(' ');
                    handleItemChange(index, 'marque', parts[0] || '');
                    handleItemChange(index, 'modele', parts.slice(1).join(' ') || '');
                  }} placeholder="Marque Modèle" />
                </td>
                <td>
                  <input className="table-input" type="number" min="1" value={item.quantite || 1} onChange={(e) => handleItemChange(index, 'quantite', Number(e.target.value))} />
                </td>
                <td>
                  <input className="table-input" type="number" min="0" value={item.prix_unitaire || 0} onChange={(e) => handleItemChange(index, 'prix_unitaire', Number(e.target.value))} />
                </td>
                <td style={{ fontWeight: 'bold' }}>
                  {(item.prix_total || 0).toLocaleString()} {currency}
                </td>
                <td>
                  <input className="table-input" value={item.fournisseur || ''} onChange={(e) => handleItemChange(index, 'fournisseur', e.target.value)} placeholder="Nom" />
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button onClick={() => removeItem(index)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', padding: '5px' }}>
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>
                  Aucun équipement ajouté. Utilisez la recherche IA ou ajoutez manuellement.
                </td>
              </tr>
            )}
            <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
              <td colSpan="6" style={{ textAlign: 'right', fontWeight: 'bold', paddingRight: '20px' }}>TOTAL GLOBAL :</td>
              <td colSpan="3" style={{ fontWeight: 'bold', color: 'var(--accent-secondary)' }}>{totalGlobal.toLocaleString()} {currency}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EquipmentTable;
