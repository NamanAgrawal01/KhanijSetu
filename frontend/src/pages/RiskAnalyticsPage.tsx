import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { RiskData, Mine } from '@/types';
import { getRiskColor, getRiskLevel } from '@/lib/utils';
import { BarChart3, AlertTriangle, Sparkles, TrendingUp, RefreshCw } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function RiskAnalyticsPage() {
  const [mines, setMines] = useState<Mine[]>([]);
  const [selectedMine, setSelectedMine] = useState<number>(1);
  const [riskData, setRiskData] = useState<RiskData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/mines').then(res => {
      const list = Array.isArray(res.data) ? res.data : res.data.mines || [];
      setMines(list);
      if (list.length > 0) setSelectedMine(list.sort((a: Mine, b: Mine) => b.risk_score - a.risk_score)[0].id);
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedMine) return;
    setLoading(true);
    api.get(`/risk/${selectedMine}`).then(res => setRiskData(res.data)).catch(console.error).finally(() => setLoading(false));
  }, [selectedMine]);

  const mine = mines.find(m => m.id === selectedMine);

  // Recurring violations demo data
  const recurringViolations = [
    { title: 'PPE Non-Compliance', count: 4, inspections: '4 consecutive inspections', mines: 'Rajmahal, Godda East, Kathara Deep' },
    { title: 'Equipment Maintenance Delays', count: 3, inspections: '3 occurrences', mines: 'Kathara Deep, Bokaro Central' },
    { title: 'Environmental Reporting Gaps', count: 2, inspections: '2 occurrences', mines: 'Godda East' },
  ];

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Intelligence</h1>
          <p className="text-sm text-gray-500 mt-0.5">AI-powered risk scoring and analysis across mining operations</p>
        </div>
        <select value={selectedMine} onChange={e => setSelectedMine(+e.target.value)} className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none">
          {mines.sort((a, b) => b.risk_score - a.risk_score).map(m => (
            <option key={m.id} value={m.id}>{m.name} (Risk: {m.risk_score})</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="skeleton h-64 rounded-xl" />
          <div className="lg:col-span-2 skeleton h-64 rounded-xl" />
        </div>
      ) : riskData ? (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Risk Gauge */}
            <div className="bg-white rounded-xl border border-gray-100 p-6 flex flex-col items-center justify-center">
              <div className="relative w-48 h-24 mb-2">
                <svg viewBox="0 0 200 110" className="w-full h-full">
                  <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#e5e7eb" strokeWidth="12" strokeLinecap="round" />
                  <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={getRiskColor(riskData.risk_score)} strokeWidth="12" strokeLinecap="round"
                    strokeDasharray={`${(riskData.risk_score / 100) * 251} 251`} />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-end pb-0">
                  <span className="text-4xl font-bold" style={{ color: getRiskColor(riskData.risk_score) }}>{riskData.risk_score}</span>
                  <span className="text-xs text-gray-400">/ 100</span>
                </div>
              </div>
              <span className="text-lg font-bold mt-2" style={{ color: getRiskColor(riskData.risk_score) }}>{riskData.risk_level} RISK</span>
              <p className="text-xs text-gray-500 mt-1">{mine?.name}</p>
            </div>

            {/* Risk Factors */}
            <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="text-sm font-semibold text-gray-800 mb-4">Risk Contributing Factors</h3>
              <div className="space-y-3">
                {riskData.factors.map((f, i) => (
                  <div key={i}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-700">{f.factor}</span>
                      <span className="text-xs font-semibold text-gray-500">{f.weight}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className="h-2 rounded-full transition-all" style={{ width: `${f.weight}%`, backgroundColor: getRiskColor(f.weight * 2.5) }} />
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5">{f.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* AI Explanation */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-brand" /> AI Risk Explanation
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed">{riskData.explanation}</p>
            {riskData.recommendations?.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recommended Actions</p>
                {riskData.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start gap-2 p-2 bg-amber-50/50 rounded-lg">
                    <span className="text-amber-brand shrink-0 mt-0.5">→</span>
                    <p className="text-sm text-gray-700">{rec}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="text-sm font-semibold text-gray-800 mb-4">Risk Score Trend</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={riskData.trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#9ca3af" />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                  <Line type="monotone" dataKey="score" stroke="#ef4444" strokeWidth={2.5} dot={{ fill: '#ef4444', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="text-sm font-semibold text-gray-800 mb-4">Risk by Mine</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={mines.sort((a, b) => b.risk_score - a.risk_score).slice(0, 8)} barSize={24}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 9 }} stroke="#9ca3af" angle={-20} textAnchor="end" height={60} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                  <Bar dataKey="risk_score" radius={[4, 4, 0, 0]}>
                    {mines.map((m, i) => <Cell key={i} fill={getRiskColor(m.risk_score)} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recurring Violations */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-purple-600" /> Recurring Compliance Failures
            </h3>
            <div className="space-y-3">
              {recurringViolations.map((rv, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-purple-50/50 border border-purple-100 rounded-lg">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center shrink-0">
                    <span className="text-sm font-bold text-purple-700">{rv.count}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-800">{rv.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{rv.inspections} · Mines: {rv.mines}</p>
                  </div>
                </div>
              ))}
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-xs font-semibold text-amber-800 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" /> AI Insight
                </p>
                <p className="text-xs text-amber-700 mt-1">
                  Repeated PPE-related observations indicate a persistent compliance weakness.
                  Recommend targeted safety training program and increased inspection frequency at affected mines.
                </p>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
