import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DoctorManagement = () => {
  const [doctors, setDoctors] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', specialty: '', phone: '', email: '', availability: ''
  });

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const res = await axios.get('/api/doctors');
      setDoctors(res.data);
    } catch (error) {
      console.error('Failed to fetch doctors');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editing) {
        await axios.put(`/api/doctors/${editing.id}`, formData);
      } else {
        await axios.post('/api/doctors', formData);
      }
      fetchDoctors();
      closeModal();
    } catch (error) {
      alert('Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Deactivate this doctor?')) {
      await axios.delete(`/api/doctors/${id}`);
      fetchDoctors();
    }
  };

  const openModal = (doctor = null) => {
    if (doctor) {
      setEditing(doctor);
      setFormData({
        first_name: doctor.first_name, last_name: doctor.last_name, specialty: doctor.specialty,
        phone: doctor.phone || '', email: doctor.email || '', availability: doctor.availability || ''
      });
    } else {
      setEditing(null);
      setFormData({ first_name: '', last_name: '', specialty: '', phone: '', email: '', availability: '' });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Doctors</h1>
        <button onClick={() => openModal()} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Doctor
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Name</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Specialty</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Phone</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Availability</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {doctors.map(d => (
              <tr key={d.id} className="hover:bg-slate-50">
                <td className="px-6 py-4 text-sm text-slate-800">Dr. {d.first_name} {d.last_name}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{d.specialty}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{d.phone}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{d.availability}</td>
                <td className="px-6 py-4 text-sm space-x-2">
                  <button onClick={() => openModal(d)} className="text-blue-600 hover:text-blue-800">Edit</button>
                  <button onClick={() => handleDelete(d.id)} className="text-red-600 hover:text-red-800">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-800">{editing ? 'Edit Doctor' : 'Add Doctor'}</h2>
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
                  <label className="block text-sm font-medium text-slate-700 mb-1">Specialty</label>
                  <input required value={formData.specialty} onChange={(e) => setFormData({...formData, specialty: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
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
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Availability</label>
                  <input value={formData.availability} onChange={(e) => setFormData({...formData, availability: e.target.value})}
                    placeholder="e.g., Mon-Fri 9AM-5PM"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
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

export default DoctorManagement;