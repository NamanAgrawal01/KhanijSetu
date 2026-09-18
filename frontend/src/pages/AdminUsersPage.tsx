import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { formatDate } from '@/lib/utils';
import {
  Users, Plus, Edit2, X, Check, Loader2,
  Shield, ChevronDown, Search, UserCheck, UserX
} from 'lucide-react';

interface UserRecord {
  id: number;
  email: string;
  name: string;
  role: string;
  designation: string;
  phone: string;
  subsidiary_id: number | null;
  mine_id: number | null;
  is_active: boolean;
  subsidiary_name: string | null;
  created_at: string | null;
}

interface Subsidiary {
  id: number;
  name: string;
  code: string;
  region: string;
}

const ROLES = [
  { value: 'admin', label: 'Admin' },
  { value: 'inspector', label: 'Inspector' },
  { value: 'mine_operator', label: 'Mine Operator' },
  { value: 'analyst', label: 'Analyst' },
  { value: 'viewer', label: 'Viewer' },
];

export default function AdminUsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [subsidiaries, setSubsidiaries] = useState<Subsidiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Create form
  const [form, setForm] = useState({
    email: '', name: '', password: '', role: 'viewer',
    designation: '', phone: '', subsidiary_id: '' as string, mine_id: '' as string,
  });

  // Edit form
  const [editForm, setEditForm] = useState({
    name: '', designation: '', phone: '', role: '',
    subsidiary_id: '' as string, mine_id: '' as string,
  });

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const params: Record<string, string> = {};
      if (roleFilter) params.role = roleFilter;
      const res = await api.get('/users', { params });
      setUsers(res.data.users || []);
    } catch {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [roleFilter]);

  useEffect(() => {
    fetchUsers();
    api.get('/users/subsidiaries').then(r => setSubsidiaries(r.data || [])).catch(() => {});
  }, [fetchUsers]);

  const filteredUsers = users.filter(u => {
    if (!search) return true;
    const q = search.toLowerCase();
    return u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || u.role.includes(q);
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/users', {
        ...form,
        subsidiary_id: form.subsidiary_id ? Number(form.subsidiary_id) : null,
        mine_id: form.mine_id ? Number(form.mine_id) : null,
      });
      setSuccess('User created successfully');
      setShowCreate(false);
      setForm({ email: '', name: '', password: '', role: 'viewer', designation: '', phone: '', subsidiary_id: '', mine_id: '' });
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async (userId: number) => {
    setSaving(true);
    setError('');
    try {
      await api.put(`/users/${userId}`, {
        ...editForm,
        subsidiary_id: editForm.subsidiary_id ? Number(editForm.subsidiary_id) : null,
        mine_id: editForm.mine_id ? Number(editForm.mine_id) : null,
      });
      setSuccess('User updated');
      setEditId(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (userId: number) => {
    try {
      await api.patch(`/users/${userId}/disable`);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to toggle user status');
    }
  };

  const startEdit = (u: UserRecord) => {
    setEditId(u.id);
    setEditForm({
      name: u.name, designation: u.designation, phone: u.phone,
      role: u.role, subsidiary_id: u.subsidiary_id?.toString() || '',
      mine_id: u.mine_id?.toString() || '',
    });
  };

  // Auto-clear messages
  useEffect(() => {
    if (success) { const t = setTimeout(() => setSuccess(''), 3000); return () => clearTimeout(t); }
  }, [success]);
  useEffect(() => {
    if (error) { const t = setTimeout(() => setError(''), 5000); return () => clearTimeout(t); }
  }, [error]);

  if (user?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">You do not have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-7 h-7 text-amber-brand" />
            User Management
          </h1>
          <p className="text-sm text-gray-500 mt-1">{users.length} registered users</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-amber-brand text-charcoal font-semibold rounded-lg hover:bg-amber-hover transition-colors"
        >
          <Plus className="w-4 h-4" /> Add User
        </button>
      </div>

      {/* Messages */}
      {success && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700 flex items-center gap-2">
          <Check className="w-4 h-4" /> {success}
        </div>
      )}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search users..."
            className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand focus:ring-2 focus:ring-amber-brand/20"
          />
        </div>
        <div className="relative">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="appearance-none pl-3 pr-8 py-2.5 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:border-amber-brand"
          >
            <option value="">All Roles</option>
            {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
          </select>
          <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-gray-900">Create New User</h3>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Name *</label>
                  <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Email *</label>
                  <input required type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Password *</label>
                  <input required type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Role *</label>
                  <select value={form.role} onChange={e => setForm({...form, role: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:border-amber-brand">
                    {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Designation</label>
                  <input value={form.designation} onChange={e => setForm({...form, designation: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Phone</label>
                  <input value={form.phone} onChange={e => setForm({...form, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Subsidiary</label>
                  <select value={form.subsidiary_id} onChange={e => setForm({...form, subsidiary_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:border-amber-brand">
                    <option value="">None</option>
                    {subsidiaries.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Mine ID</label>
                  <input type="number" value={form.mine_id} onChange={e => setForm({...form, mine_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand" />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Cancel</button>
                <button type="submit" disabled={saving}
                  className="px-4 py-2 bg-amber-brand text-charcoal font-semibold text-sm rounded-lg hover:bg-amber-hover transition-colors disabled:opacity-50 flex items-center gap-2">
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />} Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-700">User</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Role</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700 hidden md:table-cell">Designation</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700 hidden lg:table-cell">Subsidiary</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700 hidden lg:table-cell">Created</th>
                <th className="text-center px-4 py-3 font-semibold text-gray-700">Status</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center py-12">
                  <Loader2 className="w-6 h-6 animate-spin text-amber-brand mx-auto" />
                </td></tr>
              ) : filteredUsers.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-12 text-gray-400">No users found</td></tr>
              ) : filteredUsers.map(u => (
                <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50/50">
                  <td className="px-4 py-3">
                    {editId === u.id ? (
                      <input value={editForm.name} onChange={e => setEditForm({...editForm, name: e.target.value})}
                        className="w-full px-2 py-1 border border-amber-brand rounded text-sm" />
                    ) : (
                      <div>
                        <p className="font-medium text-gray-900">{u.name}</p>
                        <p className="text-xs text-gray-500">{u.email}</p>
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {editId === u.id ? (
                      <select value={editForm.role} onChange={e => setEditForm({...editForm, role: e.target.value})}
                        className="px-2 py-1 border border-amber-brand rounded text-sm bg-white">
                        {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                      </select>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                        <Shield className="w-3 h-3" />
                        {ROLES.find(r => r.value === u.role)?.label || u.role}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell text-gray-600">
                    {editId === u.id ? (
                      <input value={editForm.designation} onChange={e => setEditForm({...editForm, designation: e.target.value})}
                        className="w-full px-2 py-1 border border-amber-brand rounded text-sm" />
                    ) : u.designation || '—'}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell text-gray-600">{u.subsidiary_name || '—'}</td>
                  <td className="px-4 py-3 hidden lg:table-cell text-gray-500 text-xs">{formatDate(u.created_at)}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-block w-2 h-2 rounded-full ${u.is_active ? 'bg-emerald-500' : 'bg-gray-300'}`} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      {editId === u.id ? (
                        <>
                          <button onClick={() => handleUpdate(u.id)} disabled={saving}
                            className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded">
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                          </button>
                          <button onClick={() => setEditId(null)} className="p-1.5 text-gray-400 hover:bg-gray-100 rounded">
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button onClick={() => startEdit(u)} className="p-1.5 text-gray-400 hover:text-amber-brand hover:bg-amber-50 rounded" title="Edit">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          {u.id !== user?.id && (
                            <button onClick={() => handleToggle(u.id)}
                              className={`p-1.5 rounded ${u.is_active ? 'text-gray-400 hover:text-red-500 hover:bg-red-50' : 'text-gray-400 hover:text-emerald-600 hover:bg-emerald-50'}`}
                              title={u.is_active ? 'Disable' : 'Enable'}>
                              {u.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
