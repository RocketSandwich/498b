import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Latency from './components/Latency';
import Jitter from './components/Jitter'
import Packetloss from './components/Packetloss'

function App() {
  return (
    <Router>
      <div>
        <nav>
          <Link to="/latency">Latency</Link>
          <Link to="/jitter">Jitter</Link>
          <Link to="/packetloss">Packetloss</Link>
        </nav>
        <Routes>
          <Route path="/latency" element={<Latency />} />
          <Route path="/jitter" element={<Jitter />} />
          <Route path="/packetloss" element={<Packetloss />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;