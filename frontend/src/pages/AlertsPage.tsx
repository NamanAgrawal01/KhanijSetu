import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { Alert } from '@/types';
import { getSeverityColor, formatStatusLabel, timeAgo } from '@/lib/utils';
import { Bell, AlertOctagon, AlertTriangle, Info, Shield, ChevronRight } from 'lucide-react';

const ESCALATION_LABELS = ['Initial', 'Reminder', '1st Escalation', '2nd Escalation', 'Management'];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('all');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  useEffect(() => {
    api.get('/alerts').then(res => {
      setAlerts(Array.isArray(res.data) ? res.data : res.data.alerts || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const counts = {
    critical: alerts.filter(a => a.severity === 'critical').length,
    high: alerts.filter(a => a.severity === 'high').length,
    warning: alerts.filter(a => a.severity === 'warning').length,
    info: alerts.filter(a => a.severity === 'info').length,
  };

  const filtered = severityFilter === 'all' ? alerts : alerts.filter(a => a.severity === severityFilter);

  const getIcon = (severity: string) => {
    switch(severity) { case 'critical': return AlertOctagon; case 'high': return AlertTriangle; case 'warning': return Shield; default: return Info; }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-900">Alert Center</h1><p className="text-sm text-gray-500 mt-0.5">System alerts, escalations and notifications</p></div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Critical', count: counts.critical, color: 'text-red-600', bg: 'bg-red-50', key: 'critical' },
          { label: 'High', count: counts.high, color: 'text-orange-600', bg: 'bg-orange-50', key: 'high' },
          { label: 'Warning', count: counts.warning, color: 'text-amber-600', bg: 'bg-amber-50', key: 'warning' },
          { label: 'Information', count: counts.info, color: 'text-blue-600', bg: 'bg-blue-50', key: 'info' },
        ].map(s => (
          <div key={s.key} onClick={() => setSeverityFilter(severityFilter === s.key ? 'all' : s.key)} className={`bg-white rounded-xl border border-gray-100 p-4 cursor-pointer kpi-card ${severityFilter === s.key ? 'ring-2 ring-amber-brand' : ''}`}>
            <p className={`text-2xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        {loading ? Array.from({length:4}).map((_,i) => <div key={i} className="skeleton h-20 rounded-xl" />) :
        filtered.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center"><Bell className="w-10 h-10 text-gray-300 mx-auto mb-3" /><p className="text-sm text-gray-500">No alerts</p></div>
        ) : filtered.map(alert => {
          const Icon = getIcon(alert.severity);
          return (
            <div key={alert.id} onClick={() => setSelectedAlert(alert)} className={`bg-white rounded-xl border p-4 cursor-pointer hover:shadow-sm transition-shadow ${alert.status === 'resolved' ? 'opacity-60 border-gray-100' : 'border-gray-200'}`}>
              <div className="flex items-start gap-3">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                  alert.severity === 'critical' ? 'bg-red-100' : alert.severity === 'high' ? 'bg-orange-100' : alert.severity === 'warning' ? 'bg-amber-100' : 'bg-blue-100'
                }`}>
                  <Icon className={`w-4 h-4 ${alert.severity === 'critical' ? 'text-red-600' : alert.severity === 'high' ? 'text-orange-600' : alert.severity === 'warning' ? 'text-amber-600' : 'text-blue-600'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold uppercase ${getSeverityColor(alert.severity)}`}>{alert.severity}</span>
                    {alert.escalation_level > 0 && <span className="text-[10px] bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full font-medium">Escalation L{alert.escalation_level}</span>}
                  </div>
                  <p className="text-sm font-medium text-gray-800">{alert.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{alert.message}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                    {alert.mine_name && <span>{alert.mine_name}</span>}
                    <span>{alert.source}</span>
                    <span>{timeAgo(alert.created_at)}</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedAlert(null)} />
          <div className="relative bg-white rounded-2xl shadow-xl max-w-md w-full p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-gray-900 mb-3">{selectedAlert.title}</h3>
            <p className="text-sm text-gray-600 mb-4">{selectedAlert.message}</p>
            {selectedAlert.escalation_level > 0 && (
              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-500 mb-2">Escalation Timeline</p>
                <div className="space-y-2">
                  {Array.from({length: Math.min(selectedAlert.escalation_level + 1, 5)}).map((_, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${i <= selectedAlert!.escalation_level ? 'bg-amber-brand' : 'bg-gray-200'}`} />
                      <span className={`text-xs ${i <= selectedAlert!.escalation_level ? 'text-gray-700 font-medium' : 'text-gray-400'}`}>{ESCALATION_LABELS[i]}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <button onClick={() => setSelectedAlert(null)} className="w-full text-sm bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 font-medium">Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
