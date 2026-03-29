import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const MedicalRecords = () => {
const { user } = useAuth(); // eslint-disable-line no-unused-vars
  const [records, setRecords] = useState([]);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [loading, setLoading] = useState(false);
const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    date: '',
    diagnosis: '',
    treatment_notes: '',
    status: 'active'
  });
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);

useEffect(() => {
    fetchRecords();
    fetchDropdownData();
  }, []);

const fetchRecords = async () => {
    try {
      const res = await axios.get('/api/medical-records');
      setRecords(res.data);
    } catch (error) {
      console.error('Failed to fetch medical records');
    }
  };

  const fetchDropdownData = async () => {
    try {
      const [patientsRes, doctorsRes] = await Promise.all([
        axios.get('/api/patients'),
        axios.get('/api/doctors')
      ]);
      setPatients(patientsRes.data);
      setDoctors(doctorsRes.data);
    } catch (error) {
      console.error('Failed to fetch dropdown data');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
const submitData = {
        patient_id: parseInt(formData.patient_id),
        doctor_id: parseInt(formData.doctor_id),
        diagnosis: formData.diagnosis,
        prescription: formData.treatment_notes,
        doctor_notes: formData.treatment_notes,
        status: formData.status,
      };
      if (editing) {
        await axios.put(`/api/medical-records/${editing.id}`, submitData);
      } else {
        await axios.post('/api/medical-records', submitData);
      }
      fetchRecords();
      closeModal();
    } catch (error) {
      console.error('Submit error:', error.response?.data || error.message);
      alert('Operation failed: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this medical record?')) {
      try {
        await axios.delete(`/api/medical-records/${id}`);
        fetchRecords();
      } catch (error) {
        alert('Delete failed');
      }
    }
  };

  const openModal = (record = null) => {
if (record) {
      setEditing(record);
      setFormData({
        patient_id: record.patient_id || '',
        doctor_id: record.doctor_id || '',
        date: record.created_at ? record.created_at.split('T')[0] : '',
        diagnosis: record.diagnosis || '',
        treatment_notes: record.doctor_notes || '',
        status: record.status || 'active'
      });
    } else {
      setEditing(null);
      setFormData({
        patient_id: '',
        doctor_id: '',
        date: '',
        diagnosis: '',
        treatment_notes: '',
        status: 'active'
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const filteredRecords = records.filter(r => 
    `${r.patient_name || ''} ${r.doctor_name || ''} ${r.diagnosis || ''}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Medical Records</h1>
          <p className="text-slate-500 mt-1">Manage patient medical history and treatment records</p>
        </div>
        <button 
          onClick={() => openModal()} 
          className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          disabled={loading}
        >
          + Add Record
        </button>
      </div>

      <input
        type="text"
        placeholder="Search records by patient, doctor, or diagnosis..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md px-4 py-2.5 border border-slate-300 rounded-lg mb-6 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none shadow-sm"
      />

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Patient</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 hidden md:table-cell">Doctor</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 hidden lg:table-cell">Date</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Diagnosis</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Status</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700 w-32">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filteredRecords.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                  {search ? 'No matching records found' : 'No medical records yet. Create one above.'}
                </td>
              </tr>
            ) : (
              filteredRecords.map((record) => (
                <tr key={record.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-800">{record.patient_name}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600 hidden md:table-cell">{record.doctor_name}</td>
                  <td className="px-6 py-4 text-sm text-slate-600 hidden lg:table-cell">
                    {record.created_at ? new Date(record.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-800 max-w-xs truncate" title={record.diagnosis}>
                      {record.diagnosis}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      record.status === 'completed' ? 'bg-green-100 text-green-800' :
                      record.status === 'active' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium space-x-2">
                    <button 
                      onClick={() => openModal(record)} 
                      className="text-blue-600 hover:text-blue-900"
                      title="Edit"
                    >
                      Edit
                    </button>
                    <button 
                      onClick={() => handleDelete(record.id)} 
                      className="text-red-600 hover:text-red-900"
                      title="Delete"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={closeModal}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-slate-200 sticky top-0 bg-white">
              <h2 className="text-2xl font-bold text-slate-800">
                {editing ? 'Edit Medical Record' : 'Add Medical Record'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Patient</label>
                  <select 
                    required 
                    value={formData.patient_id} 
                    onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  >
                    <option value="">Select Patient</option>
                    {patients.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.first_name} {p.last_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Doctor</label>
                  <select 
                    required 
                    value={formData.doctor_id} 
                    onChange={(e) => setFormData({...formData, doctor_id: e.target.value})}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  >
                    <option value="">Select Doctor</option>
                    {doctors.map((d) => (
                      <option key={d.id} value={d.id}>
                        Dr. {d.first_name} {d.last_name} ({d.specialty})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Date</label>
                  <input 
                    type="date" 
                    required 
                    value={formData.date} 
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Diagnosis</label>
                  <textarea 
                    required 
                    rows="3"
                    value={formData.diagnosis} 
                    onChange={(e) => setFormData({...formData, diagnosis: e.target.value})}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all resize-vertical"
                    placeholder="Enter diagnosis details..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Treatment Notes</label>
                  <textarea 
                    rows="4"
                    value={formData.treatment_notes} 
                    onChange={(e) => setFormData({...formData, treatment_notes: e.target.value})}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all resize-vertical"
                    placeholder="Treatment plan, medications, follow-up instructions..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
                  <select 
                    value={formData.status} 
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  >
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-8 pt-6 border-t border-slate-200">
                <button 
                  type="button" 
                  onClick={closeModal} 
                  className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : editing ? 'Update Record' : 'Create Record'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MedicalRecords;

