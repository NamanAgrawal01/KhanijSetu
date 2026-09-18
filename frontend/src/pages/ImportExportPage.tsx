import { useState, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import {
  Upload, Download, FileSpreadsheet, AlertTriangle, Check,
  Loader2, X, FileUp, ChevronDown
} from 'lucide-react';

interface PreviewItem {
  row: number;
  name: string;
  code: string;
  data: Record<string, string>;
  errors: string[];
}

const EXPORT_MODULES = [
  { key: 'mines', label: 'Mines', icon: '⛏️' },
  { key: 'inspections', label: 'Inspections', icon: '📋' },
  { key: 'violations', label: 'Violations', icon: '⚠️' },
  { key: 'compliance', label: 'Compliance Records', icon: '✅' },
  { key: 'corrective-actions', label: 'Corrective Actions', icon: '🔧' },
  { key: 'production', label: 'Production', icon: '📊' },
  { key: 'contractors', label: 'Contractors', icon: '👷' },
  { key: 'workers', label: 'Workers', icon: '👥' },
  { key: 'alerts', label: 'Alerts', icon: '🔔' },
  { key: 'audit', label: 'Audit Logs', icon: '📝' },
];

export default function ImportExportPage() {
  const { user } = useAuth();
  const fileRef = useRef<HTMLInputElement>(null);
  const [tab, setTab] = useState<'import' | 'export'>('import');

  // Import state
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [importing, setImporting] = useState(false);
  const [preview, setPreview] = useState<{ valid: PreviewItem[]; invalid: PreviewItem[]; warnings: string[] } | null>(null);
  const [importResult, setImportResult] = useState<{ created: number } | null>(null);
  const [error, setError] = useState('');

  // Export state
  const [exportFormat, setExportFormat] = useState('csv');
  const [exporting, setExporting] = useState<string | null>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) { setFile(f); setPreview(null); setImportResult(null); setError(''); }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { setFile(f); setPreview(null); setImportResult(null); setError(''); }
  };

  const handlePreview = async () => {
    if (!file) return;
    setPreviewing(true);
    setError('');
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await api.post('/import/mines/preview', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPreview(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Preview failed');
    } finally {
      setPreviewing(false);
    }
  };

  const handleImport = async () => {
    if (!preview) return;
    setImporting(true);
    setError('');
    try {
      const res = await api.post('/import/mines/confirm', { rows: preview.valid });
      setImportResult(res.data);
      setPreview(null);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Import failed');
    } finally {
      setImporting(false);
    }
  };

  const handleExport = async (module: string) => {
    setExporting(module);
    try {
      const res = await api.get(`/export/${module}`, {
        params: { format: exportFormat },
        responseType: 'blob',
      });
      const ext = exportFormat === 'xlsx' ? 'xlsx' : 'csv';
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `khanijsetu_${module}_${new Date().toISOString().slice(0, 10)}.${ext}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(`Export failed for ${module}`);
    } finally {
      setExporting(null);
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <FileSpreadsheet className="w-7 h-7 text-amber-brand" />
          Import & Export
        </h1>
        <p className="text-sm text-gray-500 mt-1">Import data from CSV/Excel or export filtered datasets</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        <button onClick={() => setTab('import')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${tab === 'import' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
          <Upload className="w-4 h-4 inline mr-1.5" /> Import
        </button>
        <button onClick={() => setTab('export')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${tab === 'export' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
          <Download className="w-4 h-4 inline mr-1.5" /> Export
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" /> {error}
          <button onClick={() => setError('')} className="ml-auto"><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* IMPORT TAB */}
      {tab === 'import' && (
        <div className="space-y-4">
          {importResult ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
              <Check className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-gray-900">Import Complete</h3>
              <p className="text-gray-500 mt-1">{importResult.created} records imported successfully</p>
              <button onClick={() => { setImportResult(null); setFile(null); }}
                className="mt-4 px-4 py-2 bg-amber-brand text-charcoal font-semibold rounded-lg hover:bg-amber-hover transition-colors">
                Import More
              </button>
            </div>
          ) : (
            <>
              {/* Drop Zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileRef.current?.click()}
                className={`bg-white rounded-xl border-2 border-dashed p-12 text-center cursor-pointer transition-colors
                  ${dragging ? 'border-amber-brand bg-amber-50' : 'border-gray-200 hover:border-gray-300'}`}
              >
                <input ref={fileRef} type="file" className="hidden" accept=".csv,.xlsx,.xls" onChange={handleFileSelect} />
                <FileUp className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                {file ? (
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600 font-medium">Drop a CSV or Excel file here</p>
                    <p className="text-xs text-gray-400 mt-1">Or click to browse. Max 10 MB</p>
                  </div>
                )}
              </div>

              {/* Preview Button */}
              {file && !preview && (
                <button onClick={handlePreview} disabled={previewing}
                  className="px-6 py-2.5 bg-amber-brand text-charcoal font-semibold rounded-lg hover:bg-amber-hover transition-colors disabled:opacity-50 flex items-center gap-2">
                  {previewing ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileSpreadsheet className="w-4 h-4" />}
                  Validate & Preview
                </button>
              )}

              {/* Preview Results */}
              {preview && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-emerald-700">{preview.valid.length}</p>
                      <p className="text-xs text-emerald-600">Valid Records</p>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-red-700">{preview.invalid.length}</p>
                      <p className="text-xs text-red-600">Invalid Records</p>
                    </div>
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-amber-700">{preview.warnings.length}</p>
                      <p className="text-xs text-amber-600">Warnings</p>
                    </div>
                  </div>

                  {preview.invalid.length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-200 p-4">
                      <h4 className="font-semibold text-red-700 mb-2">Invalid Records</h4>
                      <div className="space-y-1 max-h-48 overflow-y-auto">
                        {preview.invalid.map((item, i) => (
                          <div key={i} className="text-xs text-red-600 py-1 border-b border-red-50">
                            Row {item.row}: {item.errors.join(', ')}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {preview.warnings.length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-200 p-4">
                      <h4 className="font-semibold text-amber-700 mb-2">Warnings</h4>
                      <div className="space-y-1 max-h-32 overflow-y-auto">
                        {preview.warnings.map((w, i) => (
                          <p key={i} className="text-xs text-amber-600">{w}</p>
                        ))}
                      </div>
                    </div>
                  )}

                  {preview.valid.length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900">Preview ({preview.valid.length} records)</h4>
                      </div>
                      <div className="overflow-x-auto max-h-64">
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="bg-gray-50">
                              <th className="px-3 py-2 text-left font-medium text-gray-600">Row</th>
                              <th className="px-3 py-2 text-left font-medium text-gray-600">Name</th>
                              <th className="px-3 py-2 text-left font-medium text-gray-600">Code</th>
                            </tr>
                          </thead>
                          <tbody>
                            {preview.valid.slice(0, 20).map((item, i) => (
                              <tr key={i} className="border-b border-gray-50">
                                <td className="px-3 py-2 text-gray-500">{item.row}</td>
                                <td className="px-3 py-2 font-medium text-gray-900">{item.name}</td>
                                <td className="px-3 py-2 text-gray-600">{item.code}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3">
                    {isAdmin && preview.valid.length > 0 && (
                      <button onClick={handleImport} disabled={importing}
                        className="px-6 py-2.5 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 flex items-center gap-2">
                        {importing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                        Confirm Import ({preview.valid.length} records)
                      </button>
                    )}
                    <button onClick={() => { setPreview(null); setFile(null); }}
                      className="px-4 py-2.5 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors">
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* EXPORT TAB */}
      {tab === 'export' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">Format:</span>
            <div className="relative">
              <select value={exportFormat} onChange={e => setExportFormat(e.target.value)}
                className="appearance-none pl-3 pr-8 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:border-amber-brand">
                <option value="csv">CSV</option>
                <option value="xlsx">Excel (XLSX)</option>
              </select>
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {EXPORT_MODULES.map(mod => (
              <div key={mod.key} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:shadow-sm transition-shadow">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{mod.icon}</span>
                  <span className="font-medium text-gray-900 text-sm">{mod.label}</span>
                </div>
                <button onClick={() => handleExport(mod.key)}
                  disabled={exporting === mod.key}
                  className="px-3 py-1.5 bg-gray-100 hover:bg-amber-brand/10 hover:text-amber-brand text-gray-600 text-xs font-medium rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1.5">
                  {exporting === mod.key ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                  Export
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
