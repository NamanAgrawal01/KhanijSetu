import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { ComplianceRecord } from '@/types';
import { formatDate, getStatusColor, formatStatusLabel, getSeverityColor } from '@/lib/utils';
import { ShieldCheck, Search, Filter, Download, Upload, CheckCircle2 } from 'lucide-react';

const CATEGORIES = ['all', 'safety', 'environment', 'production', 'labour', 'equipment', 'documentation'];
const STATUSES = ['all', 'completed', 'pending', 'due_soon', 'overdue'];

export default function CompliancePage() {
  const [records, setRecords] = useState<ComplianceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('all');
  const [status, setStatus] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/compliance').then(res => {
      setRecords(Array.isArray(res.data) ? res.data : res.data.records || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = records.filter(r => {
    const matchCat = category === 'all' || r.category === category;
    const matchStatus = status === 'all' || r.status === status;
    const matchSearch = !search || (r.requirement_title || '').toLowerCase().includes(search.toLowerCase()) || (r.mine_name || '').toLowerCase().includes(search.toLowerCase());
    return matchCat && matchStatus && matchSearch;
  });

  const counts = {
    completed: records.filter(r => r.status === 'completed').length,
    pending: records.filter(r => r.status === 'pending').length,
    due_soon: records.filter(r => r.status === 'due_soon').length,
    overdue: records.filter(r => r.status === 'overdue').length,
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Compliance Management</h1>
          <p className="text-sm text-gray-500 mt-0.5">Track statutory and regulatory compliance across all mines</p>
        </div>
        <button className="flex items-center gap-1.5 text-sm text-white bg-amber-brand hover:bg-amber-hover px-3 py-2 rounded-lg font-medium">
          <Download className="w-4 h-4" /> Export
        </button>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Completed', count: counts.completed, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'Pending', count: counts.pending, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Due Soon', count: counts.due_soon, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Overdue', count: counts.overdue, color: 'text-red-600', bg: 'bg-red-50' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-100 p-4 kpi-card cursor-pointer" onClick={() => setStatus(s.label.toLowerCase().replace(' ', '_'))}>
            <p className={`text-2xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 flex-1 max-w-sm focus-within:border-amber-brand/50">
          <Search className="w-4 h-4 text-gray-400 mr-2" />
          <input type="text" placeholder="Search requirements..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-sm outline-none w-full" />
        </div>
        <select value={category} onChange={e => setCategory(e.target.value)} className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none">
          {CATEGORIES.map(c => <option key={c} value={c}>{c === 'all' ? 'All Categories' : c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
        </select>
        <select value={status} onChange={e => setStatus(e.target.value)} className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none">
          {STATUSES.map(s => <option key={s} value={s}>{s === 'all' ? 'All Statuses' : formatStatusLabel(s)}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:6}).map((_,i)=><div key={i} className="skeleton h-12 w-full" />)}</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center">
            <ShieldCheck className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">No compliance records found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Requirement</th>
                  <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Category</th>
                  <th className="text-left px-5 py-3 font-medium hidden lg:table-cell">Mine</th>
                  <th className="text-center px-5 py-3 font-medium">Due Date</th>
                  <th className="text-center px-5 py-3 font-medium">Status</th>
                  <th className="text-center px-5 py-3 font-medium hidden sm:table-cell">Risk</th>
                  <th className="text-left px-5 py-3 font-medium hidden xl:table-cell">Officer</th>
                  <th className="text-center px-5 py-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(r => (
                  <tr key={r.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="px-5 py-3.5">
                      <p className="font-medium text-gray-800">{r.requirement_title || `Requirement #${r.requirement_id}`}</p>
                    </td>
                    <td className="px-5 py-3.5 hidden md:table-cell">
                      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 capitalize">{r.category || '—'}</span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 hidden lg:table-cell">{r.mine_name || `Mine #${r.mine_id}`}</td>
                    <td className="px-5 py-3.5 text-center text-gray-600">{formatDate(r.due_date)}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getStatusColor(r.status)}`}>
                        {formatStatusLabel(r.status)}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center hidden sm:table-cell">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getSeverityColor(r.risk_level)}`}>
                        {formatStatusLabel(r.risk_level)}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 hidden xl:table-cell">{r.responsible_officer || '—'}</td>
                    <td className="px-5 py-3.5 text-center">
                      <div className="flex items-center justify-center gap-1">
                        {r.status !== 'completed' && (
                          <button className="text-xs text-emerald-600 font-medium hover:text-emerald-700 flex items-center gap-0.5">
                            <CheckCircle2 className="w-3 h-3" /> Complete
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
