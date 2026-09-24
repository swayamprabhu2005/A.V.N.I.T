import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, Database, Check, AlertCircle } from 'lucide-react';
import { fetchVehicles, createVehicle, deleteVehicle } from '../services/api';

export default function VehicleManagerModal({ isOpen, onClose }) {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // New vehicle form state
  const [plate, setPlate] = useState('');
  const [type, setType] = useState('car');
  const [color, setColor] = useState('white');
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [status, setStatus] = useState('Active');

  const loadVehicles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchVehicles();
      setVehicles(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadVehicles();
      setError(null);
      setSuccess(null);
    }
  }, [isOpen]);

  const handleAddVehicle = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!plate.trim()) {
      setError("Please enter a valid number plate.");
      return;
    }

    try {
      await createVehicle({
        plate_number: plate.toUpperCase().trim(),
        vehicle_type: type,
        color: color,
        make: make.trim() || "Generic",
        model: model.trim() || "Model",
        registration_status: status
      });
      setSuccess(`Vehicle ${plate.toUpperCase()} registered successfully!`);
      setPlate('');
      setMake('');
      setModel('');
      loadVehicles();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id, plateNum) => {
    if (!window.confirm(`Delete registered record for ${plateNum}?`)) return;
    try {
      await deleteVehicle(id);
      loadVehicles();
    } catch (err) {
      setError(err.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-border w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Controlled Vehicle Registration Database</h3>
              <p className="text-xs text-slate-400">Manage expected ground-truth records for identity verification</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {success && (
            <div className="flex items-center gap-2 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs">
              <Check className="w-4 h-4 flex-shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {/* Add Vehicle Form */}
          <form onSubmit={handleAddVehicle} className="bg-slate-900/60 p-4 rounded-xl border border-border/70 space-y-3">
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Plus className="w-3.5 h-3.5 text-blue-400" /> Register New Test Vehicle
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Plate Number</label>
                <input
                  type="text"
                  placeholder="e.g. MH12DE1433"
                  value={plate}
                  onChange={(e) => setPlate(e.target.value.toUpperCase())}
                  className="w-full bg-slate-950 border border-border text-white text-xs rounded-lg px-3 py-2 outline-none focus:border-blue-500 font-mono uppercase"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Vehicle Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full bg-slate-950 border border-border text-white text-xs rounded-lg px-3 py-2 outline-none focus:border-blue-500 capitalize"
                >
                  <option value="car">Car / Sedan / SUV</option>
                  <option value="motorcycle">Motorcycle / Scooter</option>
                  <option value="truck">Truck / Pickup</option>
                  <option value="bus">Bus / Van</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Registered Color</label>
                <select
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="w-full bg-slate-950 border border-border text-white text-xs rounded-lg px-3 py-2 outline-none focus:border-blue-500 capitalize"
                >
                  <option value="white">White</option>
                  <option value="black">Black</option>
                  <option value="silver_grey">Silver / Grey</option>
                  <option value="red">Red</option>
                  <option value="blue">Blue</option>
                  <option value="yellow">Yellow</option>
                  <option value="green">Green</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Make</label>
                <input
                  type="text"
                  placeholder="e.g. Hyundai"
                  value={make}
                  onChange={(e) => setMake(e.target.value)}
                  className="w-full bg-slate-950 border border-border text-white text-xs rounded-lg px-3 py-2 outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Model</label>
                <input
                  type="text"
                  placeholder="e.g. i20"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-slate-950 border border-border text-white text-xs rounded-lg px-3 py-2 outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full bg-slate-950 border border-border text-white text-xs rounded-lg px-3 py-2 outline-none focus:border-blue-500"
                >
                  <option value="Active">Active</option>
                  <option value="Suspended">Suspended</option>
                  <option value="Flagged">Flagged</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-md shadow-blue-500/20"
              >
                Register Record
              </button>
            </div>
          </form>

          {/* Registered Vehicles Table */}
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
              Registered Vehicles ({vehicles.length})
            </h4>
            <div className="overflow-x-auto border border-border rounded-xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900 border-b border-border text-[11px] font-mono uppercase text-slate-400">
                  <tr>
                    <th className="py-2.5 px-3">Plate</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Color</th>
                    <th className="py-2.5 px-3">Make / Model</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40">
                  {vehicles.map((v) => (
                    <tr key={v.vehicle_id} className="hover:bg-slate-800/30 transition">
                      <td className="py-2.5 px-3 font-mono font-bold text-white">
                        {v.plate_number}
                      </td>
                      <td className="py-2.5 px-3 capitalize text-slate-300">{v.vehicle_type}</td>
                      <td className="py-2.5 px-3 capitalize text-slate-300">{v.color}</td>
                      <td className="py-2.5 px-3 text-slate-300">{v.make} {v.model}</td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${v.registration_status === 'Active' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}`}>
                          {v.registration_status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => handleDelete(v.vehicle_id, v.plate_number)}
                          className="text-slate-400 hover:text-rose-400 p-1 rounded hover:bg-slate-800 transition"
                          title="Delete vehicle"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
