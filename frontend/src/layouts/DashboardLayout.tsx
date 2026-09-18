import { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard, Mountain, ShieldCheck, ClipboardCheck, AlertTriangle,
  CheckCircle2, Users, Factory, FileText, FolderSearch, BarChart3, Map,
  FileBarChart, Bot, Bell, Settings, LogOut, Menu, X, Search,
  ChevronDown, Activity, User
} from 'lucide-react';

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
  module: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Overview', path: '/app', icon: LayoutDashboard, module: 'dashboard' },
  { label: 'Mines', path: '/app/mines', icon: Mountain, module: 'mines' },
  { label: 'Compliance', path: '/app/compliance', icon: ShieldCheck, module: 'compliance' },
  { label: 'Inspections', path: '/app/inspections', icon: ClipboardCheck, module: 'inspections' },
  { label: 'Violations', path: '/app/violations', icon: AlertTriangle, module: 'violations' },
  { label: 'Corrective Actions', path: '/app/corrective-actions', icon: CheckCircle2, module: 'corrective_actions' },
  { label: 'Contractors', path: '/app/contractors', icon: Users, module: 'contractors' },
  { label: 'Production', path: '/app/production', icon: Factory, module: 'production' },
  { label: 'Field Reports', path: '/app/field-reports', icon: FileText, module: 'field_reports' },
  { label: 'Documents', path: '/app/documents', icon: FolderSearch, module: 'documents' },
  { label: 'Risk Analytics', path: '/app/risk', icon: BarChart3, module: 'risk' },
  { label: 'GIS Map', path: '/app/gis', icon: Map, module: 'gis' },
  { label: 'Reports', path: '/app/reports', icon: FileBarChart, module: 'reports' },
  { label: 'AI Assistant', path: '/app/ai-assistant', icon: Bot, module: 'ai_assistant' },
];

const BOTTOM_ITEMS: NavItem[] = [
  { label: 'Alerts', path: '/app/alerts', icon: Bell, module: 'alerts' },
  { label: 'Audit Trail', path: '/app/audit', icon: Activity, module: 'audit' },
  { label: 'Users', path: '/app/users', icon: Users, module: 'users' },
  { label: 'Import / Export', path: '/app/import-export', icon: FileBarChart, module: 'import' },
  { label: 'Settings', path: '/app/settings', icon: Settings, module: 'settings' },
];

const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrator',
  inspector: 'Inspector',
  mine_operator: 'Mine Operator',
  analyst: 'Analyst',
  viewer: 'Viewer',
};

export default function DashboardLayout() {
  const { user, logout, hasModule } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredNav = NAV_ITEMS.filter((item) => hasModule(item.module));
  const filteredBottom = BOTTOM_ITEMS.filter((item) => hasModule(item.module));

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getPageTitle = () => {
    const current = [...NAV_ITEMS, ...BOTTOM_ITEMS].find(
      (item) => location.pathname === item.path || location.pathname.startsWith(item.path + '/')
    );
    return current?.label || 'Dashboard';
  };

  const renderNavLink = (item: NavItem) => {
    const Icon = item.icon;
    const isExact = item.path === '/app';
    return (
      <NavLink
        key={item.path}
        to={item.path}
        end={isExact}
        onClick={() => setMobileOpen(false)}
        className={({ isActive }) =>
          `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group ${
            isActive
              ? 'bg-amber-brand/15 text-amber-brand'
              : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
          }`
        }
      >
        {({ isActive }) => (
          <>
            {isActive && (
              <span className="absolute left-0 w-[3px] h-6 bg-amber-brand rounded-r" />
            )}
            <Icon className="w-[18px] h-[18px] shrink-0" />
            {(sidebarOpen || mobileOpen) && <span className="truncate">{item.label}</span>}
          </>
        )}
      </NavLink>
    );
  };

  const sidebarContent = (
    <>
      {/* Brand */}
      <div className={`px-4 py-5 border-b border-white/10 ${sidebarOpen ? '' : 'px-2'}`}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-amber-brand rounded-lg flex items-center justify-center shrink-0">
            <Mountain className="w-5 h-5 text-charcoal" />
          </div>
          {(sidebarOpen || mobileOpen) && (
            <div>
              <h1 className="text-base font-bold text-white tracking-tight">KhanijSetu</h1>
              <p className="text-[11px] text-gray-500 leading-tight">Smart Mining Governance</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Nav */}
      <nav className="flex-1 px-2 py-3 overflow-y-auto space-y-0.5">
        {filteredNav.map(renderNavLink)}
      </nav>

      {/* Bottom */}
      <div className="px-2 py-2 border-t border-white/10 space-y-0.5">
        {filteredBottom.map(renderNavLink)}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all w-full"
        >
          <LogOut className="w-[18px] h-[18px] shrink-0" />
          {(sidebarOpen || mobileOpen) && <span>Logout</span>}
        </button>
      </div>
    </>
  );

  return (
    <div className="flex h-screen bg-surface overflow-hidden">
      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:flex flex-col bg-charcoal text-white transition-all duration-200 ${
          sidebarOpen ? 'w-[248px]' : 'w-[68px]'
        } relative shrink-0`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 bottom-0 w-[260px] bg-charcoal text-white flex flex-col">
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
            {sidebarContent}
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-6 shrink-0">
          <div className="flex items-center gap-3">
            {/* Mobile menu */}
            <button
              onClick={() => setMobileOpen(true)}
              className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            {/* Sidebar toggle */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:block p-1.5 rounded-lg hover:bg-gray-100"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            {/* Breadcrumb */}
            <div className="hidden sm:flex items-center gap-1.5 text-sm">
              <span className="text-gray-400">KhanijSetu</span>
              <span className="text-gray-300">/</span>
              <span className="font-medium text-gray-700">{getPageTitle()}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {/* Search */}
            <div className="hidden md:flex items-center bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 w-56 focus-within:border-amber-brand/50 focus-within:ring-1 focus-within:ring-amber-brand/20">
              <Search className="w-4 h-4 text-gray-400 mr-2" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-sm outline-none w-full placeholder:text-gray-400"
              />
            </div>

            {/* System Status */}
            <div className="hidden lg:flex items-center gap-1.5 text-xs text-gray-500 bg-gray-50 px-2.5 py-1.5 rounded-lg">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
              Systems Operational
            </div>

            {/* Notifications */}
            <button
              onClick={() => navigate('/app/alerts')}
              className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Bell className="w-5 h-5 text-gray-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* User */}
            <div className="flex items-center gap-2 pl-2 border-l border-gray-200">
              <div className="w-8 h-8 bg-slate-dark rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-gray-700 leading-tight">{user?.name?.split(' ').slice(0, 2).join(' ')}</p>
                <p className="text-[11px] text-gray-400 leading-tight">{ROLE_LABELS[user?.role || ''] || user?.role}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
