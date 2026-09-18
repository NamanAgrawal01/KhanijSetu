import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import api from '@/lib/api';
import type { User, TokenResponse, UserRole } from '@/types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  demoLogin: (role: string) => Promise<void>;
  logout: () => void;
  hasModule: (module: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('khanijsetu_token');
    const savedUser = localStorage.getItem('khanijsetu_user');
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('khanijsetu_token');
        localStorage.removeItem('khanijsetu_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<TokenResponse>('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('khanijsetu_token', access_token);
    localStorage.setItem('khanijsetu_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
  }, []);

  const demoLogin = useCallback(async (role: string) => {
    const res = await api.post<TokenResponse>('/auth/demo-login', { role });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('khanijsetu_token', access_token);
    localStorage.setItem('khanijsetu_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('khanijsetu_token');
    localStorage.removeItem('khanijsetu_user');
    setToken(null);
    setUser(null);
  }, []);

  const hasModule = useCallback((module: string) => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return user.accessible_modules.includes(module);
  }, [user]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        demoLogin,
        logout,
        hasModule,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
