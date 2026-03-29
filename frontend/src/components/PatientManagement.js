import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PatientManagement = () => {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', date_of_birth: '', gender: '', phone: '', email: '', address: '', medical_history: ''
  });

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const res = await axios.get('/api/patients');
      setPatients(res.data);
    } catch (error) {
      console.error('Failed to fetch patients');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editing) {
        await axios.put(`/api/patients/${editing.id}`, formData);
      } else {
        await axios.post('/api/patients', formData);
      }
      fetchPatients();
      closeModal();
    } catch (error) {
      alert('Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this patient?')) {
      await axios.delete(`/api/patients/${id}`);
      fetchPatients();
    }
  };

  const openModal = (patient = null) => {
    if (patient) {
      setEditing(patient);
      setFormData({
        first_name: patient.first_name, last_name: patient.last_name, date_of_birth: patient.date_of_birth || '',
        gender: patient.gender, phone: patient.phone || '', email: patient.email || '',
        address: patient.address || '', medical_history: patient.medical_history || ''
      });
    } else {
      setEditing(null);
      setFormData({ first_name: '', last_name: '', date_of_birth: '', gender: '', phone: '', email: '', address: '', medical_history: '' });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const filtered = patients.filter(p => 
    `${p.first_name} ${p.last_name}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Patients</h1>
        <button onClick={() => openModal()} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          + Add Patient
        </button>
      </div>

      <input
        type="text"
        placeholder="Search patients..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md px-4 py-2 border border-slate-300 rounded-lg mb-6 focus:ring-2 focus:ring-blue-500 outline-none"
      />

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Name</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Age</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Gender</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Phone</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filtered.map(p => (
              <tr key={p.id} className="hover:bg-slate-50">
                <td className="px-6 py-4 text-sm text-slate-800">{p.first_name} {p.last_name}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{p.age}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{p.gender}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{p.phone}</td>
                <td className="px-6 py-4 text-sm space-x-2">
                  <button onClick={() => openModal(p)} className="text-blue-600 hover:text-blue-800">Edit</button>
                  <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:text-red-800">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-800">{editing ? 'Edit Patient' : 'Add Patient'}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                  <input required value={formData.first_name} onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                  <input required value={formData.last_name} onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Date of Birth</label>
                  <input type="date" required value={formData.date_of_birth} onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Gender</label>
                  <select required value={formData.gender} onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                  <input value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                  <input type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Address</label>
                  <textarea value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" rows="2" />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Medical History</label>
                  <textarea value={formData.medical_history} onChange={(e) => setFormData({...formData, medical_history: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" rows="3" />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={closeModal} className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">{editing ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientManagement;