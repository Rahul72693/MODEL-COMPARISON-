import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Header from './components/layout/Header';
import TabNavigation from './components/layout/TabNavigation';
import DocumentInputPage from './pages/DocumentInputPage';
import ComparisonPage from './pages/ComparisonPage';
import MetricsPage from './pages/MetricsPage';
import './index.css';

function App() {
  const [sessionId] = useState(() => `session-${Date.now()}`);

  return (
    <Router>
      <div className="min-h-screen bg-bg-primary">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <TabNavigation />
          <div className="mt-8">
            <Routes>
              <Route path="/" element={<Navigate to="/document" replace />} />
              <Route path="/document" element={<DocumentInputPage />} />
              <Route path="/comparison" element={<ComparisonPage sessionId={sessionId} />} />
              <Route path="/metrics" element={<MetricsPage sessionId={sessionId} />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
