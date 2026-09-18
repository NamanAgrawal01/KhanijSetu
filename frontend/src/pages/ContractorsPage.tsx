import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { Contractor } from '@/types';
import { formatDate, getStatusColor, formatStatusLabel, getSeverityColor } from '@/lib/utils';
import { Users, Search, ShieldCheck, AlertTriangle, Calendar, Star } from 'lucide-react';

export default function ContractorsPage() {
  const [contractors, setContractors] = useState<Contractor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/contractors').then(res => {
      setContractors(Array.isArray(res.data) ? res.data : res.data.contractors || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const stats = {
    total: contractors.length,
    active: contractors.filter(c => c.status === 'active').length,
    expiring: contractors.filter(c => c.compliance_status === 'expiring').length,
    nonCompliant: contractors.filter(c => c.compliance_status === 'non_compliant').length,
  };

  const filtered = contractors.filter(c =>
    !search || c.name.toLowerCase().includes(search.toLowerCase()) || (c.company || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-5 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-900">Contractor Management</h1><p className="text-sm text-gray-500 mt-0.5">Monitor contractor compliance, safety performance and workforce</p></div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total Contractors', value: stats.total, color: 'text-gray-700', bg: 'bg-gray-50' },
          { label: 'Active', value: stats.active, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'Expiring Soon', value: stats.expiring, color: 'text-orange-600', bg: 'bg-orange-50' },
          { label: 'Non-Compliant', value: stats.nonCompliant, color: 'text-red-600', bg: 'bg-red-50' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-100 p-4 kpi-card">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 max-w-md focus-within:border-amber-brand/50">
        <Search className="w-4 h-4 text-gray-400 mr-2" />
        <input type="text" placeholder="Search contractors..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-sm outline-none w-full" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:5}).map((_,i)=><div key={i} className="skeleton h-12 w-full" />)}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Contractor</th>
                <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Company</th>
                <th className="text-left px-5 py-3 font-medium hidden lg:table-cell">Mine</th>
                <th className="text-center px-5 py-3 font-medium">Workers</th>
                <th className="text-center px-5 py-3 font-medium">Safety</th>
                <th className="text-center px-5 py-3 font-medium hidden sm:table-cell">Violations</th>
                <th className="text-center px-5 py-3 font-medium">Compliance</th>
                <th className="text-center px-5 py-3 font-medium hidden lg:table-cell">Contract End</th>
              </tr></thead>
              <tbody>
                {filtered.map(c => (
                  <tr key={c.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="px-5 py-3.5 font-medium text-gray-800">{c.name}</td>
                    <td className="px-5 py-3.5 text-gray-600 hidden md:table-cell">{c.company || '—'}</td>
                    <td className="px-5 py-3.5 text-gray-600 hidden lg:table-cell">{c.mine_name || `Mine #${c.mine_id}`}</td>
                    <td className="px-5 py-3.5 text-center text-gray-600">{c.num_workers}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`font-semibold ${c.safety_score >= 80 ? 'text-emerald-600' : c.safety_score >= 60 ? 'text-amber-600' : 'text-red-600'}`}>{c.safety_score}%</span>
                    </td>
                    <td className="px-5 py-3.5 text-center text-gray-600 hidden sm:table-cell">{c.violation_count}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getStatusColor(c.compliance_status)}`}>{formatStatusLabel(c.compliance_status)}</span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 text-center hidden lg:table-cell">{formatDate(c.contract_end)}</td>
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
