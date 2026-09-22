import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/layouts/DashboardLayout';
import LoginPage from '@/pages/LoginPage';
import SignupPage from '@/pages/SignupPage';
import DashboardPage from '@/pages/DashboardPage';
import MinesPage from '@/pages/MinesPage';
import MineProfilePage from '@/pages/MineProfilePage';
import CompliancePage from '@/pages/CompliancePage';
import InspectionsPage from '@/pages/InspectionsPage';
import ViolationsPage from '@/pages/ViolationsPage';
import CorrectiveActionsPage from '@/pages/CorrectiveActionsPage';
import ContractorsPage from '@/pages/ContractorsPage';
import ProductionPage from '@/pages/ProductionPage';
import FieldReportsPage from '@/pages/FieldReportsPage';
import DocumentsPage from '@/pages/DocumentsPage';
import RiskAnalyticsPage from '@/pages/RiskAnalyticsPage';
import GISMapPage from '@/pages/GISMapPage';
import ReportsPage from '@/pages/ReportsPage';
import AIAssistantPage from '@/pages/AIAssistantPage';
import AlertsPage from '@/pages/AlertsPage';
import AuditTrailPage from '@/pages/AuditTrailPage';
import AdminUsersPage from '@/pages/AdminUsersPage';
import ImportExportPage from '@/pages/ImportExportPage';
import SettingsPage from '@/pages/SettingsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <div className="text-center">
          <div className="w-10 h-10 border-3 border-amber-brand border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-500">Loading KhanijSetu...</p>
        </div>
      </div>
    );
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  return isAuthenticated ? <Navigate to="/app" replace /> : <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><SignupPage /></PublicRoute>} />

          {/* Protected Dashboard */}
          <Route path="/app" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
            <Route index element={<DashboardPage />} />
            <Route path="mines" element={<MinesPage />} />
            <Route path="mines/:id" element={<MineProfilePage />} />
            <Route path="compliance" element={<CompliancePage />} />
            <Route path="inspections" element={<InspectionsPage />} />
            <Route path="violations" element={<ViolationsPage />} />
            <Route path="corrective-actions" element={<CorrectiveActionsPage />} />
            <Route path="contractors" element={<ContractorsPage />} />
            <Route path="production" element={<ProductionPage />} />
            <Route path="field-reports" element={<FieldReportsPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="risk" element={<RiskAnalyticsPage />} />
            <Route path="gis" element={<GISMapPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="ai-assistant" element={<AIAssistantPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="audit" element={<AuditTrailPage />} />
            <Route path="users" element={<AdminUsersPage />} />
            <Route path="import-export" element={<ImportExportPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
