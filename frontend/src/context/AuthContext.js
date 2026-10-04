import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On first load, check if we already have a token + user saved locally.
  // We trust localStorage for the initial paint, then quietly verify
  // with the backend via /api/auth/me.
  useEffect(() => {
    const token = localStorage.getItem('axiomguard_token');
    const savedUser = localStorage.getItem('axiomguard_user');

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        // corrupted local data — ignore
      }

      api.get('/api/auth/me')
        .then((res) => {
          setUser(res.data);
          localStorage.setItem('axiomguard_user', JSON.stringify(res.data));
        })
        .catch(() => {
          // token invalid/expired — log out silently
          localStorage.removeItem('axiomguard_token');
          localStorage.removeItem('axiomguard_user');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password });
    const { access_token, user: loggedInUser } = res.data;
    localStorage.setItem('axiomguard_token', access_token);
    localStorage.setItem('axiomguard_user', JSON.stringify(loggedInUser));
    setUser(loggedInUser);
    return loggedInUser;
  };

  const signup = async (name, email, password) => {
    const res = await api.post('/api/auth/signup', { name, email, password });
    const { access_token, user: newUser } = res.data;
    localStorage.setItem('axiomguard_token', access_token);
    localStorage.setItem('axiomguard_user', JSON.stringify(newUser));
    setUser(newUser);
    return newUser;
  };

  const logout = () => {
    localStorage.removeItem('axiomguard_token');
    localStorage.removeItem('axiomguard_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
