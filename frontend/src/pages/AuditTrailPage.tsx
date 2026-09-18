import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { AuditLog } from '@/types';
import { formatDateTime, getStatusColor, formatStatusLabel } from '@/lib/utils';
import { Activity, Search } from 'lucide-react';

export default function AuditTrailPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/audit').then(res => {
      setLogs(Array.isArray(res.data) ? res.data : res.data.logs || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = logs.filter(l =>
    !search || (l.user_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.details || '').toLowerCase().includes(search.toLowerCase()) ||
    l.module.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-5 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-900">Digital Audit Trail</h1><p className="text-sm text-gray-500 mt-0.5">Complete transparency and accountability log</p></div>

      <div className="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 max-w-md focus-within:border-amber-brand/50">
        <Search className="w-4 h-4 text-gray-400 mr-2" />
        <input type="text" placeholder="Search audit logs..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-sm outline-none w-full" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:8}).map((_,i)=><div key={i} className="skeleton h-10 w-full" />)}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">User</th>
                <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Role</th>
                <th className="text-center px-5 py-3 font-medium">Action</th>
                <th className="text-left px-5 py-3 font-medium">Module</th>
                <th className="text-left px-5 py-3 font-medium hidden lg:table-cell">Details</th>
                <th className="text-center px-5 py-3 font-medium">Status</th>
                <th className="text-left px-5 py-3 font-medium">Timestamp</th>
              </tr></thead>
              <tbody>
                {filtered.map(log => (
                  <tr key={log.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="px-5 py-3 font-medium text-gray-800">{log.user_name || '—'}</td>
                    <td className="px-5 py-3 text-gray-500 capitalize hidden md:table-cell">{log.user_role?.replace('_',' ') || '—'}</td>
                    <td className="px-5 py-3 text-center"><span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full capitalize">{log.action}</span></td>
                    <td className="px-5 py-3 text-gray-600 capitalize">{log.module}</td>
                    <td className="px-5 py-3 text-gray-500 text-xs max-w-xs truncate hidden lg:table-cell">{log.details || '—'}</td>
                    <td className="px-5 py-3 text-center"><span className={`text-xs px-2 py-1 rounded-full border font-medium ${getStatusColor(log.status)}`}>{log.status}</span></td>
                    <td className="px-5 py-3 text-gray-500 text-xs">{formatDateTime(log.created_at)}</td>
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
