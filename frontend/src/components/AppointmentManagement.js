import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AppointmentManagement = () => {
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    patient_id: '', doctor_id: '', appointment_date: '', appointment_time: '', status: 'scheduled', notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [aptRes, patRes, docRes] = await Promise.all([
        axios.get('/api/appointments'),
        axios.get('/api/patients'),
        axios.get('/api/doctors')
      ]);
      setAppointments(aptRes.data);
      setPatients(patRes.data);
      setDoctors(docRes.data);
    } catch (error) {
      console.error('Failed to fetch data');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        patient_id: parseInt(formData.patient_id),
        doctor_id: parseInt(formData.doctor_id),
        appointment_date: `${formData.appointment_date}T${formData.appointment_time}:00`,
        status: formData.status,
        notes: formData.notes
      };
      if (editing) {
        await axios.put(`/api/appointments/${editing.id}`, payload);
      } else {
        await axios.post('/api/appointments', payload);
      }
      fetchData();
      closeModal();
    } catch (error) {
      alert('Operation failed: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this appointment?')) {
      await axios.delete(`/api/appointments/${id}`);
      fetchData();
    }
  };

  const openModal = (apt = null) => {
    if (apt) {
      setEditing(apt);
      const [date, time] = apt.appointment_date.split('T');
      setFormData({
        patient_id: apt.patient_id,
        doctor_id: apt.doctor_id,
        appointment_date: date,
        appointment_time: time.substring(0, 5),
        status: apt.status,
        notes: apt.notes || ''
      });
    } else {
      setEditing(null);
      setFormData({
        patient_id: '', doctor_id: '', appointment_date: new Date().toISOString().split('T')[0],
        appointment_time: '09:00', status: 'scheduled', notes: ''
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditing(null);
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'scheduled': return 'bg-blue-100 text-blue-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'cancelled': return 'bg-red-100 text-red-700';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Appointments</h1>
        <button onClick={() => openModal()} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Book Appointment
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Patient</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Doctor</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Date & Time</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Status</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {appointments.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-400">No appointments found</td>
              </tr>
            ) : (
              appointments.map(apt => (
                <tr key={apt.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 text-sm text-slate-800">{apt.patient_name}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{apt.doctor_name}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{new Date(apt.appointment_date).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(apt.status)}`}>
                      {apt.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm space-x-2">
                    <button onClick={() => openModal(apt)} className="text-blue-600 hover:text-blue-800">Edit</button>
                    <button onClick={() => handleDelete(apt.id)} className="text-red-600 hover:text-red-800">Delete</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-800">{editing ? 'Edit Appointment' : 'Book Appointment'}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Patient</label>
                  <select required value={formData.patient_id} onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="">Select Patient</option>
                    {patients.map(p => (
                      <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Doctor</label>
                  <select required value={formData.doctor_id} onChange={(e) => setFormData({...formData, doctor_id: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="">Select Doctor</option>
                    {doctors.map(d => (
                      <option key={d.id} value={d.id}>Dr. {d.first_name} {d.last_name} - {d.specialty}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Date</label>
                  <input type="date" required value={formData.appointment_date} onChange={(e) => setFormData({...formData, appointment_date: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Time</label>
                  <input type="time" required value={formData.appointment_time} onChange={(e) => setFormData({...formData, appointment_time: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
                  <select value={formData.status} onChange={(e) => setFormData({...formData, status: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <option value="scheduled">Scheduled</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
                  <textarea value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" rows="3" />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={closeModal} className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">{editing ? 'Update' : 'Book'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentManagement;