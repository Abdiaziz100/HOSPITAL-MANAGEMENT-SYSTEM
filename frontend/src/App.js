import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import PatientManagement from './components/PatientManagement';
import DoctorManagement from './components/DoctorManagement';
import AppointmentManagement from './components/AppointmentManagement';
import BillingManagement from './components/BillingManagement';
import MedicalRecords from './components/MedicalRecords';
import UserManagement from './components/UserManagement';
import Sidebar from './components/Sidebar';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import './App.css';

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-lg text-slate-600">Loading Hospital Management System...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex">
      {user && <Sidebar />}
      <main className={user ? "flex-1" : "w-full"}>
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/patients" element={user ? <PatientManagement /> : <Navigate to="/login" />} />
          <Route path="/doctors" element={user ? <DoctorManagement /> : <Navigate to="/login" />} />
          <Route path="/appointments" element={user ? <AppointmentManagement /> : <Navigate to="/login" />} />
          <Route path="/medical-records" element={user ? <MedicalRecords /> : <Navigate to="/login" />} />
          <Route path="/billing" element={user ? <BillingManagement /> : <Navigate to="/login" />} />
          <Route path="/users" element={user && user.role === 'admin' ? <UserManagement /> : <Navigate to="/dashboard" />} />
          <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <NotificationProvider>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </NotificationProvider>
  );
}

export default App;

