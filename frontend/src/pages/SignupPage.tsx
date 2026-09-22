import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Mountain, Eye, EyeOff, Shield, Loader2 } from 'lucide-react';

export default function SignupPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) { setError('Please fill in all fields'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setError('');
    setLoading(true);
    try {
      await register(name, email, password);
      navigate('/app');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
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
            Join KhanijSetu for<br />
            <span className="text-amber-brand">Transparency & Safety</span>
          </h2>
          <p className="text-gray-400 text-[15px] leading-relaxed mb-8">
            Create an account to view and access public compliance data, safety records, and general insights into Indian coal mining operations.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-xs text-gray-600">
          <Shield className="w-3.5 h-3.5" />
          <span>Secured & Compliant · Government-grade Infrastructure</span>
        </div>
      </div>

      {/* Right Panel — Signup Form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile brand */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-amber-brand rounded-lg flex items-center justify-center">
              <Mountain className="w-5 h-5 text-charcoal" />
            </div>
            <span className="text-lg font-bold text-charcoal">KhanijSetu</span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">Create an account</h2>
          <p className="text-sm text-gray-500 mb-8">Sign up for viewer access to the platform</p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ramesh Kumar"
                className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm outline-none focus:border-amber-brand focus:ring-2 focus:ring-amber-brand/20 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
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
              <p className="mt-1.5 text-xs text-gray-500">Must be at least 6 characters.</p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-amber-brand hover:bg-amber-hover text-charcoal font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-60 mt-6"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Sign Up
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-8 text-center text-sm">
            <span className="text-gray-500">Already have an account? </span>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-amber-brand hover:text-amber-hover font-semibold transition-colors"
            >
              Sign In
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
