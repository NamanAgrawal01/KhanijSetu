import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import type { Mine } from '@/types';
import { getRiskColor, getRiskLevel, formatDate, getStatusColor, formatStatusLabel } from '@/lib/utils';
import {
  Mountain, Search, Filter, Plus, Download, ChevronRight, MapPin,
  ChevronLeft, ChevronDown, AlertTriangle, CheckCircle, TrendingUp,
  Users, Building2, Globe, Layers, RefreshCw, X, SortAsc, SortDesc,
  Shield, Zap, Activity, Info
} from 'lucide-react';

const SUBSIDIARY_COLORS: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  ECL:  { bg: 'bg-blue-50',    text: 'text-blue-700',   border: 'border-blue-200',  dot: 'bg-blue-500' },
  BCCL: { bg: 'bg-orange-50',  text: 'text-orange-700', border: 'border-orange-200',dot: 'bg-orange-500' },
  CCL:  { bg: 'bg-purple-50',  text: 'text-purple-700', border: 'border-purple-200',dot: 'bg-purple-500' },
  MCL:  { bg: 'bg-teal-50',    text: 'text-teal-700',   border: 'border-teal-200',  dot: 'bg-teal-500' },
  SECL: { bg: 'bg-red-50',     text: 'text-red-700',    border: 'border-red-200',   dot: 'bg-red-500' },
  WCL:  { bg: 'bg-yellow-50',  text: 'text-yellow-700', border: 'border-yellow-200',dot: 'bg-yellow-500' },
  NCL:  { bg: 'bg-green-50',   text: 'text-green-700',  border: 'border-green-200', dot: 'bg-green-500' },
  NEC:  { bg: 'bg-pink-50',    text: 'text-pink-700',   border: 'border-pink-200',  dot: 'bg-pink-500' },
};

function getSubsidiaryCode(subsidiaryName: string | undefined): string {
  if (!subsidiaryName) return '';
  const codes = ['ECL', 'BCCL', 'CCL', 'MCL', 'SECL', 'WCL', 'NCL', 'NEC'];
  for (const code of codes) {
    if (subsidiaryName.includes(code)) return code;
  }
  return '';
}

function SubsidiaryBadge({ name }: { name?: string }) {
  const code = getSubsidiaryCode(name);
  const colors = SUBSIDIARY_COLORS[code] || { bg: 'bg-gray-50', text: 'text-gray-600', border: 'border-gray-200', dot: 'bg-gray-400' };
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border ${colors.bg} ${colors.text} ${colors.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${colors.dot}`} />
      {code || name}
    </span>
  );
}

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 rounded-full bg-gray-100 overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-semibold w-8 text-right" style={{ color }}>{Math.round(value)}%</span>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, sub, color }: {
  icon: any; label: string; value: string | number; sub?: string; color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-3 shadow-sm hover:shadow-md transition-shadow">
      <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: color + '18' }}>
        <Icon className="w-5 h-5" style={{ color }} />
      </div>
      <div>
        <p className="text-xs text-gray-500 font-medium">{label}</p>
        <p className="text-xl font-bold text-gray-900 leading-tight">{value}</p>
        {sub && <p className="text-xs text-gray-400">{sub}</p>}
      </div>
    </div>
  );
}

const PAGE_SIZE_OPTIONS = [25, 50, 100];

export default function MinesPage() {
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [stateFilter, setStateFilter] = useState('all');
  const [subsidiaryFilter, setSubsidiaryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [mineTypeFilter, setMineTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name_asc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [showFilters, setShowFilters] = useState(false);
  const [dataClassFilter, setDataClassFilter] = useState('all');
  const navigate = useNavigate();

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => { setDebouncedSearch(search); setPage(1); }, 350);
    return () => clearTimeout(t);
  }, [search]);

  const fetchMines = useCallback(() => {
    setLoading(true);
    const params: any = {
      skip: (page - 1) * pageSize,
      limit: pageSize,
      sort_by: sortBy,
    };
    if (debouncedSearch) params.search = debouncedSearch;
    if (stateFilter !== 'all') params.state = stateFilter;
    if (statusFilter !== 'all') params.status = statusFilter;
    if (mineTypeFilter !== 'all') params.mine_type = mineTypeFilter;
    if (riskFilter !== 'all') params.risk_level = riskFilter;

    api.get('/mines', { params })
      .then(res => {
        const data = res.data;
        const minesList: Mine[] = Array.isArray(data) ? data : (data.mines || []);
        const totalCount: number = data.total ?? minesList.length;
        setMines(minesList);
        setTotal(totalCount);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page, pageSize, debouncedSearch, riskFilter, stateFilter, statusFilter, mineTypeFilter, sortBy]);

  useEffect(() => { fetchMines(); }, [fetchMines]);

  // Client-side filtering for subsidiary (not supported by API yet)
  const filtered = subsidiaryFilter === 'all'
    ? mines
    : mines.filter(m => {
        const code = getSubsidiaryCode((m as any).subsidiary_name);
        return code === subsidiaryFilter;
      });

  // Stats from current page
  const totalPages = Math.ceil(total / pageSize);
  const operationalCount = mines.filter(m => m.status === 'operational').length;
  const highRiskCount = mines.filter(m => m.risk_score >= 70).length;
  const avgCompliance = mines.length > 0 ? Math.round(mines.reduce((a, m) => a + m.compliance_score, 0) / mines.length) : 0;
  const totalWorkers = mines.reduce((a, m) => a + (m.num_workers || 0), 0);

  const STATES = [
    'all','Jharkhand','West Bengal','Odisha','Chhattisgarh','Madhya Pradesh',
    'Maharashtra','Uttar Pradesh','Assam','Arunachal Pradesh',
  ];
  const SUBSIDIARIES = ['all','ECL','BCCL','CCL','MCL','SECL','WCL','NCL','NEC'];
  const SORT_OPTIONS = [
    { value: 'name_asc', label: 'Name A-Z' },
    { value: 'name_desc', label: 'Name Z-A' },
    { value: 'risk_desc', label: 'Risk: High First' },
    { value: 'risk_asc', label: 'Risk: Low First' },
    { value: 'compliance_desc', label: 'Compliance: Best First' },
    { value: 'compliance_asc', label: 'Compliance: Worst First' },
    { value: 'violations_desc', label: 'Violations: Most First' },
  ];

  const activeFiltersCount = [
    riskFilter !== 'all', stateFilter !== 'all', statusFilter !== 'all',
    mineTypeFilter !== 'all', subsidiaryFilter !== 'all'
  ].filter(Boolean).length;

  const clearFilters = () => {
    setRiskFilter('all'); setStateFilter('all'); setStatusFilter('all');
    setMineTypeFilter('all'); setSubsidiaryFilter('all'); setSearch('');
    setPage(1);
  };

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Mountain className="w-6 h-6 text-amber-500" />
            Coal Mines Database
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {total} mines across all CIL subsidiaries — official public data
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchMines}
            className="flex items-center gap-1.5 text-sm text-gray-500 bg-white border border-gray-200 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border border-gray-200 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-4 h-4" /> Export
          </button>
          <button className="flex items-center gap-1.5 text-sm text-white bg-amber-500 hover:bg-amber-600 px-3 py-2 rounded-lg font-medium transition-colors">
            <Plus className="w-4 h-4" /> Add Mine
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard icon={Mountain} label="Total Mines" value={total} sub="All subsidiaries" color="#f59e0b" />
        <StatCard icon={CheckCircle} label="Operational" value={operationalCount} sub={`${Math.round((operationalCount/Math.max(mines.length,1))*100)}% of page`} color="#10b981" />
        <StatCard icon={AlertTriangle} label="High Risk" value={highRiskCount} sub="Risk score ≥ 70" color="#ef4444" />
        <StatCard icon={TrendingUp} label="Avg Compliance" value={`${avgCompliance}%`} sub="Current page" color="#6366f1" />
      </div>

      {/* Search, Filters Row */}
      <div className="bg-white rounded-xl border border-gray-100 p-4 space-y-3 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="flex items-center bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 flex-1 focus-within:border-amber-400 focus-within:bg-white transition-colors">
            <Search className="w-4 h-4 text-gray-400 mr-2 shrink-0" />
            <input
              type="text"
              placeholder="Search mines by name, location, code..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="bg-transparent text-sm outline-none w-full text-gray-800 placeholder-gray-400"
            />
            {search && (
              <button onClick={() => setSearch('')} className="ml-1 text-gray-400 hover:text-gray-600">
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <select
              value={sortBy}
              onChange={e => { setSortBy(e.target.value); setPage(1); }}
              className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-600 outline-none focus:border-amber-400 cursor-pointer"
            >
              {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>

            <button
              onClick={() => setShowFilters(v => !v)}
              className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border transition-colors font-medium ${
                showFilters || activeFiltersCount > 0
                  ? 'bg-amber-50 text-amber-700 border-amber-300'
                  : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
              }`}
            >
              <Filter className="w-4 h-4" />
              Filters
              {activeFiltersCount > 0 && (
                <span className="bg-amber-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {activeFiltersCount}
                </span>
              )}
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="border-t border-gray-100 pt-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {[
              { label: 'Risk Level', value: riskFilter, onChange: (v: string) => { setRiskFilter(v); setPage(1); },
                options: [['all','All Risks'],['low','Low (<40)'],['medium','Medium (40-69)'],['high','High (≥70)'],['critical','Critical (≥75)']] },
              { label: 'State', value: stateFilter, onChange: (v: string) => { setStateFilter(v); setPage(1); },
                options: STATES.map(s => [s, s === 'all' ? 'All States' : s]) },
              { label: 'Subsidiary', value: subsidiaryFilter, onChange: (v: string) => setSubsidiaryFilter(v),
                options: SUBSIDIARIES.map(s => [s, s === 'all' ? 'All Subsidiaries' : s]) },
              { label: 'Status', value: statusFilter, onChange: (v: string) => { setStatusFilter(v); setPage(1); },
                options: [['all','All Status'],['operational','Operational'],['suspended','Suspended'],['maintenance','Maintenance'],['archived','Archived']] },
              { label: 'Mine Type', value: mineTypeFilter, onChange: (v: string) => { setMineTypeFilter(v); setPage(1); },
                options: [['all','All Types'],['Opencast','Opencast'],['Underground','Underground']] },
            ].map(({ label, value, onChange, options }) => (
              <div key={label}>
                <label className="text-xs text-gray-500 font-medium block mb-1">{label}</label>
                <select
                  value={value}
                  onChange={e => onChange(e.target.value)}
                  className="w-full bg-white border border-gray-200 rounded-lg px-2 py-1.5 text-sm text-gray-700 outline-none focus:border-amber-400 cursor-pointer"
                >
                  {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </div>
            ))}

            {activeFiltersCount > 0 && (
              <div className="flex items-end">
                <button onClick={clearFilters} className="w-full flex items-center justify-center gap-1 text-sm text-red-600 border border-red-200 rounded-lg px-2 py-1.5 hover:bg-red-50 transition-colors">
                  <X className="w-3.5 h-3.5" /> Clear All
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Subsidiary quick filter pills */}
      <div className="flex flex-wrap gap-2">
        {SUBSIDIARIES.map(sub => {
          const colors = SUBSIDIARY_COLORS[sub] || { bg: '', text: '', border: '', dot: '' };
          const isActive = subsidiaryFilter === sub;
          return (
            <button
              key={sub}
              onClick={() => { setSubsidiaryFilter(sub === subsidiaryFilter ? 'all' : sub); setPage(1); }}
              className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition-all ${
                sub === 'all'
                  ? isActive ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-600 border-gray-300 hover:border-gray-500'
                  : isActive ? `${colors.bg} ${colors.text} ${colors.border} shadow-sm` : `bg-white text-gray-500 border-gray-200 hover:${colors.border}`
              }`}
            >
              {sub === 'all' ? 'All' : sub}
            </button>
          );
        })}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <div className="skeleton h-10 w-10 rounded-lg shrink-0" />
                <div className="flex-1 space-y-2">
                  <div className="skeleton h-4 w-2/5" />
                  <div className="skeleton h-3 w-3/5" />
                </div>
                <div className="skeleton h-6 w-16 rounded-full" />
                <div className="skeleton h-6 w-16 rounded-full" />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-16 text-center">
            <Mountain className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No mines found</p>
            <p className="text-gray-400 text-sm mt-1">Try adjusting your filters or search term</p>
            {activeFiltersCount > 0 && (
              <button onClick={clearFilters} className="mt-3 text-sm text-amber-600 hover:underline">
                Clear all filters
              </button>
            )}
          </div>
        ) : (
          <>
            {/* Table header */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/50 text-xs text-gray-500 uppercase tracking-wider">
                    <th className="text-left px-4 py-3 font-semibold">Mine</th>
                    <th className="text-left px-4 py-3 font-semibold hidden md:table-cell">Location</th>
                    <th className="text-left px-4 py-3 font-semibold hidden lg:table-cell">Subsidiary</th>
                    <th className="text-center px-4 py-3 font-semibold">Type</th>
                    <th className="text-left px-4 py-3 font-semibold hidden xl:table-cell" style={{ minWidth: 120 }}>Scores</th>
                    <th className="text-center px-4 py-3 font-semibold">Compliance</th>
                    <th className="text-center px-4 py-3 font-semibold">Risk</th>
                    <th className="text-center px-4 py-3 font-semibold hidden sm:table-cell">Workers</th>
                    <th className="text-center px-4 py-3 font-semibold hidden lg:table-cell">Status</th>
                    <th className="text-center px-4 py-3 font-semibold hidden md:table-cell">Data</th>
                    <th className="text-center px-4 py-3 font-semibold"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {filtered.map((mine, idx) => {
                    const riskColor = getRiskColor(mine.risk_score);
                    const subCode = getSubsidiaryCode((mine as any).subsidiary_name);
                    const subColors = SUBSIDIARY_COLORS[subCode] || { bg: 'bg-gray-50', text: 'text-gray-600', border: 'border-gray-200', dot: 'bg-gray-400' };
                    const isOfficialData = (mine as any).data_classification === 'official_public';

                    return (
                      <tr
                        key={mine.id}
                        className="hover:bg-amber-50/30 cursor-pointer transition-colors group"
                        onClick={() => navigate(`/app/mines/${mine.id}`)}
                      >
                        {/* Mine Name */}
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2.5">
                            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${subColors.bg} ${subColors.border} border`}>
                              <Mountain className={`w-4 h-4 ${subColors.text}`} />
                            </div>
                            <div>
                              <p className="font-semibold text-gray-800 text-sm group-hover:text-amber-700 transition-colors leading-tight">{mine.name}</p>
                              <p className="text-xs text-gray-400 font-mono">{mine.code}</p>
                            </div>
                          </div>
                        </td>

                        {/* Location */}
                        <td className="px-4 py-3 hidden md:table-cell">
                          <div className="flex items-center gap-1 text-gray-600 text-xs">
                            <MapPin className="w-3 h-3 text-gray-400 shrink-0" />
                            <span className="truncate max-w-[140px]">{mine.district}, {mine.state}</span>
                          </div>
                        </td>

                        {/* Subsidiary */}
                        <td className="px-4 py-3 hidden lg:table-cell">
                          <SubsidiaryBadge name={(mine as any).subsidiary_name} />
                        </td>

                        {/* Type */}
                        <td className="px-4 py-3 text-center">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            mine.mine_type === 'Opencast'
                              ? 'bg-sky-50 text-sky-700 border border-sky-200'
                              : 'bg-slate-100 text-slate-700 border border-slate-200'
                          }`}>
                            {mine.mine_type === 'Opencast' ? '⛏ OC' : '🕳 UG'}
                          </span>
                        </td>

                        {/* Score bars */}
                        <td className="px-4 py-3 hidden xl:table-cell" style={{ minWidth: 120 }}>
                          <div className="space-y-1">
                            <div className="flex items-center gap-1 text-xs text-gray-400">
                              <Shield className="w-2.5 h-2.5" />
                              <ScoreBar value={mine.safety_score || 0} color="#10b981" />
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-400">
                              <Globe className="w-2.5 h-2.5" />
                              <ScoreBar value={mine.environment_score || 0} color="#3b82f6" />
                            </div>
                          </div>
                        </td>

                        {/* Compliance */}
                        <td className="px-4 py-3 text-center">
                          <span className={`font-bold text-sm ${
                            mine.compliance_score < 65 ? 'text-red-600' :
                            mine.compliance_score < 80 ? 'text-amber-600' : 'text-emerald-600'
                          }`}>
                            {mine.compliance_score?.toFixed(0)}%
                          </span>
                        </td>

                        {/* Risk */}
                        <td className="px-4 py-3 text-center">
                          <span
                            className="inline-flex items-center text-xs font-bold px-2 py-1 rounded-full"
                            style={{ backgroundColor: riskColor + '18', color: riskColor }}
                          >
                            {mine.risk_score}
                          </span>
                        </td>

                        {/* Workers */}
                        <td className="px-4 py-3 text-center hidden sm:table-cell">
                          <div className="flex items-center justify-center gap-1 text-gray-600">
                            <Users className="w-3 h-3 text-gray-400" />
                            <span className="text-xs font-medium">{mine.num_workers?.toLocaleString()}</span>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="px-4 py-3 text-center hidden lg:table-cell">
                          <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${getStatusColor(mine.status)}`}>
                            {formatStatusLabel(mine.status)}
                          </span>
                        </td>

                        {/* Data classification badge */}
                        <td className="px-4 py-3 text-center hidden md:table-cell">
                          {isOfficialData ? (
                            <span className="inline-flex items-center gap-0.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full font-medium">
                              <CheckCircle className="w-2.5 h-2.5" /> Official
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-0.5 text-xs text-gray-500 bg-gray-50 border border-gray-200 px-1.5 py-0.5 rounded-full font-medium">
                              <Info className="w-2.5 h-2.5" /> Demo
                            </span>
                          )}
                        </td>

                        {/* Action */}
                        <td className="px-4 py-3 text-center">
                          <button className="text-xs text-amber-600 font-semibold hover:text-amber-800 flex items-center gap-0.5 mx-auto opacity-0 group-hover:opacity-100 transition-opacity">
                            View <ChevronRight className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50/50">
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">
                  Showing {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, total)} of <strong>{total}</strong> mines
                </span>
                <select
                  value={pageSize}
                  onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
                  className="text-xs bg-white border border-gray-200 rounded px-2 py-1 outline-none text-gray-600"
                >
                  {PAGE_SIZE_OPTIONS.map(n => <option key={n} value={n}>{n} per page</option>)}
                </select>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => setPage(1)}
                  disabled={page === 1}
                  className="p-1.5 rounded text-gray-400 hover:text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                </button>
                {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                  let pageNum: number;
                  if (totalPages <= 7) pageNum = i + 1;
                  else if (page <= 4) pageNum = i + 1;
                  else if (page >= totalPages - 3) pageNum = totalPages - 6 + i;
                  else pageNum = page - 3 + i;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`w-7 h-7 rounded text-xs font-medium transition-colors ${
                        page === pageNum
                          ? 'bg-amber-500 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => setPage(p => Math.min(p + 1, totalPages))}
                  disabled={page >= totalPages}
                  className="p-1.5 rounded text-gray-400 hover:text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 px-1">
        <span className="font-semibold text-gray-600">Subsidiaries:</span>
        {Object.entries(SUBSIDIARY_COLORS).map(([code, colors]) => (
          <span key={code} className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${colors.dot}`} />
            {code}
          </span>
        ))}
        <span className="ml-auto text-gray-400">
          Source: Coal India Limited / Ministry of Coal (Public Data) • Retrieved Sep 2026
        </span>
      </div>
    </div>
  );
}
