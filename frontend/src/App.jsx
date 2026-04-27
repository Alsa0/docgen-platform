import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import GenerateOT from './pages/GenerateOT';
import GenerateIR from './pages/GenerateIR';
import GenerateLLD from './pages/GenerateLLD';
import UnifiedGenerator from './pages/UnifiedGenerator';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main className="container mt-8 animate-fade-in">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/generate/unified" element={<UnifiedGenerator />} />
          <Route path="/generate/bom" element={<UnifiedGenerator />} />
          <Route path="/generate/sow" element={<UnifiedGenerator />} />
          <Route path="/generate/ot" element={<GenerateOT />} />
          <Route path="/generate/ir" element={<GenerateIR />} />
          <Route path="/generate/lld" element={<GenerateLLD />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;