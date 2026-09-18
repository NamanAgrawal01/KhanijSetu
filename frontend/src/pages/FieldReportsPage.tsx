import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { FieldReport } from '@/types';
import { formatDate, getSeverityColor, getStatusColor, formatStatusLabel, timeAgo } from '@/lib/utils';
import { FileText, Plus, MapPin, Camera, Loader2, CheckCircle2, Wifi, WifiOff } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

export default function FieldReportsPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<FieldReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [gpsStatus, setGpsStatus] = useState<'idle'|'loading'|'success'|'error'>('idle');
  const [form, setForm] = useState({
    mine_id: 1, observation_type: 'safety', severity: 'medium',
    title: '', description: '', latitude: 0, longitude: 0, location_label: '',
  });

  useEffect(() => {
    api.get('/field-reports').then(res => {
      setReports(Array.isArray(res.data) ? res.data : res.data.reports || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const captureGPS = () => {
    setGpsStatus('loading');
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setForm({...form, latitude: pos.coords.latitude, longitude: pos.coords.longitude, location_label: `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`});
          setGpsStatus('success');
        },
        () => {
          setForm({...form, latitude: 23.7957, longitude: 86.4304, location_label: 'Demo Location (23.7957, 86.4304)'});
          setGpsStatus('success');
        },
        { timeout: 5000 }
      );
    } else {
      setForm({...form, latitude: 23.7957, longitude: 86.4304, location_label: 'Demo Location (23.7957, 86.4304)'});
      setGpsStatus('success');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.description) return;
    setSubmitting(true);
    try {
      await api.post('/field-reports', form);
      setShowForm(false);
      setForm({mine_id: 1, observation_type: 'safety', severity: 'medium', title: '', description: '', latitude: 0, longitude: 0, location_label: ''});
      setGpsStatus('idle');
      const res = await api.get('/field-reports');
      setReports(Array.isArray(res.data) ? res.data : res.data.reports || []);
    } catch (err) { console.error(err); }
    setSubmitting(false);
  };

  // Offline queue (localStorage)
  const pendingReports = JSON.parse(localStorage.getItem('khanijsetu_pending_reports') || '[]');

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Field Intelligence</h1>
          <p className="text-sm text-gray-500 mt-0.5">Submit and track field observations and safety reports</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-1.5 text-sm text-white bg-amber-brand hover:bg-amber-hover px-4 py-2.5 rounded-lg font-medium">
          <Plus className="w-4 h-4" /> New Report
        </button>
      </div>

      {/* Sync Status */}
      <div className="flex items-center gap-4 bg-white rounded-xl border border-gray-100 p-3">
        <div className="flex items-center gap-2 text-sm">
          <Wifi className="w-4 h-4 text-emerald-500" />
          <span className="text-emerald-600 font-medium">Online</span>
        </div>
        <div className="text-xs text-gray-400">
          Synced: {reports.length} reports · Pending: {pendingReports.length}
        </div>
      </div>

      {/* Report Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">{Array.from({length:4}).map((_,i)=><div key={i} className="skeleton h-16 w-full" />)}</div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No field reports yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {reports.map(report => (
              <div key={report.id} className="p-4 hover:bg-gray-50/50 transition-colors">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-gray-400">{report.report_code}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${getSeverityColor(report.severity)}`}>{report.severity}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${getStatusColor(report.status)}`}>{formatStatusLabel(report.status)}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-800">{report.title || report.description.slice(0, 80)}</p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{report.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span>{report.reporter_name}</span>
                      <span>{report.mine_name || `Mine #${report.mine_id}`}</span>
                      {report.location_label && <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{report.location_label}</span>}
                      <span>{timeAgo(report.created_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Report Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowForm(false)} />
          <div className="relative bg-white rounded-t-2xl sm:rounded-2xl shadow-xl w-full sm:max-w-md max-h-[90vh] overflow-y-auto p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-gray-900 mb-4">New Field Report</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mine</label>
                <select value={form.mine_id} onChange={e => setForm({...form, mine_id: +e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
                  <option value={1}>Rajmahal Coal Mine</option>
                  <option value={2}>Godda East Mine</option>
                  <option value={3}>Kathara Deep Mine</option>
                  <option value={4}>Bokaro Central Mine</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select value={form.observation_type} onChange={e => setForm({...form, observation_type: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
                    {['safety','environment','equipment','general'].map(t=><option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                  <select value={form.severity} onChange={e => setForm({...form, severity: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
                    {['low','medium','high','critical'].map(s=><option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input type="text" value={form.title} onChange={e => setForm({...form, title: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Brief observation title" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={3} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none resize-none" placeholder="Describe the observation..." required />
              </div>

              {/* GPS */}
              <div>
                <button type="button" onClick={captureGPS} className="flex items-center gap-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg transition-colors w-full justify-center">
                  {gpsStatus === 'loading' ? <Loader2 className="w-4 h-4 animate-spin" /> : <MapPin className="w-4 h-4" />}
                  {gpsStatus === 'success' ? 'Location Captured' : 'Capture Location'}
                </button>
                {gpsStatus === 'success' && (
                  <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> {form.location_label}</p>
                )}
              </div>

              {/* Photo placeholder */}
              <button type="button" className="flex items-center gap-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg transition-colors w-full justify-center">
                <Camera className="w-4 h-4" /> Capture Photo
              </button>

              <div className="flex gap-2 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 text-sm bg-gray-100 text-gray-700 py-2.5 rounded-lg hover:bg-gray-200 font-medium">Cancel</button>
                <button type="submit" disabled={submitting} className="flex-1 text-sm bg-amber-brand text-white py-2.5 rounded-lg hover:bg-amber-hover font-medium flex items-center justify-center gap-1 disabled:opacity-60">
                  {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />} Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
