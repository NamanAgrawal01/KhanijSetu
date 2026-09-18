import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import type { Violation } from '@/types';
import { formatDate, getStatusColor, formatStatusLabel, getSeverityColor } from '@/lib/utils';
import { AlertTriangle, Search, Plus, Download, RefreshCw, ChevronRight, AlertOctagon } from 'lucide-react';

const STATUS_FLOW = ['detected', 'assigned', 'in_progress', 'resolved', 'verified', 'closed'];

export default function ViolationsPage() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedViolation, setSelectedViolation] = useState<Violation | null>(null);
  const navigate = useNavigate();

  const fetchViolations = () => {
    setLoading(true);
    api.get('/violations').then(res => {
      setViolations(Array.isArray(res.data) ? res.data : res.data.violations || []);
    }).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchViolations(); }, []);

  const filtered = violations.filter(v => {
    const matchSearch = !search || v.title.toLowerCase().includes(search.toLowerCase()) || v.violation_code.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || v.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const updateStatus = async (id: number, newStatus: string) => {
    try {
      await api.put(`/violations/${id}`, { status: newStatus });
      fetchViolations();
      setSelectedViolation(null);
    } catch (err) { console.error(err); }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Violations</h1>
          <p className="text-sm text-gray-500 mt-0.5">Track and manage compliance violations across mining operations</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 text-sm text-white bg-amber-brand hover:bg-amber-hover px-3 py-2 rounded-lg font-medium">
            <Plus className="w-4 h-4" /> Report Violation
          </button>
        </div>
      </div>

      {/* Lifecycle */}
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <p className="text-xs text-gray-400 mb-3 font-medium uppercase tracking-wider">Violation Lifecycle</p>
        <div className="flex items-center gap-1 overflow-x-auto pb-1">
          {STATUS_FLOW.map((s, i) => (
            <div key={s} className="flex items-center gap-1">
              <button
                onClick={() => setStatusFilter(statusFilter === s ? 'all' : s)}
                className={`text-xs px-3 py-1.5 rounded-full font-medium whitespace-nowrap border transition-colors ${
                  statusFilter === s ? 'bg-amber-brand text-white border-amber-brand' : `${getStatusColor(s)}`
                }`}
              >
                {formatStatusLabel(s)} ({violations.filter(v => v.status === s).length})
              </button>
              {i < STATUS_FLOW.length - 1 && <ChevronRight className="w-3.5 h-3.5 text-gray-300 shrink-0" />}
            </div>
          ))}
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 max-w-md focus-within:border-amber-brand/50">
        <Search className="w-4 h-4 text-gray-400 mr-2" />
        <input type="text" placeholder="Search violations..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-sm outline-none w-full" />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:6}).map((_,i)=><div key={i} className="skeleton h-12 w-full" />)}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Code</th>
                  <th className="text-left px-5 py-3 font-medium">Title</th>
                  <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Mine</th>
                  <th className="text-center px-5 py-3 font-medium">Severity</th>
                  <th className="text-center px-5 py-3 font-medium">Status</th>
                  <th className="text-left px-5 py-3 font-medium hidden lg:table-cell">Detected</th>
                  <th className="text-left px-5 py-3 font-medium hidden xl:table-cell">Assigned To</th>
                  <th className="text-center px-5 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(v => (
                  <tr key={v.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <span className="text-xs font-mono text-gray-500">{v.violation_code}</span>
                      {v.is_recurring && <span className="ml-1.5 text-[10px] bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full font-medium">×{v.recurrence_count}</span>}
                    </td>
                    <td className="px-5 py-3.5">
                      <p className="font-medium text-gray-800 max-w-xs truncate">{v.title}</p>
                      <p className="text-xs text-gray-400 capitalize">{v.category}</p>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 hidden md:table-cell">{v.mine_name || `Mine #${v.mine_id}`}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getSeverityColor(v.severity)}`}>{formatStatusLabel(v.severity)}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getStatusColor(v.status)}`}>{formatStatusLabel(v.status)}</span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 hidden lg:table-cell">{formatDate(v.detected_date)}</td>
                    <td className="px-5 py-3.5 text-gray-600 hidden xl:table-cell">{v.assigned_to_name || '—'}</td>
                    <td className="px-5 py-3.5 text-center">
                      <button onClick={() => setSelectedViolation(v)} className="text-xs text-amber-brand font-medium hover:text-amber-hover">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Violation Detail Modal */}
      {selectedViolation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedViolation(null)} />
          <div className="relative bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-6 animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-xs font-mono text-gray-400">{selectedViolation.violation_code}</span>
                <h3 className="text-lg font-bold text-gray-900 mt-1">{selectedViolation.title}</h3>
              </div>
              <button onClick={() => setSelectedViolation(null)} className="text-gray-400 hover:text-gray-600 text-lg">✕</button>
            </div>
            <div className="space-y-3 text-sm">
              <p className="text-gray-600">{selectedViolation.description}</p>
              <div className="grid grid-cols-2 gap-3 pt-3 border-t">
                {[
                  ['Category', selectedViolation.category],
                  ['Severity', selectedViolation.severity],
                  ['Status', selectedViolation.status],
                  ['Mine', selectedViolation.mine_name || `Mine #${selectedViolation.mine_id}`],
                  ['Reported By', selectedViolation.reported_by_name || '—'],
                  ['Assigned To', selectedViolation.assigned_to_name || '—'],
                  ['Detected', formatDate(selectedViolation.detected_date)],
                  ['Deadline', formatDate(selectedViolation.deadline)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <p className="text-xs text-gray-400">{label}</p>
                    <p className="font-medium text-gray-700 capitalize">{value}</p>
                  </div>
                ))}
              </div>
              {selectedViolation.is_recurring && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mt-3">
                  <p className="text-xs font-semibold text-purple-800">⚠ Recurring Violation — {selectedViolation.recurrence_count} occurrences</p>
                  <p className="text-xs text-purple-600 mt-1">This violation has been observed in multiple inspections, indicating a persistent compliance issue.</p>
                </div>
              )}
              <div className="flex gap-2 pt-3">
                {selectedViolation.status === 'detected' && (
                  <button onClick={() => updateStatus(selectedViolation.id, 'assigned')} className="flex-1 text-sm bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium">Assign</button>
                )}
                {selectedViolation.status === 'assigned' && (
                  <button onClick={() => updateStatus(selectedViolation.id, 'in_progress')} className="flex-1 text-sm bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium">Start Progress</button>
                )}
                {selectedViolation.status === 'in_progress' && (
                  <button onClick={() => updateStatus(selectedViolation.id, 'resolved')} className="flex-1 text-sm bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-medium">Mark Resolved</button>
                )}
                {selectedViolation.status === 'resolved' && (
                  <button onClick={() => updateStatus(selectedViolation.id, 'verified')} className="flex-1 text-sm bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-medium">Verify</button>
                )}
                <button onClick={() => navigate('/app/corrective-actions')} className="text-sm bg-white border border-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 font-medium">
                  Corrective Actions
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
