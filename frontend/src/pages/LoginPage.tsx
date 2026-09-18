import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Mountain, Eye, EyeOff, Shield, ChevronRight, Loader2 } from 'lucide-react';

const QUICK_ACCESS_ROLES = [
  { role: 'admin', label: 'Admin', desc: 'Full platform access' },
  { role: 'mine_operator', label: 'Mine Operator', desc: 'Mine operations' },
  { role: 'inspector', label: 'Inspector', desc: 'Field inspections' },
  { role: 'analyst', label: 'Analyst', desc: 'Analytics & oversight' },
  { role: 'viewer', label: 'Viewer', desc: 'Read-only access' },
];

export default function LoginPage() {
  const { login, demoLogin } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setError('Please enter email and password'); return; }
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/app');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials. Try a demo account.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role: string) => {
    setError('');
    setDemoLoading(role);
    try {
      await demoLogin(role);
      navigate('/app');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Demo login failed. Ensure backend is running.');
    } finally {
      setDemoLoading(null);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-[55%] bg-charcoal relative flex-col justify-between p-10 overflow-hidden">
        {/* Geometric background */}
        <div className="absolute inset-0 opacity-[0.04]">
          <div className="absolute top-20 left-10 w-96 h-96 border border-white/20 rotate-45" />
          <div className="absolute bottom-20 right-10 w-72 h-72 border border-white/20 rotate-12" />
          <div className="absolute top-1/2 left-1/3 w-48 h-48 border border-amber-brand/30 rotate-[30deg]" />
        </div>
        {/* Abstract mining layers */}
        <div className="absolute bottom-0 left-0 right-0 h-48 opacity-5">
          <div className="absolute bottom-0 left-0 right-0 h-12 bg-amber-brand/40" />
          <div className="absolute bottom-12 left-0 right-0 h-16 bg-gray-600/40" />
          <div className="absolute bottom-28 left-0 right-0 h-20 bg-gray-700/40" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-amber-brand rounded-xl flex items-center justify-center">
              <Mountain className="w-6 h-6 text-charcoal" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">KhanijSetu</span>
          </div>
        </div>

        <div className="relative z-10 max-w-lg">
          <h2 className="text-3xl font-bold text-white leading-snug mb-4">
            Intelligent Governance for<br />
            <span className="text-amber-brand">Safer, Smarter Mining</span>
          </h2>
          <p className="text-gray-400 text-[15px] leading-relaxed mb-8">
            An integrated digital governance platform for compliance monitoring, safety intelligence,
            field operations and risk management across coal mining operations in India.
          </p>

          <div className="grid grid-cols-2 gap-3">
            {[
              { n: 'Real-Time', l: 'Compliance Monitoring' },
              { n: 'AI-Driven', l: 'Risk Analysis' },
              { n: '24/7', l: 'Safety Intelligence' },
              { n: '5', l: 'Role-Based Views' },
            ].map((s, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3">
                <p className="text-2xl font-bold text-white">{s.n}</p>
                <p className="text-xs text-gray-500">{s.l}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-xs text-gray-600">
          <Shield className="w-3.5 h-3.5" />
          <span>Secured & Compliant · Government-grade Infrastructure</span>
        </div>
      </div>

      {/* Right Panel — Login Form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile brand */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-amber-brand rounded-lg flex items-center justify-center">
              <Mountain className="w-5 h-5 text-charcoal" />
            </div>
            <span className="text-lg font-bold text-charcoal">KhanijSetu</span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">Sign in to your account</h2>
          <p className="text-sm text-gray-500 mb-8">Access the mining governance platform</p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@khanijsetu.gov.in"
                className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm outline-none focus:border-amber-brand focus:ring-2 focus:ring-amber-brand/20 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm outline-none focus:border-amber-brand focus:ring-2 focus:ring-amber-brand/20 transition-all pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded border-gray-300 text-amber-brand focus:ring-amber-brand/30" />
                <span className="text-gray-600">Remember me</span>
              </label>
              <button type="button" className="text-amber-brand hover:text-amber-hover font-medium">
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-amber-brand hover:bg-amber-hover text-charcoal font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Sign In
            </button>
          </form>

          {/* Demo Access */}
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-white px-3 text-gray-500">Quick Access</span>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
              {QUICK_ACCESS_ROLES.map((d) => (
                <button
                  key={d.role}
                  onClick={() => handleDemoLogin(d.role)}
                  disabled={!!demoLoading}
                  className="flex flex-col items-start px-3 py-2.5 border border-gray-200 rounded-lg hover:border-amber-brand/40 hover:bg-amber-brand/5 transition-all text-left disabled:opacity-50 group"
                >
                  {demoLoading === d.role ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-brand mb-1" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-gray-400 group-hover:text-amber-brand mb-1 transition-colors" />
                  )}
                  <span className="text-xs font-semibold text-gray-700">{d.label}</span>
                  <span className="text-[10px] text-gray-400">{d.desc}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
