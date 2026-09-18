// ==========================================
// KhanijSetu — TypeScript Types
// Mirrors backend Pydantic schemas
// ==========================================

// === Auth ===
export interface LoginRequest {
  email: string;
  password: string;
}

export interface DemoLoginRequest {
  role: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  designation: string;
  phone: string;
  subsidiary_id: number | null;
  mine_id: number | null;
  is_active: boolean;
  avatar_url: string;
  accessible_modules: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type UserRole = 'admin' | 'inspector' | 'mine_operator' | 'analyst' | 'viewer';

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrator',
  inspector: 'Inspector',
  mine_operator: 'Mine Operator',
  analyst: 'Analyst',
  viewer: 'Viewer',
};

// === Mine ===
export interface Mine {
  id: number;
  name: string;
  code: string;
  subsidiary_id: number;
  subsidiary_name?: string;
  location: string;
  district: string;
  state: string;
  latitude: number;
  longitude: number;
  mine_type: string;
  manager_id: number | null;
  manager_name: string;
  capacity_mtpa: number;
  num_workers: number;
  status: string;
  compliance_score: number;
  risk_score: number;
  safety_score: number;
  environment_score: number;
  labour_score: number;
  production_score: number;
  open_violations: number;
  last_inspection_date: string | null;
  created_at: string;
}

export interface MineCreate {
  name: string;
  code: string;
  subsidiary_id: number;
  location?: string;
  district?: string;
  state?: string;
  latitude?: number;
  longitude?: number;
  mine_type?: string;
  manager_name?: string;
  capacity_mtpa?: number;
  num_workers?: number;
}

export interface MineListResponse {
  mines: Mine[];
  total: number;
}

// === Compliance ===
export interface ComplianceRequirement {
  id: number;
  title: string;
  category: string;
  description: string;
  frequency: string;
  authority: string;
  regulation_ref: string;
}

export interface ComplianceRecord {
  id: number;
  requirement_id: number;
  requirement_title?: string;
  mine_id: number;
  mine_name?: string;
  status: ComplianceStatus;
  due_date: string;
  completed_date: string | null;
  evidence_url: string | null;
  notes: string | null;
  responsible_officer: string;
  risk_level: string;
  category?: string;
  created_at: string;
}

export type ComplianceStatus = 'completed' | 'pending' | 'due_soon' | 'overdue';

export interface ComplianceListResponse {
  records: ComplianceRecord[];
  total: number;
  requirements: ComplianceRequirement[];
}

export interface ComplianceUpdate {
  status?: string;
  notes?: string;
  evidence_url?: string;
}

// === Inspection ===
export interface Inspection {
  id: number;
  mine_id: number;
  mine_name?: string;
  inspector_id: number;
  inspector_name?: string;
  inspection_type: string;
  scheduled_date: string;
  completed_date: string | null;
  status: string;
  priority: string;
  overall_rating: string | null;
  findings_summary: string | null;
  recommendations: string | null;
  gps_latitude: number | null;
  gps_longitude: number | null;
  items?: InspectionItem[];
  created_at: string;
}

export interface InspectionItem {
  id: number;
  inspection_id: number;
  category: string;
  item_name: string;
  status: string;
  severity: string | null;
  notes: string | null;
  photo_url: string | null;
}

export interface InspectionCreate {
  mine_id: number;
  inspector_id: number;
  inspection_type: string;
  scheduled_date: string;
  priority: string;
}

export interface InspectionListResponse {
  inspections: Inspection[];
  total: number;
  scheduled: number;
  in_progress: number;
  completed: number;
  overdue: number;
}

// === Violation ===
export interface Violation {
  id: number;
  violation_code: string;
  mine_id: number;
  mine_name?: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  reported_by: number | null;
  reported_by_name: string;
  assigned_to: number | null;
  assigned_to_name: string;
  detected_date: string;
  deadline: string | null;
  status: ViolationStatus;
  resolution_notes: string | null;
  evidence_url: string | null;
  inspection_id: number | null;
  is_recurring: boolean;
  recurrence_count: number;
  created_at: string;
}

export type ViolationStatus = 'detected' | 'assigned' | 'in_progress' | 'resolved' | 'verified' | 'closed';

export interface ViolationCreate {
  mine_id: number;
  category: string;
  severity: string;
  title: string;
  description: string;
  reported_by_name?: string;
  assigned_to_name?: string;
  deadline?: string;
}

export interface ViolationListResponse {
  violations: Violation[];
  total: number;
}

// === Corrective Action ===
export interface CorrectiveAction {
  id: number;
  action_code: string;
  violation_id: number;
  violation_title?: string;
  mine_id: number;
  mine_name?: string;
  title: string;
  description: string;
  assigned_to: number | null;
  assigned_to_name: string;
  deadline: string;
  priority: string;
  status: CorrectiveActionStatus;
  evidence_url: string | null;
  evidence_notes: string | null;
  verified_by: number | null;
  verified_by_name: string | null;
  verified_date: string | null;
  verification_notes: string | null;
  created_at: string;
}

export type CorrectiveActionStatus = 'pending' | 'in_progress' | 'overdue' | 'submitted' | 'verified' | 'closed';

export interface CorrectiveActionCreate {
  violation_id: number;
  mine_id: number;
  title: string;
  description: string;
  assigned_to_name?: string;
  deadline: string;
  priority: string;
}

export interface CorrectiveActionListResponse {
  actions: CorrectiveAction[];
  total: number;
}

// === Document ===
export interface Document {
  id: number;
  name: string;
  document_type: string;
  mine_id: number;
  mine_name?: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  uploaded_by: number | null;
  uploaded_by_name: string;
  processing_status: string;
  ocr_text: string | null;
  created_at: string;
  analysis?: DocumentAnalysis;
}

export interface DocumentAnalysis {
  id: number;
  document_id: number;
  summary: string;
  document_category: string;
  extracted_mine: string;
  extracted_date: string;
  extracted_inspector: string;
  extracted_expiry: string;
  key_findings: string[];
  issues_high: number;
  issues_medium: number;
  issues_low: number;
  issues_details: Array<{ severity: string; description: string; regulation: string }>;
  recommendations: string[];
  compliance_status: string;
  risk_indicators: string[];
  confidence_score: number;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

// === Contractor ===
export interface Contractor {
  id: number;
  name: string;
  company: string | null;
  mine_id: number;
  mine_name?: string;
  contract_type: string | null;
  contract_start: string | null;
  contract_end: string | null;
  num_workers: number;
  safety_score: number;
  violation_count: number;
  compliance_status: string;
  performance_rating: string;
  status: string;
  created_at: string;
}

export interface ContractorListResponse {
  contractors: Contractor[];
  total: number;
  active: number;
  expiring_soon: number;
  non_compliant: number;
}

// === Production ===
export interface ProductionRecord {
  id: number;
  mine_id: number;
  mine_name?: string;
  date: string;
  shift: string;
  target_tonnes: number;
  actual_tonnes: number;
  overburden_removed: number;
  equipment_hours: number;
  downtime_hours: number;
  downtime_reason: string | null;
  safety_incidents: number;
}

export interface ProductionListResponse {
  records: ProductionRecord[];
  total: number;
  daily_avg_target: number;
  daily_avg_actual: number;
  total_downtime: number;
}

// === Field Report ===
export interface FieldReport {
  id: number;
  report_code: string;
  mine_id: number;
  mine_name?: string;
  reporter_id: number;
  reporter_name: string;
  observation_type: string;
  severity: string;
  title: string | null;
  description: string;
  latitude: number | null;
  longitude: number | null;
  location_label: string | null;
  photo_url: string | null;
  status: string;
  sync_status: string;
  created_at: string;
}

export interface FieldReportCreate {
  mine_id: number;
  observation_type: string;
  severity: string;
  title?: string;
  description: string;
  latitude?: number;
  longitude?: number;
  location_label?: string;
  photo_url?: string;
}

export interface FieldReportListResponse {
  reports: FieldReport[];
  total: number;
}

// === Alert ===
export interface Alert {
  id: number;
  mine_id: number | null;
  mine_name: string | null;
  type: string;
  severity: string;
  title: string;
  message: string | null;
  status: string;
  escalation_level: number;
  source: string | null;
  link: string | null;
  created_at: string;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  critical: number;
  high: number;
  warning: number;
  info: number;
}

// === Audit ===
export interface AuditLog {
  id: number;
  user_name: string | null;
  user_role: string | null;
  action: string;
  module: string;
  entity: string | null;
  entity_id: number | null;
  details: string | null;
  status: string;
  created_at: string;
}

export interface AuditLogListResponse {
  logs: AuditLog[];
  total: number;
}

// === Dashboard ===
export interface DashboardData {
  total_mines: number;
  overall_compliance: number;
  high_risk_mines: number;
  critical_issues: number;
  open_violations: number;
  pending_actions: number;
  compliance_trend: Array<{ month: string; compliance: number }>;
  compliance_by_category: Array<{ category: string; score: number }>;
  risk_distribution: Array<{ level: string; count: number; color: string }>;
  violations_by_category: Array<{ category: string; count: number }>;
  high_risk_mine_list: Array<{
    id: number;
    name: string;
    subsidiary_name: string;
    location: string;
    compliance_score: number;
    risk_score: number;
    open_violations: number;
    last_inspection: string;
  }>;
  recent_activity: Array<{
    id: number;
    user: string;
    action: string;
    module: string;
    entity: string;
    details: string;
    time: string;
    status: string;
  }>;
}

// === Risk ===
export interface RiskData {
  mine_id: number;
  mine_name: string;
  risk_score: number;
  risk_level: string;
  factors: Array<{ factor: string; weight: number; detail: string }>;
  explanation: string;
  trend: Array<{ month: string; score: number }>;
  recommendations: string[];
}

// === AI ===
export interface AIQueryRequest {
  query: string;
  context?: Record<string, unknown>;
}

export interface AIQueryResponse {
  answer: string;
  data: Record<string, unknown> | null;
  entities: Array<{ name: string; [key: string]: unknown }>;
  recommendations: string[];
  confidence: number;
}

// === Reports ===
export interface ReportRequest {
  report_type: string;
  mine_id?: number;
  start_date?: string;
  end_date?: string;
}

export interface ReportResponse {
  id: string;
  report_type: string;
  title: string;
  generated_at: string;
  data: unknown;
  summary: string;
}
