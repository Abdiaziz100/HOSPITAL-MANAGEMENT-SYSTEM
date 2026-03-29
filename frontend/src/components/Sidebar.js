import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import EventIcon from '@mui/icons-material/Event';
// import ReceiptIcon from '@mui/icons-material/Receipt';
import MedicalInfoIcon from '@mui/icons-material/MedicalInformation';
import PaymentIcon from '@mui/icons-material/Payment';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
    { name: 'Patients', path: '/patients', icon: <PeopleIcon /> },
    { name: 'Doctors', path: '/doctors', icon: <LocalHospitalIcon /> },
    { name: 'Appointments', path: '/appointments', icon: <EventIcon /> },
    { name: 'Billing', path: '/billing', icon: <PaymentIcon /> },
    { name: 'Medical Records', path: '/medical-records', icon: <MedicalInfoIcon /> },
    ...(user?.role === 'admin' ? [{ name: 'Users', path: '/users', icon: <AdminPanelSettingsIcon /> }] : []),
  ];

  return (
    <div className="w-64 bg-white shadow-lg h-screen p-4">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-blue-600">HospitalPro</h2>
        <p className="text-sm text-gray-500">Management System</p>
      </div>
      <nav className="space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
              location.pathname === item.path
                ? 'bg-blue-500 text-white shadow-md'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            {item.icon}
            <span>{item.name}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;

