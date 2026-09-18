import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { Settings, Server, Database, Shield, Check, Loader2, Plus, X } from 'lucide-react';

interface SystemInfo {
  status: string;
  version: string;
  database: string;
  environment: string;
}

interface Subsidiary {
  id: number;
  name: string;
  code: string;
  region: string;
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [sysInfo, setSysInfo] = useState<SystemInfo | null>(null);
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddSub, setShowAddSub] = useState(false);
  const [subForm, setSubForm] = useState({ name: '', code: '', region: '' });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/health').then(r => setSysInfo(r.data)).catch(() => setSysInfo({ status: 'unknown', version: '1.0.0', database: 'SQLite', environment: 'development' })),
      api.get('/users/subsidiaries').then(r => setSubsidiaries(r.data || [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const handleAddSub = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/users/subsidiaries', subForm);
      setSuccess('Subsidiary created');
      setShowAddSub(false);
      setSubForm({ name: '', code: '', region: '' });
      const r = await api.get('/users/subsidiaries');
      setSubsidiaries(r.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create subsidiary');
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    if (success) { const t = setTimeout(() => setSuccess(''), 3000); return () => clearTimeout(t); }
  }, [success]);

  const isAdmin = user?.role === 'admin';

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Settings className="w-7 h-7 text-amber-brand" />
          Settings
        </h1>
        <p className="text-sm text-gray-500 mt-1">System configuration and management</p>
      </div>

      {success && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700 flex items-center gap-2">
          <Check className="w-4 h-4" /> {success}
        </div>
      )}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      )}

      {/* System Info */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
          <Server className="w-5 h-5 text-gray-400" /> System Information
        </h2>
        {loading ? (
          <Loader2 className="w-5 h-5 animate-spin text-amber-brand" />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500">Status</p>
              <p className="font-medium text-gray-900 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500" /> {sysInfo?.status || 'Unknown'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Version</p>
              <p className="font-medium text-gray-900">{sysInfo?.version || '1.0.0'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Database</p>
              <p className="font-medium text-gray-900 flex items-center gap-1">
                <Database className="w-3.5 h-3.5 text-gray-400" /> {sysInfo?.database || 'SQLite'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Environment</p>
              <p className="font-medium text-gray-900">{sysInfo?.environment || 'development'}</p>
            </div>
          </div>
        )}
      </div>

      {/* Roles */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
          <Shield className="w-5 h-5 text-gray-400" /> Roles & Permissions
        </h2>
        <div className="space-y-3">
          {[
            { role: 'Admin', desc: 'Full system access — manage users, mines, imports, settings', color: 'bg-red-100 text-red-800' },
            { role: 'Inspector', desc: 'Create/manage inspections, record violations and compliance', color: 'bg-blue-100 text-blue-800' },
            { role: 'Mine Operator', desc: 'Manage assigned mine operations, compliance, documents', color: 'bg-amber-100 text-amber-800' },
            { role: 'Analyst', desc: 'View analytics, reports, search — read-only across modules', color: 'bg-purple-100 text-purple-800' },
            { role: 'Viewer', desc: 'Read-only access to authorized data', color: 'bg-gray-100 text-gray-800' },
          ].map(r => (
            <div key={r.role} className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${r.color} whitespace-nowrap`}>{r.role}</span>
              <p className="text-sm text-gray-600">{r.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Subsidiaries */}
      {isAdmin && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Subsidiaries</h2>
            <button onClick={() => setShowAddSub(true)}
              className="flex items-center gap-1 px-3 py-1.5 bg-amber-brand text-charcoal text-sm font-medium rounded-lg hover:bg-amber-hover transition-colors">
              <Plus className="w-4 h-4" /> Add
            </button>
          </div>

          {showAddSub && (
            <form onSubmit={handleAddSub} className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <input required placeholder="Name" value={subForm.name} onChange={e => setSubForm({...subForm, name: e.target.value})}
                  className="px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                <input required placeholder="Code" value={subForm.code} onChange={e => setSubForm({...subForm, code: e.target.value})}
                  className="px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                <input placeholder="Region" value={subForm.region} onChange={e => setSubForm({...subForm, region: e.target.value})}
                  className="px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={saving}
                  className="px-4 py-2 bg-amber-brand text-charcoal text-sm font-semibold rounded-lg hover:bg-amber-hover disabled:opacity-50 flex items-center gap-1">
                  {saving && <Loader2 className="w-3.5 h-3.5 animate-spin" />} Save
                </button>
                <button type="button" onClick={() => setShowAddSub(false)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">
                  <X className="w-4 h-4 inline" /> Cancel
                </button>
              </div>
            </form>
          )}

          <div className="space-y-2">
            {subsidiaries.map(s => (
              <div key={s.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                <div>
                  <span className="font-medium text-gray-900 text-sm">{s.name}</span>
                  <span className="ml-2 text-xs text-gray-500">({s.code})</span>
                </div>
                <span className="text-xs text-gray-400">{s.region || '—'}</span>
              </div>
            ))}
            {subsidiaries.length === 0 && <p className="text-sm text-gray-400 py-2">No subsidiaries configured</p>}
          </div>
        </div>
      )}
    </div>
  );
}
