import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { ProductionRecord } from '@/types';
import { formatDate, formatNumber } from '@/lib/utils';
import { Factory, TrendingUp, TrendingDown, Clock, AlertTriangle } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function ProductionPage() {
  const [records, setRecords] = useState<ProductionRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/production').then(res => {
      setRecords(Array.isArray(res.data) ? res.data : res.data.records || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const totalTarget = records.reduce((s, r) => s + r.target_tonnes, 0);
  const totalActual = records.reduce((s, r) => s + r.actual_tonnes, 0);
  const totalDowntime = records.reduce((s, r) => s + r.downtime_hours, 0);
  const totalIncidents = records.reduce((s, r) => s + r.safety_incidents, 0);
  const efficiency = totalTarget > 0 ? ((totalActual / totalTarget) * 100).toFixed(1) : '0';

  // Chart data: aggregate by date
  const dateMap = new Map<string, { date: string; target: number; actual: number }>();
  records.forEach(r => {
    const existing = dateMap.get(r.date) || { date: r.date, target: 0, actual: 0 };
    existing.target += r.target_tonnes;
    existing.actual += r.actual_tonnes;
    dateMap.set(r.date, existing);
  });
  const chartData = Array.from(dateMap.values()).sort((a, b) => a.date.localeCompare(b.date)).slice(-30);

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Production Intelligence</h1>
        <p className="text-sm text-gray-500 mt-0.5">Track production output, efficiency and anomalies across mining operations</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Total Target', value: `${formatNumber(totalTarget)} T`, icon: Factory, color: 'text-gray-700', bg: 'bg-gray-50' },
          { label: 'Total Actual', value: `${formatNumber(totalActual)} T`, icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50', sub: `${efficiency}% efficiency` },
          { label: 'Total Downtime', value: `${totalDowntime.toFixed(1)} hrs`, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Safety Incidents', value: totalIncidents.toString(), icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' },
        ].map(kpi => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="bg-white rounded-xl border border-gray-100 p-4 kpi-card">
              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded-lg ${kpi.bg} flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </div>
              <p className={`text-xl font-bold ${kpi.color}`}>{kpi.value}</p>
              <p className="text-xs text-gray-500 mt-0.5">{kpi.label}</p>
              {kpi.sub && <p className="text-[10px] text-emerald-600 font-medium mt-0.5">{kpi.sub}</p>}
            </div>
          );
        })}
      </div>

      {/* Target vs Actual Chart */}
      <div className="bg-white rounded-xl border border-gray-100 p-5">
        <h3 className="text-sm font-semibold text-gray-800 mb-4">Target vs Actual Production</h3>
        {loading ? <div className="skeleton h-48 w-full" /> : (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData} barSize={12}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="target" fill="#d1d5db" name="Target" radius={[2, 2, 0, 0]} />
              <Bar dataKey="actual" fill="#D99A24" name="Actual" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Production Records Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-800">Production Records</h3>
        </div>
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:5}).map((_,i)=><div key={i} className="skeleton h-10 w-full" />)}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Mine</th>
                <th className="text-center px-5 py-3 font-medium">Date</th>
                <th className="text-center px-5 py-3 font-medium hidden sm:table-cell">Shift</th>
                <th className="text-center px-5 py-3 font-medium">Target (T)</th>
                <th className="text-center px-5 py-3 font-medium">Actual (T)</th>
                <th className="text-center px-5 py-3 font-medium hidden md:table-cell">Efficiency</th>
                <th className="text-center px-5 py-3 font-medium hidden lg:table-cell">Downtime</th>
                <th className="text-center px-5 py-3 font-medium hidden lg:table-cell">Incidents</th>
              </tr></thead>
              <tbody>
                {records.slice(0, 50).map(r => {
                  const eff = r.target_tonnes > 0 ? ((r.actual_tonnes / r.target_tonnes) * 100) : 0;
                  return (
                    <tr key={r.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                      <td className="px-5 py-3 font-medium text-gray-800">{r.mine_name || `Mine #${r.mine_id}`}</td>
                      <td className="px-5 py-3 text-center text-gray-600">{formatDate(r.date)}</td>
                      <td className="px-5 py-3 text-center text-gray-600 capitalize hidden sm:table-cell">{r.shift}</td>
                      <td className="px-5 py-3 text-center text-gray-600">{formatNumber(r.target_tonnes)}</td>
                      <td className="px-5 py-3 text-center font-medium text-gray-800">{formatNumber(r.actual_tonnes)}</td>
                      <td className="px-5 py-3 text-center hidden md:table-cell">
                        <span className={`font-medium ${eff >= 90 ? 'text-emerald-600' : eff >= 70 ? 'text-amber-600' : 'text-red-600'}`}>{eff.toFixed(1)}%</span>
                      </td>
                      <td className="px-5 py-3 text-center text-gray-500 hidden lg:table-cell">{r.downtime_hours}h</td>
                      <td className="px-5 py-3 text-center hidden lg:table-cell">
                        {r.safety_incidents > 0 ? <span className="text-red-600 font-semibold">{r.safety_incidents}</span> : <span className="text-gray-300">0</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
