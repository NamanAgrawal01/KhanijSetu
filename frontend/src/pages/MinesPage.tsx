import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import type { Mine } from '@/types';
import { getRiskColor, getRiskLevel, formatDate, getStatusColor, formatStatusLabel } from '@/lib/utils';
import { Mountain, Search, Filter, Plus, Download, ChevronRight, MapPin } from 'lucide-react';

export default function MinesPage() {
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/mines').then(res => {
      setMines(Array.isArray(res.data) ? res.data : res.data.mines || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = mines.filter(m => {
    const matchSearch = m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.location?.toLowerCase().includes(search.toLowerCase());
    const matchRisk = riskFilter === 'all' ||
      (riskFilter === 'high' && m.risk_score >= 70) ||
      (riskFilter === 'medium' && m.risk_score >= 40 && m.risk_score < 70) ||
      (riskFilter === 'low' && m.risk_score < 40);
    return matchSearch && matchRisk;
  });

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mines</h1>
          <p className="text-sm text-gray-500 mt-0.5">Manage and monitor all mining operations</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 text-sm text-white bg-amber-brand hover:bg-amber-hover px-3 py-2 rounded-lg font-medium">
            <Plus className="w-4 h-4" /> Add Mine
          </button>
          <button className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border border-gray-200 px-3 py-2 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4" /> Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 flex-1 max-w-md focus-within:border-amber-brand/50">
          <Search className="w-4 h-4 text-gray-400 mr-2" />
          <input type="text" placeholder="Search mines..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-sm outline-none w-full" />
        </div>
        <select value={riskFilter} onChange={e => setRiskFilter(e.target.value)} className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-600 outline-none">
          <option value="all">All Risk Levels</option>
          <option value="high">High Risk</option>
          <option value="medium">Medium Risk</option>
          <option value="low">Low Risk</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length: 5}).map((_, i) => <div key={i} className="skeleton h-12 w-full" />)}</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center">
            <Mountain className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">No mines found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                  <th className="text-left px-5 py-3 font-medium">Mine Name</th>
                  <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Location</th>
                  <th className="text-left px-5 py-3 font-medium hidden lg:table-cell">Manager</th>
                  <th className="text-center px-5 py-3 font-medium">Type</th>
                  <th className="text-center px-5 py-3 font-medium">Compliance</th>
                  <th className="text-center px-5 py-3 font-medium">Risk</th>
                  <th className="text-center px-5 py-3 font-medium hidden sm:table-cell">Violations</th>
                  <th className="text-center px-5 py-3 font-medium hidden lg:table-cell">Status</th>
                  <th className="text-center px-5 py-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(mine => (
                  <tr key={mine.id} className="border-b border-gray-50 hover:bg-gray-50/50 cursor-pointer transition-colors" onClick={() => navigate(`/app/mines/${mine.id}`)}>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0">
                          <Mountain className="w-4 h-4 text-slate-500" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">{mine.name}</p>
                          <p className="text-xs text-gray-400">{mine.code}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 hidden md:table-cell">
                      <div className="flex items-center gap-1 text-gray-600">
                        <MapPin className="w-3 h-3 text-gray-400" /> {mine.location}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 hidden lg:table-cell">{mine.manager_name || '—'}</td>
                    <td className="px-5 py-3.5 text-center">
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">{mine.mine_type}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`font-semibold ${mine.compliance_score < 70 ? 'text-red-600' : mine.compliance_score < 85 ? 'text-amber-600' : 'text-emerald-600'}`}>
                        {mine.compliance_score}%
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full" style={{ backgroundColor: getRiskColor(mine.risk_score) + '20', color: getRiskColor(mine.risk_score) }}>
                        {mine.risk_score}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center text-gray-600 hidden sm:table-cell">{mine.open_violations}</td>
                    <td className="px-5 py-3.5 text-center hidden lg:table-cell">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${getStatusColor(mine.status)}`}>
                        {formatStatusLabel(mine.status)}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <button className="text-xs text-amber-brand font-medium hover:text-amber-hover">View</button>
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
