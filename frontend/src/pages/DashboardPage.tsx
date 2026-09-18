import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import type { DashboardData } from '@/types';
import { formatStatusLabel, getRiskColor, getRiskLevel, timeAgo } from '@/lib/utils';
import {
  Mountain, ShieldCheck, AlertTriangle, AlertOctagon, Ban, Clock,
  TrendingUp, TrendingDown, RefreshCw, Download, Calendar,
  ChevronRight, Activity
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const KPI_CONFIG = [
  { key: 'total_mines', label: 'Total Mines', icon: Mountain, color: 'text-slate-700', bg: 'bg-slate-50' },
  { key: 'overall_compliance', label: 'Overall Compliance', icon: ShieldCheck, color: 'text-emerald-700', bg: 'bg-emerald-50', suffix: '%' },
  { key: 'high_risk_mines', label: 'High Risk Mines', icon: AlertTriangle, color: 'text-orange-700', bg: 'bg-orange-50' },
  { key: 'critical_issues', label: 'Critical Issues', icon: AlertOctagon, color: 'text-red-700', bg: 'bg-red-50' },
  { key: 'open_violations', label: 'Open Violations', icon: Ban, color: 'text-amber-700', bg: 'bg-amber-50' },
  { key: 'pending_actions', label: 'Pending Actions', icon: Clock, color: 'text-blue-700', bg: 'bg-blue-50' },
];

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const res = await api.get('/dashboard/overview');
      setData(res.data);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDashboard(); }, []);

  if (loading || !data) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-100 p-4 h-28">
              <div className="skeleton h-4 w-24 mb-3" />
              <div className="skeleton h-8 w-16 mb-2" />
              <div className="skeleton h-3 w-20" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-100 p-6 h-72">
              <div className="skeleton h-5 w-40 mb-4" />
              <div className="skeleton h-48 w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Governance Overview</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Real-time compliance, safety and operational intelligence across mining operations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-50">
            <Calendar className="w-4 h-4" /> Last 30 days
          </button>
          <button onClick={fetchDashboard} className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">
            <RefreshCw className="w-4 h-4 text-gray-600" />
          </button>
          <button className="flex items-center gap-1.5 text-sm text-white bg-amber-brand hover:bg-amber-hover px-3 py-1.5 rounded-lg font-medium">
            <Download className="w-4 h-4" /> Export
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {KPI_CONFIG.map((kpi) => {
          const Icon = kpi.icon;
          const value = (data as any)[kpi.key];
          return (
            <div key={kpi.key} className="kpi-card bg-white rounded-xl border border-gray-100 p-4 cursor-pointer" onClick={() => {
              if (kpi.key === 'open_violations') navigate('/app/violations');
              if (kpi.key === 'high_risk_mines') navigate('/app/risk');
              if (kpi.key === 'pending_actions') navigate('/app/corrective-actions');
            }}>
              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded-lg ${kpi.bg} flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
                {kpi.key === 'overall_compliance' && <TrendingUp className="w-4 h-4 text-emerald-500" />}
                {kpi.key === 'high_risk_mines' && <TrendingUp className="w-4 h-4 text-red-500" />}
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {typeof value === 'number' && kpi.suffix ? value.toFixed(1) : value}
                {kpi.suffix || ''}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">{kpi.label}</p>
              {kpi.key === 'overall_compliance' && (
                <p className="text-[10px] text-emerald-600 font-medium mt-1">↑ 4.2% vs last month</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Compliance Trend */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Compliance Trend (6 months)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.compliance_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <YAxis domain={[60, 100]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }} />
              <Line type="monotone" dataKey="compliance" stroke="#D99A24" strokeWidth={2.5} dot={{ fill: '#D99A24', r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Compliance by Category */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Compliance by Category</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.compliance_by_category} barSize={32}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="category" tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }} />
              <Bar dataKey="score" fill="#D99A24" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Risk Distribution */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Risk Distribution</h3>
          <div className="flex items-center">
            <ResponsiveContainer width="50%" height={200}>
              <PieChart>
                <Pie
                  data={data.risk_distribution}
                  cx="50%" cy="50%"
                  innerRadius={50} outerRadius={80}
                  paddingAngle={3} dataKey="count"
                >
                  {data.risk_distribution.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {data.risk_distribution.map((item) => (
                <div key={item.level} className="flex items-center gap-2 text-sm">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-gray-600">{item.level}</span>
                  <span className="font-semibold text-gray-800 ml-auto">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Violations by Category */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Violations by Category</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.violations_by_category} layout="vertical" barSize={20}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <YAxis type="category" dataKey="category" tick={{ fontSize: 11 }} stroke="#9ca3af" width={90} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }} />
              <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* High-Risk Mines Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-800">High-Risk Mines</h3>
          <button onClick={() => navigate('/app/mines')} className="text-xs text-amber-brand font-medium hover:text-amber-hover flex items-center gap-1">
            View all <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Mine</th>
                <th className="text-left px-5 py-3 font-medium hidden md:table-cell">Location</th>
                <th className="text-center px-5 py-3 font-medium">Compliance</th>
                <th className="text-center px-5 py-3 font-medium">Risk</th>
                <th className="text-center px-5 py-3 font-medium hidden sm:table-cell">Violations</th>
                <th className="text-left px-5 py-3 font-medium hidden lg:table-cell">Last Inspection</th>
                <th className="text-center px-5 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {data.high_risk_mine_list.map((mine) => (
                <tr key={mine.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors cursor-pointer" onClick={() => navigate(`/app/mines/${mine.id}`)}>
                  <td className="px-5 py-3">
                    <p className="font-medium text-gray-800">{mine.name}</p>
                    <p className="text-xs text-gray-400">{mine.subsidiary_name}</p>
                  </td>
                  <td className="px-5 py-3 text-gray-600 hidden md:table-cell">{mine.location}</td>
                  <td className="px-5 py-3 text-center">
                    <span className={`text-sm font-semibold ${mine.compliance_score < 70 ? 'text-red-600' : mine.compliance_score < 85 ? 'text-amber-600' : 'text-emerald-600'}`}>
                      {mine.compliance_score}%
                    </span>
                  </td>
                  <td className="px-5 py-3 text-center">
                    <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full" style={{ backgroundColor: getRiskColor(mine.risk_score) + '20', color: getRiskColor(mine.risk_score) }}>
                      {mine.risk_score}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-center text-gray-600 hidden sm:table-cell">{mine.open_violations}</td>
                  <td className="px-5 py-3 text-gray-500 text-xs hidden lg:table-cell">{mine.last_inspection}</td>
                  <td className="px-5 py-3 text-center">
                    <button className="text-xs text-amber-brand font-medium hover:text-amber-hover">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl border border-gray-100 p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-800">Recent Activity</h3>
          <button onClick={() => navigate('/app/audit')} className="text-xs text-amber-brand font-medium hover:text-amber-hover flex items-center gap-1">
            View all <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="space-y-3">
          {data.recent_activity.slice(0, 6).map((event) => (
            <div key={event.id} className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${event.status === 'warning' ? 'bg-amber-50' : 'bg-emerald-50'}`}>
                <Activity className={`w-4 h-4 ${event.status === 'warning' ? 'text-amber-600' : 'text-emerald-600'}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700">{event.details}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-gray-400">{event.user}</span>
                  <span className="text-xs text-gray-300">·</span>
                  <span className="text-xs text-gray-400">{timeAgo(event.time)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
