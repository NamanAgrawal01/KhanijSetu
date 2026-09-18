import { useState, useEffect } from 'react';
import api from '@/lib/api';
import type { Mine } from '@/types';
import { getRiskColor, getRiskLevel, formatDate } from '@/lib/utils';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Map as MapIcon, Filter } from 'lucide-react';

// Fix Leaflet default icon
delete (L.Icon.Default.prototype as any)._getIconUrl;

function createMarkerIcon(color: string) {
  return L.divIcon({
    html: `<div style="width:24px;height:24px;background:${color};border:3px solid white;border-radius:50%;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>`,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14],
  });
}

export default function GISMapPage() {
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState('all');

  useEffect(() => {
    api.get('/mines').then(res => {
      setMines(Array.isArray(res.data) ? res.data : res.data.mines || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = mines.filter(m => {
    if (riskFilter === 'all') return true;
    if (riskFilter === 'critical') return m.risk_score >= 75;
    if (riskFilter === 'high') return m.risk_score >= 50 && m.risk_score < 75;
    if (riskFilter === 'medium') return m.risk_score >= 25 && m.risk_score < 50;
    if (riskFilter === 'low') return m.risk_score < 25;
    return true;
  });

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <MapIcon className="w-6 h-6 text-amber-brand" /> GIS Map
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">Geographic intelligence for mining operations</p>
        </div>
        <select value={riskFilter} onChange={e => setRiskFilter(e.target.value)} className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none">
          <option value="all">All Risk Levels</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden relative" style={{ height: 'calc(100vh - 14rem)' }}>
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="skeleton h-full w-full" />
          </div>
        ) : (
          <MapContainer center={[23.75, 86.5]} zoom={8} className="h-full w-full" scrollWheelZoom={true}>
            <TileLayer
              attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {filtered.map(mine => (
              <Marker key={mine.id} position={[mine.latitude, mine.longitude]} icon={createMarkerIcon(getRiskColor(mine.risk_score))}>
                <Popup>
                  <div className="min-w-[200px]">
                    <h3 className="font-bold text-gray-900 text-sm mb-1">{mine.name}</h3>
                    <p className="text-xs text-gray-500 mb-2">{mine.location}</p>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between"><span className="text-gray-500">Compliance</span><span className="font-semibold">{mine.compliance_score}%</span></div>
                      <div className="flex justify-between"><span className="text-gray-500">Risk Score</span><span className="font-semibold" style={{color: getRiskColor(mine.risk_score)}}>{mine.risk_score} ({getRiskLevel(mine.risk_score)})</span></div>
                      <div className="flex justify-between"><span className="text-gray-500">Open Violations</span><span className="font-semibold">{mine.open_violations}</span></div>
                      <div className="flex justify-between"><span className="text-gray-500">Last Inspection</span><span>{formatDate(mine.last_inspection_date)}</span></div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur rounded-lg border border-gray-200 p-3 z-[1000]">
          <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Risk Level</p>
          <div className="space-y-1.5">
            {[
              { label: 'Low (0-24)', color: '#22c55e' },
              { label: 'Medium (25-49)', color: '#eab308' },
              { label: 'High (50-74)', color: '#f97316' },
              { label: 'Critical (75+)', color: '#ef4444' },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-xs text-gray-600">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
