import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import type { Mine } from '@/types';
import { getRiskColor, getRiskLevel, formatDate } from '@/lib/utils';
import { Mountain, MapPin, ShieldCheck, AlertTriangle, Leaf, Users, Factory, ArrowLeft, ExternalLink } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TABS = ['Overview', 'Compliance', 'Inspections', 'Violations', 'Documents', 'Contractors', 'Production'];

export default function MineProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [mine, setMine] = useState<Mine | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('Overview');

  useEffect(() => {
    if (!id) return;
    api.get(`/mines/${id}`).then(res => setMine(res.data)).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="skeleton h-8 w-48" />
        <div className="grid grid-cols-3 gap-4">{Array.from({length:6}).map((_,i)=><div key={i} className="skeleton h-24 w-full rounded-xl" />)}</div>
      </div>
    );
  }

  if (!mine) {
    return (
      <div className="text-center py-20">
        <Mountain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">Mine not found</p>
        <button onClick={() => navigate('/app/mines')} className="mt-4 text-amber-brand text-sm font-medium">← Back to Mines</button>
      </div>
    );
  }

  const kpis = [
    { label: 'Compliance', value: `${mine.compliance_score}%`, color: mine.compliance_score < 70 ? 'text-red-600' : 'text-emerald-600', icon: ShieldCheck, bg: 'bg-emerald-50' },
    { label: 'Risk Score', value: mine.risk_score, color: `text-[${getRiskColor(mine.risk_score)}]`, icon: AlertTriangle, bg: 'bg-orange-50', sub: getRiskLevel(mine.risk_score) },
    { label: 'Safety', value: `${mine.safety_score}%`, color: mine.safety_score < 70 ? 'text-red-600' : 'text-emerald-600', icon: ShieldCheck, bg: 'bg-blue-50' },
    { label: 'Environment', value: `${mine.environment_score}%`, color: 'text-emerald-600', icon: Leaf, bg: 'bg-green-50' },
    { label: 'Labour', value: `${mine.labour_score}%`, color: 'text-blue-600', icon: Users, bg: 'bg-blue-50' },
    { label: 'Production', value: `${mine.production_score}%`, color: 'text-purple-600', icon: Factory, bg: 'bg-purple-50' },
  ];

  const trendData = [
    { month: 'Apr', compliance: Math.max(50, mine.compliance_score - 12) },
    { month: 'May', compliance: Math.max(50, mine.compliance_score - 8) },
    { month: 'Jun', compliance: Math.max(50, mine.compliance_score - 5) },
    { month: 'Jul', compliance: Math.max(50, mine.compliance_score - 3) },
    { month: 'Aug', compliance: Math.max(50, mine.compliance_score - 1) },
    { month: 'Sep', compliance: mine.compliance_score },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <button onClick={() => navigate('/app/mines')} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-3">
          <ArrowLeft className="w-4 h-4" /> Back to Mines
        </button>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-amber-brand/10 flex items-center justify-center">
              <Mountain className="w-6 h-6 text-amber-brand" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{mine.name}</h1>
              <div className="flex items-center gap-3 text-sm text-gray-500 mt-0.5">
                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{mine.location}</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-medium">{mine.status}</span>
                <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: getRiskColor(mine.risk_score) + '20', color: getRiskColor(mine.risk_score) }}>
                  {getRiskLevel(mine.risk_score)} Risk
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/app/compliance')} className="text-sm bg-white border border-gray-200 px-3 py-2 rounded-lg hover:bg-gray-50 flex items-center gap-1.5">
              <ExternalLink className="w-3.5 h-3.5" /> View Compliance
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="bg-white rounded-xl border border-gray-100 p-4 kpi-card">
              <div className="flex items-center justify-between mb-2">
                <div className={`w-7 h-7 rounded-lg ${kpi.bg} flex items-center justify-center`}>
                  <Icon className="w-3.5 h-3.5 text-gray-500" />
                </div>
              </div>
              <p className={`text-xl font-bold ${kpi.color}`}>{kpi.value}</p>
              <p className="text-xs text-gray-500 mt-0.5">{kpi.label}</p>
              {kpi.sub && <p className="text-[10px] font-medium mt-0.5" style={{color: getRiskColor(mine.risk_score)}}>{kpi.sub}</p>}
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-1 overflow-x-auto">
          {TABS.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab ? 'border-amber-brand text-amber-brand' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'Overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Compliance Trend</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#9ca3af" />
                <YAxis domain={[40, 100]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }} />
                <Line type="monotone" dataKey="compliance" stroke="#D99A24" strokeWidth={2.5} dot={{ fill: '#D99A24', r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Mine Information</h3>
            <div className="space-y-3 text-sm">
              {[
                ['Mine Code', mine.code],
                ['Type', mine.mine_type],
                ['District', mine.district],
                ['State', mine.state],
                ['Manager', mine.manager_name || '—'],
                ['Workers', mine.num_workers?.toString()],
                ['Capacity', `${mine.capacity_mtpa} MTPA`],
                ['Open Violations', mine.open_violations?.toString()],
                ['Last Inspection', formatDate(mine.last_inspection_date)],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between py-1.5 border-b border-gray-50">
                  <span className="text-gray-500">{label}</span>
                  <span className="font-medium text-gray-800">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab !== 'Overview' && (
        <div className="bg-white rounded-xl border border-gray-100 p-8 text-center">
          <p className="text-gray-400 text-sm">Navigate to the {activeTab} module for detailed {activeTab.toLowerCase()} data for this mine.</p>
          <button onClick={() => navigate(`/app/${activeTab.toLowerCase().replace(' ', '-')}`)} className="mt-3 text-sm text-amber-brand font-medium hover:text-amber-hover">
            Go to {activeTab} →
          </button>
        </div>
      )}
    </div>
  );
}
