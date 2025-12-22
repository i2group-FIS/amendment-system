import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import AmendmentList from './pages/AmendmentList';
import AmendmentDetail from './pages/AmendmentDetail';
import AmendmentCreate from './pages/AmendmentCreate';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/amendments" element={<AmendmentList />} />
          <Route path="/amendments/new" element={<AmendmentCreate />} />
          <Route path="/amendments/:id" element={<AmendmentDetail />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
