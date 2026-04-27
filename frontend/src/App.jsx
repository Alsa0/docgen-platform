import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import GenerateBOM from './pages/GenerateBOM';
import GenerateSOW from './pages/GenerateSOW';
import GenerateOT from './pages/GenerateOT';
import GenerateIR from './pages/GenerateIR';
import GenerateLLD from './pages/GenerateLLD';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main className="container mt-8 animate-fade-in">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/generate/bom" element={<GenerateBOM />} />
          <Route path="/generate/sow" element={<GenerateSOW />} />
          <Route path="/generate/ot" element={<GenerateOT />} />
          <Route path="/generate/ir" element={<GenerateIR />} />
          <Route path="/generate/lld" element={<GenerateLLD />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
