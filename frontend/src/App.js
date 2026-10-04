import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import ScanPage from './pages/ScanPage';
import PhishPage from './pages/PhishPage';
import GuardPage from './pages/GuardPage';
import HistoryPage from './pages/HistoryPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import './index.css';

function NavAuthControls() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (isAuthenticated) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
          👤 {user?.name}
        </span>
        <button
          onClick={handleLogout}
          style={{
            background: 'transparent',
            border: '1px solid #ef4444',
            color: '#ef4444',
            borderRadius: '6px',
            padding: '0.35rem 0.75rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '1px',
            cursor: 'pointer',
          }}
        >
          LOGOUT
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <NavLink to="/login">LOGIN</NavLink>
      <NavLink to="/signup">SIGN UP</NavLink>
    </div>
  );
}

function AppShell() {
  const { isAuthenticated } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <Router>
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">⚔ AXIOMGUARD</div>
          <div className="navbar-tagline">"Because security should be absolute."</div>
        </div>
        <button
          type="button"
          className={menuOpen ? 'nav-toggle open' : 'nav-toggle'}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((o) => !o)}
        >
          <span /><span /><span />
        </button>
        <ul
          className={menuOpen ? 'nav-links open' : 'nav-links'}
          onClick={() => setMenuOpen(false)}
        >
          {isAuthenticated && (
            <>
              <li><NavLink to="/" end>HOME</NavLink></li>
              <li><NavLink to="/scan">AXIOM//SCAN</NavLink></li>
              <li><NavLink to="/phish">AXIOM//PHISH</NavLink></li>
              <li><NavLink to="/guard">AXIOM//GUARD</NavLink></li>
              <li><NavLink to="/history">HISTORY</NavLink></li>
            </>
          )}
          <li><NavAuthControls /></li>
        </ul>
      </nav>

      <Routes>
        <Route path="/login"   element={<LoginPage />} />
        <Route path="/signup"  element={<SignupPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scan"
          element={
            <ProtectedRoute>
              <ScanPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/phish"
          element={
            <ProtectedRoute>
              <PhishPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/guard"
          element={
            <ProtectedRoute>
              <GuardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
