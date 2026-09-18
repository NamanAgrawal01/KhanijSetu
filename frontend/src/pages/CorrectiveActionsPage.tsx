import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { CorrectiveAction } from '@/types';
import { formatDate, getStatusColor, formatStatusLabel, getSeverityColor } from '@/lib/utils';
import { CheckCircle2, Clock, AlertTriangle, Upload, Plus, Search } from 'lucide-react';

const COLUMNS: { key: string; label: string; color: string }[] = [
  { key: 'pending', label: 'Pending', color: 'border-t-amber-400' },
  { key: 'in_progress', label: 'In Progress', color: 'border-t-blue-400' },
  { key: 'overdue', label: 'Overdue', color: 'border-t-red-400' },
  { key: 'submitted', label: 'Submitted', color: 'border-t-purple-400' },
  { key: 'verified', label: 'Verified', color: 'border-t-emerald-400' },
  { key: 'closed', label: 'Closed', color: 'border-t-gray-400' },
];

export default function CorrectiveActionsPage() {
  const [actions, setActions] = useState<CorrectiveAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAction, setSelectedAction] = useState<CorrectiveAction | null>(null);

  const fetchActions = () => {
    setLoading(true);
    api.get('/corrective-actions').then(res => {
      setActions(Array.isArray(res.data) ? res.data : res.data.actions || []);
    }).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchActions(); }, []);

  const updateStatus = async (id: number, newStatus: string) => {
    try {
      await api.put(`/corrective-actions/${id}`, { status: newStatus });
      fetchActions();
      setSelectedAction(null);
    } catch (err) { console.error(err); }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Corrective Actions</h1>
          <p className="text-sm text-gray-500 mt-0.5">Workflow management for violation resolution and compliance restoration</p>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-4 min-w-[1200px]">
          {COLUMNS.map(col => {
            const colActions = actions.filter(a => a.status === col.key);
            return (
              <div key={col.key} className={`flex-1 min-w-[200px] bg-gray-50 rounded-xl border-t-4 ${col.color} p-3`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-700">{col.label}</h3>
                  <span className="text-xs bg-white border border-gray-200 text-gray-500 px-2 py-0.5 rounded-full font-medium">{colActions.length}</span>
                </div>
                <div className="space-y-2">
                  {loading ? (
                    Array.from({length: 2}).map((_, i) => <div key={i} className="skeleton h-28 w-full rounded-lg" />)
                  ) : colActions.length === 0 ? (
                    <p className="text-xs text-gray-400 text-center py-4">No items</p>
                  ) : (
                    colActions.map(action => (
                      <div
                        key={action.id}
                        onClick={() => setSelectedAction(action)}
                        className="bg-white rounded-lg border border-gray-200 p-3 cursor-pointer hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[10px] font-mono text-gray-400">{action.action_code}</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium ${getSeverityColor(action.priority)}`}>
                            {action.priority}
                          </span>
                        </div>
                        <p className="text-xs font-medium text-gray-800 line-clamp-2 mb-2">{action.title}</p>
                        <div className="flex items-center justify-between text-[10px] text-gray-400">
                          <span>{action.mine_name || `Mine #${action.mine_id}`}</span>
                          <span className="flex items-center gap-0.5">
                            <Clock className="w-3 h-3" /> {formatDate(action.deadline)}
                          </span>
                        </div>
                        {action.assigned_to_name && (
                          <p className="text-[10px] text-gray-400 mt-1">→ {action.assigned_to_name}</p>
                        )}
                        {col.key === 'overdue' && (
                          <div className="mt-2 bg-red-50 border border-red-100 rounded px-2 py-1">
                            <p className="text-[10px] text-red-600 font-medium">⚠ Overdue</p>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedAction(null)} />
          <div className="relative bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-6 animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-xs font-mono text-gray-400">{selectedAction.action_code}</span>
                <h3 className="text-lg font-bold text-gray-900 mt-1">{selectedAction.title}</h3>
              </div>
              <button onClick={() => setSelectedAction(null)} className="text-gray-400 hover:text-gray-600 text-lg">✕</button>
            </div>
            <p className="text-sm text-gray-600 mb-4">{selectedAction.description}</p>
            <div className="grid grid-cols-2 gap-3 text-sm border-t pt-3">
              {[
                ['Status', formatStatusLabel(selectedAction.status)],
                ['Priority', selectedAction.priority],
                ['Assigned To', selectedAction.assigned_to_name || '—'],
                ['Deadline', formatDate(selectedAction.deadline)],
                ['Mine', selectedAction.mine_name || `Mine #${selectedAction.mine_id}`],
                ['Verified By', selectedAction.verified_by_name || '—'],
              ].map(([l, v]) => (
                <div key={l}><p className="text-xs text-gray-400">{l}</p><p className="font-medium text-gray-700 capitalize">{v}</p></div>
              ))}
            </div>
            {selectedAction.evidence_notes && (
              <div className="mt-3 bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                <p className="text-xs font-semibold text-emerald-800">Evidence Submitted</p>
                <p className="text-xs text-emerald-600 mt-1">{selectedAction.evidence_notes}</p>
              </div>
            )}
            <div className="flex gap-2 mt-4">
              {selectedAction.status === 'pending' && (
                <button onClick={() => updateStatus(selectedAction.id, 'in_progress')} className="flex-1 text-sm bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium">Start Work</button>
              )}
              {selectedAction.status === 'in_progress' && (
                <button onClick={() => updateStatus(selectedAction.id, 'submitted')} className="flex-1 text-sm bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 font-medium flex items-center justify-center gap-1">
                  <Upload className="w-3.5 h-3.5" /> Submit Evidence
                </button>
              )}
              {selectedAction.status === 'submitted' && (
                <button onClick={() => updateStatus(selectedAction.id, 'verified')} className="flex-1 text-sm bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-medium flex items-center justify-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Verify
                </button>
              )}
              {selectedAction.status === 'verified' && (
                <button onClick={() => updateStatus(selectedAction.id, 'closed')} className="flex-1 text-sm bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 font-medium">Close</button>
              )}
              {selectedAction.status === 'overdue' && (
                <button onClick={() => updateStatus(selectedAction.id, 'in_progress')} className="flex-1 text-sm bg-amber-brand text-white py-2 rounded-lg hover:bg-amber-hover font-medium">Resume Work</button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
