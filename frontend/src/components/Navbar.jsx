import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layers, FileText, Briefcase, Wrench, Network, Mail } from 'lucide-react';
import logo from '../logo.png';

const Navbar = () => {
  const location = useLocation();

  const navLinks = [
    { path: '/generate/unified', label: 'BOM & SOW', icon: <Layers size={18} /> },
    { path: '/generate/ot', label: 'OT', icon: <Briefcase size={18} /> },
    { path: '/generate/ir', label: 'IR', icon: <Wrench size={18} /> },
    { path: '/generate/lld', label: 'LLD', icon: <Network size={18} /> },
  ];

  return (
    <nav className="glass-panel" style={{ borderRadius: 0, borderTop: 0, borderLeft: 0, borderRight: 0, position: 'sticky', top: 0, zIndex: 100 }}>
      <div className="container flex items-center justify-between" style={{ height: '70px' }}>
        <Link to="/" className="flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
          <div style={{ 
            background: 'white',
            padding: '4px', 
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)',
            width: '40px',
            height: '40px',
            overflow: 'hidden'
          }}>
            <img src={logo} alt="DocGen Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </div>
          <span style={{ fontSize: '1.2rem', fontWeight: 700, letterSpacing: '0.5px' }}>
            DocGen <span style={{ color: 'var(--accent-tertiary)' }}>Platform</span>
          </span>
        </Link>
        
        <div className="flex gap-2">
          {navLinks.map((link) => (
            <Link 
              key={link.path} 
              to={link.path}
              className={`btn ${location.pathname === link.path ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '8px 16px' }}
            >
              {link.icon}
              <span style={{ display: 'none' }} className="md:inline-block">{link.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
