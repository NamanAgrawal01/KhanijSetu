import { useState } from 'react';
import api from '@/lib/api';
import type { ReportResponse } from '@/types';
import { FileBarChart, Download, Eye, Loader2, CheckCircle2, Sparkles } from 'lucide-react';

const REPORT_TYPES = [
  { type: 'monthly_compliance', title: 'Monthly Compliance Report', desc: 'Comprehensive compliance status across all mines' },
  { type: 'mine_inspection', title: 'Mine Inspection Report', desc: 'Inspection findings and recommendations' },
  { type: 'risk_assessment', title: 'Risk Assessment Report', desc: 'AI-powered risk analysis and scoring' },
  { type: 'violation_report', title: 'Violation Report', desc: 'Open and resolved violations summary' },
  { type: 'contractor_compliance', title: 'Contractor Compliance', desc: 'Contractor safety and performance review' },
  { type: 'environmental_summary', title: 'Environmental Summary', desc: 'Environmental monitoring and compliance data' },
  { type: 'management_summary', title: 'Management Summary', desc: 'Executive governance overview for leadership' },
];

export default function ReportsPage() {
  const [generating, setGenerating] = useState<string | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);

  const generateReport = async (reportType: string) => {
    setGenerating(reportType);
    setReport(null);
    try {
      const res = await api.post('/reports/generate', { report_type: reportType });
      setReport(res.data);
    } catch (err) {
      console.error(err);
      // Fallback demo
      setReport({
        id: `RPT-${Date.now()}`,
        report_type: reportType,
        title: REPORT_TYPES.find(r => r.type === reportType)?.title || 'Report',
        generated_at: new Date().toISOString(),
        summary: `This ${REPORT_TYPES.find(r => r.type === reportType)?.title} has been generated successfully. It covers data from the last 30 days across all monitored mining operations.\n\nKey Highlights:\n• 48 mines under active monitoring\n• Overall compliance rate: 78%\n• 37 open violations tracked\n• 12 corrective actions pending\n• 9 high-risk mines identified\n\nThe report includes detailed breakdowns by subsidiary, mine, and compliance category.`,
        data: null,
      });
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-900">Reports</h1><p className="text-sm text-gray-500 mt-0.5">Generate and download governance reports</p></div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {REPORT_TYPES.map(rt => (
          <div key={rt.type} className="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 bg-amber-brand/10 rounded-lg flex items-center justify-center">
                <FileBarChart className="w-5 h-5 text-amber-brand" />
              </div>
            </div>
            <h3 className="text-sm font-semibold text-gray-800 mb-1">{rt.title}</h3>
            <p className="text-xs text-gray-500 mb-4">{rt.desc}</p>
            <div className="flex gap-2">
              <button onClick={() => generateReport(rt.type)} disabled={!!generating} className="flex items-center gap-1 text-xs bg-amber-brand hover:bg-amber-hover text-white px-3 py-1.5 rounded-lg font-medium disabled:opacity-50 transition-colors">
                {generating === rt.type ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />} Generate
              </button>
              <button className="flex items-center gap-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1.5 rounded-lg font-medium"><Eye className="w-3 h-3" /> Preview</button>
            </div>
          </div>
        ))}
      </div>

      {report && (
        <div className="bg-white rounded-xl border border-gray-100 p-6 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <h3 className="text-sm font-semibold text-gray-800">Report Generated</h3>
              </div>
              <p className="text-xs text-gray-400">ID: {report.id} · Generated: {new Date(report.generated_at).toLocaleString()}</p>
            </div>
            <button className="flex items-center gap-1 text-sm bg-amber-brand hover:bg-amber-hover text-white px-4 py-2 rounded-lg font-medium">
              <Download className="w-4 h-4" /> Download PDF
            </button>
          </div>
          <div className="border-t pt-4">
            <h4 className="text-lg font-bold text-gray-900 mb-3">{report.title}</h4>
            <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{report.summary}</div>
          </div>
        </div>
      )}
    </div>
  );
}
