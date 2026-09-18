import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { Inspection } from '@/types';
import { formatDate, getStatusColor, formatStatusLabel } from '@/lib/utils';
import { ClipboardCheck, Plus, Search, Calendar, MapPin, Loader2 } from 'lucide-react';

export default function InspectionsPage() {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [form, setForm] = useState({ mine_id: 1, inspector_id: 3, inspection_type: 'routine', scheduled_date: '', priority: 'normal' });

  const fetchInspections = () => {
    setLoading(true);
    api.get('/inspections').then(res => {
      setInspections(Array.isArray(res.data) ? res.data : res.data.inspections || []);
    }).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchInspections(); }, []);

  const counts = {
    scheduled: inspections.filter(i => i.status === 'scheduled').length,
    in_progress: inspections.filter(i => i.status === 'in_progress').length,
    completed: inspections.filter(i => i.status === 'completed').length,
    overdue: inspections.filter(i => i.status === 'overdue').length,
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.scheduled_date) return;
    setFormLoading(true);
    try {
      await api.post('/inspections', form);
      setShowForm(false);
      fetchInspections();
    } catch (err) { console.error(err); }
    setFormLoading(false);
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inspections</h1>
          <p className="text-sm text-gray-500 mt-0.5">Schedule, manage and track mine inspections</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-1.5 text-sm text-white bg-amber-brand hover:bg-amber-hover px-3 py-2 rounded-lg font-medium">
          <Plus className="w-4 h-4" /> Schedule Inspection
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Scheduled', count: counts.scheduled, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'In Progress', count: counts.in_progress, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Completed', count: counts.completed, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'Overdue', count: counts.overdue, color: 'text-red-600', bg: 'bg-red-50' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-100 p-4 kpi-card">
            <p className={`text-2xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:5}).map((_,i)=><div key={i} className="skeleton h-12 w-full" />)}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Mine</th>
                  <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Inspector</th>
                  <th className="text-center px-5 py-3 font-medium">Type</th>
                  <th className="text-center px-5 py-3 font-medium">Date</th>
                  <th className="text-center px-5 py-3 font-medium">Priority</th>
                  <th className="text-center px-5 py-3 font-medium">Status</th>
                  <th className="text-center px-5 py-3 font-medium hidden lg:table-cell">Rating</th>
                </tr>
              </thead>
              <tbody>
                {inspections.map(insp => (
                  <tr key={insp.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="px-5 py-3.5 font-medium text-gray-800">{insp.mine_name || `Mine #${insp.mine_id}`}</td>
                    <td className="px-5 py-3.5 text-gray-600 hidden md:table-cell">{insp.inspector_name || `Inspector #${insp.inspector_id}`}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full capitalize">{insp.inspection_type}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center text-gray-600">{formatDate(insp.scheduled_date)}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${
                        insp.priority === 'urgent' ? 'bg-red-100 text-red-700 border-red-200' :
                        insp.priority === 'high' ? 'bg-orange-100 text-orange-700 border-orange-200' :
                        'bg-gray-100 text-gray-600 border-gray-200'
                      }`}>{insp.priority}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getStatusColor(insp.status)}`}>{formatStatusLabel(insp.status)}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center text-gray-600 capitalize hidden lg:table-cell">{insp.overall_rating?.replace('_', ' ') || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Schedule Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowForm(false)} />
          <div className="relative bg-white rounded-2xl shadow-xl max-w-md w-full p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Schedule Inspection</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mine</label>
                <select value={form.mine_id} onChange={e => setForm({...form, mine_id: +e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-amber-brand">
                  {Array.from({length:8}).map((_,i)=><option key={i+1} value={i+1}>Mine #{i+1}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Inspection Type</label>
                <select value={form.inspection_type} onChange={e => setForm({...form, inspection_type: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-amber-brand">
                  {['routine','safety','environmental','special','follow_up'].map(t=><option key={t} value={t}>{t.replace('_',' ')}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Scheduled Date</label>
                <input type="date" value={form.scheduled_date} onChange={e => setForm({...form, scheduled_date: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-amber-brand" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-amber-brand">
                  {['low','normal','high','urgent'].map(p=><option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div className="flex gap-2 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 text-sm bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 font-medium">Cancel</button>
                <button type="submit" disabled={formLoading} className="flex-1 text-sm bg-amber-brand text-white py-2 rounded-lg hover:bg-amber-hover font-medium flex items-center justify-center gap-1 disabled:opacity-60">
                  {formLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />} Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
