import React from 'react';

const ConfigForm = ({ template, config, setConfig }) => {
  if (!template || !template.fields) return null;

  const handleChange = (field, value) => {
    setConfig({ ...config, [field]: value });
  };

  const handleListChange = (field, index, value) => {
    const newList = [...(config[field] || [])];
    newList[index] = value;
    setConfig({ ...config, [field]: newList });
  };

  const addListElement = (field) => {
    const newList = [...(config[field] || []), ''];
    setConfig({ ...config, [field]: newList });
  };

  const removeListElement = (field, index) => {
    const newList = [...(config[field] || [])];
    newList.splice(index, 1);
    setConfig({ ...config, [field]: newList });
  };

  return (
    <div className="glass-card p-6 mb-6">
      <h2 style={{ marginBottom: '20px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px' }}>
        Configuration {template.title}
      </h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {Object.entries(template.fields).map(([key, field]) => {
          if (field.type === 'list') {
            const listValue = config[key] || [];
            return (
              <div key={key} className="input-group" style={{ gridColumn: '1 / -1' }}>
                <label className="label">
                  {field.label} {field.required && <span style={{ color: 'var(--danger)' }}>*</span>}
                </label>
                {listValue.map((item, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      className="input"
                      value={item}
                      onChange={(e) => handleListChange(key, index, e.target.value)}
                      placeholder={`Élément ${index + 1}`}
                    />
                    <button 
                      className="btn btn-danger" 
                      onClick={() => removeListElement(key, index)}
                      style={{ padding: '0 15px' }}
                    >
                      &times;
                    </button>
                  </div>
                ))}
                <button 
                  className="btn btn-secondary mt-2" 
                  onClick={() => addListElement(key)}
                  style={{ fontSize: '0.85rem' }}
                >
                  + Ajouter un élément
                </button>
              </div>
            );
          }

          if (field.type === 'boolean') {
            return (
              <div key={key} className="input-group" style={{ gridColumn: '1 / -1' }}>
                <label className="checkbox-container">
                  <input
                    type="checkbox"
                    checked={config[key] || false}
                    onChange={(e) => handleChange(key, e.target.checked)}
                  />
                  <span className="checkmark"></span>
                  {field.label}
                </label>
              </div>
            );
          }

          if (field.type === 'textarea') {
            return (
              <div key={key} className="input-group" style={{ gridColumn: '1 / -1' }}>
                <label className="label">
                  {field.label} {field.required && <span style={{ color: 'var(--danger)' }}>*</span>}
                </label>
                <textarea
                  className="textarea"
                  value={config[key] || ''}
                  onChange={(e) => handleChange(key, e.target.value)}
                  required={field.required}
                  placeholder={`Entrez ${field.label.toLowerCase()}`}
                />
              </div>
            );
          }

          if (field.type === 'select') {
            return (
              <div key={key} className="input-group">
                <label className="label">
                  {field.label} {field.required && <span style={{ color: 'var(--danger)' }}>*</span>}
                </label>
                <select
                  className="select"
                  value={config[key] || field.default || ''}
                  onChange={(e) => handleChange(key, e.target.value)}
                  required={field.required}
                >
                  <option value="" disabled>Sélectionnez une option</option>
                  {field.options?.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            );
          }

          return (
            <div key={key} className="input-group">
              <label className="label">
                {field.label} {field.required && <span style={{ color: 'var(--danger)' }}>*</span>}
              </label>
              <input
                type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : field.type === 'time' ? 'time' : 'text'}
                className="input"
                value={config[key] || ''}
                onChange={(e) => handleChange(key, field.type === 'number' ? Number(e.target.value) : e.target.value)}
                required={field.required}
                placeholder={`Entrez ${field.label.toLowerCase()}`}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ConfigForm;
