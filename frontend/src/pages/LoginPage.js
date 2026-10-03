import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);

    try {
      // This is the exact function signature used by your AuthContext.js.
      await login(email.trim(), password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Login failed. Check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        .ag-login-page { --ag-text:#f7fbff; --ag-muted:#93a6c2; --ag-cyan:#25d4e9; position:relative; display:grid; grid-template-columns:minmax(260px,.82fr) minmax(420px,1.18fr); gap:clamp(32px,7vw,112px); align-items:center; width:min(1240px,calc(100% - 48px)); min-height:calc(100vh - 90px); margin:0 auto; padding:56px 0; overflow:hidden; color:var(--ag-text); font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
        .ag-login-page, .ag-login-page * { box-sizing:border-box; }
        .ag-login-page::before { content:''; position:fixed; z-index:-2; inset:0; pointer-events:none; background:radial-gradient(circle at 12% 88%,rgba(0,102,255,.38),transparent 31rem),radial-gradient(circle at 84% 14%,rgba(0,203,255,.16),transparent 28rem),linear-gradient(135deg,#02040b 0%,#071327 52%,#02050e 100%); }
        .ag-login-page::after { content:''; position:fixed; z-index:-1; inset:0; pointer-events:none; opacity:.18; background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px); background-size:44px 44px; mask-image:linear-gradient(to bottom,black,transparent 80%); }
        .ag-login-brand, .ag-login-card { position:relative; z-index:1; }
        .ag-login-brand { padding-left:8px; }
        .ag-login-logo { display:inline-flex; align-items:center; gap:12px; margin-bottom:54px; font-size:23px; font-weight:800; letter-spacing:-1px; }
        .ag-login-logo-mark { display:grid; place-items:center; width:42px; height:48px; color:#9feaff; border:2px solid #25aeff; border-radius:14px 14px 19px 19px; box-shadow:0 0 22px rgba(25,160,255,.58),inset 0 0 14px rgba(70,180,255,.22); transform:rotate(45deg); }
        .ag-login-logo-mark span { transform:rotate(-45deg); font-size:25px; }
        .ag-login-logo strong { color:var(--ag-cyan); }
        .ag-login-eyebrow { margin:0 0 18px; color:#5bc9ff; font-size:12px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; }
        .ag-login-title { max-width:430px; margin:0 0 22px; font-size:clamp(38px,5vw,62px); line-height:1.04; letter-spacing:-3px; }
        .ag-login-intro { max-width:420px; margin:0; color:var(--ag-muted); font-size:16px; line-height:1.8; }
        .ag-login-orbit { position:relative; width:260px; height:220px; margin:58px 0 0 54px; perspective:700px; }
        .ag-login-orbit::before, .ag-login-orbit::after { content:''; position:absolute; inset:28px -42px; border:1px solid rgba(50,176,255,.68); border-radius:50%; box-shadow:0 0 24px rgba(0,144,255,.5); transform:rotateX(66deg) rotateZ(-14deg); animation:ag-login-orbit 9s linear infinite; }
        .ag-login-orbit::after { inset:46px -24px; transform:rotateX(70deg) rotateZ(55deg); animation-duration:12s; }
        .ag-login-shield { position:absolute; z-index:2; left:74px; top:18px; width:104px; height:126px; clip-path:polygon(50% 0,94% 18%,86% 69%,50% 100%,14% 69%,6% 18%); background:linear-gradient(145deg,rgba(170,236,255,.55),rgba(20,80,190,.25) 35%,rgba(0,137,255,.75)); border:1px solid rgba(180,238,255,.92); box-shadow:0 0 36px #148cff,inset 0 0 26px rgba(185,244,255,.44); animation:ag-login-hover 4s ease-in-out infinite; }
        .ag-login-shield::after { content:'A'; position:absolute; inset:0; display:grid; place-items:center; color:#d8f7ff; font-size:56px; font-weight:800; text-shadow:0 0 18px #fff; }
        .ag-login-card { width:100%; padding:clamp(28px,5vw,54px); overflow:hidden; border:1px solid rgba(151,198,255,.28); border-radius:32px; background:linear-gradient(135deg,rgba(29,57,93,.54),rgba(7,19,40,.68)); box-shadow:0 30px 90px rgba(0,0,0,.48),inset 0 1px 0 rgba(255,255,255,.2),0 0 50px rgba(0,134,255,.1); backdrop-filter:blur(28px) saturate(140%); -webkit-backdrop-filter:blur(28px) saturate(140%); }
        .ag-login-card::before { content:''; position:absolute; top:-140px; right:-120px; width:320px; height:260px; border-radius:50%; background:rgba(64,176,255,.18); filter:blur(42px); pointer-events:none; }
        .ag-login-float { position:absolute; z-index:4; padding:12px 15px; color:#a9c9f2; border:1px solid rgba(150,211,255,.28); border-radius:15px; background:rgba(23,55,95,.38); box-shadow:0 18px 40px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.18); backdrop-filter:blur(16px); font-size:11px; animation:ag-login-hover 5s ease-in-out infinite; }
        .ag-login-float strong { display:block; margin-top:4px; color:#5fe0ff; font-size:14px; }
        .ag-login-float-one { top:4%; right:-6%; transform:rotate(8deg); }
        .ag-login-float-two { bottom:6%; left:-8%; transform:rotate(-8deg); animation-delay:-2s; }
        .ag-login-header { position:relative; margin-bottom:30px; }
        .ag-login-heading { margin:0 0 10px; font-size:clamp(28px,4vw,39px); letter-spacing:-1.8px; }
        .ag-login-subtitle { margin:0; color:var(--ag-muted); font-size:14px; }
        .ag-login-form { position:relative; }
        .ag-login-field { margin-bottom:20px; }
        .ag-login-label { display:block; margin:0 0 9px; color:#e5efff; font-size:13px; font-weight:600; }
        .ag-login-input-wrap { position:relative; }
        .ag-login-icon { position:absolute; left:16px; top:50%; color:#8bbcff; font-size:17px; transform:translateY(-50%); pointer-events:none; }
        .ag-login-input { width:100%; height:56px; padding:0 58px 0 46px; color:var(--ag-text); font:inherit; font-size:14px; outline:none; border:1px solid rgba(144,192,247,.25); border-radius:14px; background:rgba(2,12,29,.43); box-shadow:inset 0 1px 0 rgba(255,255,255,.08); transition:.25s ease; }
        .ag-login-input::placeholder { color:#8293ad; }
        .ag-login-input:focus { border-color:#34caff; background:rgba(8,27,56,.68); box-shadow:0 0 0 4px rgba(31,189,255,.12),0 0 24px rgba(23,140,255,.16); }
        .ag-login-toggle { position:absolute; top:50%; right:15px; padding:4px; color:#91b4e8; border:0; background:transparent; cursor:pointer; transform:translateY(-50%); }
        .ag-login-toggle:hover { color:#5fe0ff; }
        .ag-login-submit { position:relative; width:100%; height:56px; margin-top:8px; overflow:hidden; color:white; font:inherit; font-weight:700; border:0; border-radius:14px; cursor:pointer; background:linear-gradient(100deg,#1069ed,#1bbde7); box-shadow:0 12px 28px rgba(13,126,255,.3),inset 0 1px 0 rgba(255,255,255,.45); transition:transform .2s ease,box-shadow .2s ease; }
        .ag-login-submit:hover:not(:disabled) { transform:translateY(-2px); box-shadow:0 17px 35px rgba(13,126,255,.43),inset 0 1px 0 rgba(255,255,255,.5); }
        .ag-login-submit:disabled { cursor:wait; opacity:.7; }
        .ag-login-error { min-height:18px; margin:13px 0 0; color:#ff7894; text-align:center; font-size:12px; }
        .ag-login-prompt { margin:24px 0 0; color:#9aabc4; text-align:center; font-size:13px; }
        .ag-login-link { color:#55c9ff; text-decoration:none; }
        .ag-login-link:hover { text-decoration:underline; }
        @keyframes ag-login-hover { 0%,100% { transform:translateY(0) rotate(0); } 50% { transform:translateY(-13px) rotate(1deg); } }
        @keyframes ag-login-orbit { to { transform:rotateX(66deg) rotateZ(346deg); } }
        @media (max-width:850px) { .ag-login-page { grid-template-columns:1fr; width:min(560px,calc(100% - 32px)); min-height:calc(100vh - 70px); padding:34px 0; } .ag-login-brand { padding-left:0; text-align:center; } .ag-login-logo { margin-bottom:38px; } .ag-login-title, .ag-login-intro { margin-left:auto; margin-right:auto; } .ag-login-orbit { display:none; } .ag-login-float-one { right:-3%; } .ag-login-float-two { left:-3%; } }
        @media (max-width:480px) { .ag-login-card { padding:26px 20px; border-radius:24px; } .ag-login-float { display:none; } }
      `}</style>

      <main className="ag-login-page">
        <section className="ag-login-brand" aria-label="AxiomGuard introduction">
          <div className="ag-login-logo"><span className="ag-login-logo-mark"><span>⌃</span></span><span>Axiom<strong>Guard</strong></span></div>
          <p className="ag-login-eyebrow">Next-generation protection</p>
          <h1 className="ag-login-title">Welcome back.</h1>
          <p className="ag-login-intro">Sign in to view your personal scan history, monitor threats, and keep your workspace protected with AxiomGuard.</p>
          <div className="ag-login-orbit" aria-hidden="true"><div className="ag-login-shield" /></div>
        </section>

        <section className="ag-login-card">
          <div className="ag-login-float ag-login-float-one">Security posture<strong>Strong</strong></div>
          <div className="ag-login-float ag-login-float-two">Protection<strong>Active</strong></div>

          <header className="ag-login-header">
            <h2 className="ag-login-heading">Welcome back</h2>
            <p className="ag-login-subtitle">Sign in to your secure workspace.</p>
          </header>

          <form className="ag-login-form" onSubmit={handleSubmit}>
            <div className="ag-login-field">
              <label className="ag-login-label" htmlFor="login-email">Email address</label>
              <div className="ag-login-input-wrap"><span className="ag-login-icon">✉</span><input className="ag-login-input" id="login-email" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></div>
            </div>

            <div className="ag-login-field">
              <label className="ag-login-label" htmlFor="login-password">Password</label>
              <div className="ag-login-input-wrap"><span className="ag-login-icon">♙</span><input className="ag-login-input" id="login-password" type={showPassword ? 'text' : 'password'} placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" /><button className="ag-login-toggle" type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button></div>
            </div>

            {error && <div className="ag-login-error" role="alert">{error}</div>}
            <button className="ag-login-submit" type="submit" disabled={loading}>{loading ? 'LOGGING IN...' : 'LOGIN'}</button>
          </form>

          <p className="ag-login-prompt">Don't have an account? <Link className="ag-login-link" to="/signup">Sign up</Link></p>
        </section>
      </main>
    </>
  );
}
