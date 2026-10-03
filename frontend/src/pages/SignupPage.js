import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !email.trim() || !password || !confirmPassword) {
      setError('Please complete all fields.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      // This is the exact function signature used by your AuthContext.js.
      await signup(name.trim(), email.trim(), password);
      navigate('/', { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        .ag-signup-page {
          --ag-text: #f7fbff;
          --ag-muted: #93a6c2;
          --ag-cyan: #25d4e9;
          position: relative;
          display: grid;
          grid-template-columns: minmax(260px, .82fr) minmax(420px, 1.18fr);
          gap: clamp(32px, 7vw, 112px);
          align-items: center;
          width: min(1240px, calc(100% - 48px));
          min-height: calc(100vh - 90px);
          margin: 0 auto;
          padding: 56px 0;
          overflow: hidden;
          color: var(--ag-text);
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .ag-signup-page, .ag-signup-page * { box-sizing: border-box; }
        .ag-signup-page::before { content: ''; position: fixed; z-index: -2; inset: 0; pointer-events: none; background: radial-gradient(circle at 12% 88%, rgba(0,102,255,.38), transparent 31rem), radial-gradient(circle at 84% 14%, rgba(0,203,255,.16), transparent 28rem), linear-gradient(135deg, #02040b 0%, #071327 52%, #02050e 100%); }
        .ag-signup-page::after { content: ''; position: fixed; z-index: -1; inset: 0; pointer-events: none; opacity: .18; background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px); background-size: 44px 44px; mask-image: linear-gradient(to bottom, black, transparent 80%); }

        .ag-brand, .ag-card { position: relative; z-index: 1; }
        .ag-brand { padding-left: 8px; }
        .ag-logo { display: inline-flex; align-items: center; gap: 12px; margin-bottom: 54px; font-size: 23px; font-weight: 800; letter-spacing: -1px; }
        .ag-logo-mark { display: grid; place-items: center; width: 42px; height: 48px; color: #9feaff; border: 2px solid #25aeff; border-radius: 14px 14px 19px 19px; box-shadow: 0 0 22px rgba(25,160,255,.58), inset 0 0 14px rgba(70,180,255,.22); transform: rotate(45deg); }
        .ag-logo-mark span { transform: rotate(-45deg); font-size: 25px; }
        .ag-logo strong { color: var(--ag-cyan); }
        .ag-eyebrow { margin: 0 0 18px; color: #5bc9ff; font-size: 12px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; }
        .ag-title { max-width: 430px; margin: 0 0 22px; font-size: clamp(38px, 5vw, 62px); line-height: 1.04; letter-spacing: -3px; }
        .ag-intro { max-width: 420px; margin: 0; color: var(--ag-muted); font-size: 16px; line-height: 1.8; }

        .ag-orbital-shield { position: relative; width: 260px; height: 220px; margin: 58px 0 0 54px; perspective: 700px; }
        .ag-orbital-shield::before, .ag-orbital-shield::after { content: ''; position: absolute; inset: 28px -42px; border: 1px solid rgba(50,176,255,.68); border-radius: 50%; box-shadow: 0 0 24px rgba(0,144,255,.5); transform: rotateX(66deg) rotateZ(-14deg); animation: ag-orbit 9s linear infinite; }
        .ag-orbital-shield::after { inset: 46px -24px; transform: rotateX(70deg) rotateZ(55deg); animation-duration: 12s; }
        .ag-shield { position: absolute; z-index: 2; left: 74px; top: 18px; width: 104px; height: 126px; clip-path: polygon(50% 0,94% 18%,86% 69%,50% 100%,14% 69%,6% 18%); background: linear-gradient(145deg, rgba(170,236,255,.55), rgba(20,80,190,.25) 35%, rgba(0,137,255,.75)); border: 1px solid rgba(180,238,255,.92); box-shadow: 0 0 36px #148cff, inset 0 0 26px rgba(185,244,255,.44); animation: ag-hover 4s ease-in-out infinite; }
        .ag-shield::after { content: 'A'; position: absolute; inset: 0; display: grid; place-items: center; color: #d8f7ff; font-size: 56px; font-weight: 800; text-shadow: 0 0 18px #fff; }

        .ag-card { width: 100%; padding: clamp(28px, 5vw, 54px); overflow: hidden; border: 1px solid rgba(151,198,255,.28); border-radius: 32px; background: linear-gradient(135deg, rgba(29,57,93,.54), rgba(7,19,40,.68)); box-shadow: 0 30px 90px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.2), 0 0 50px rgba(0,134,255,.1); backdrop-filter: blur(28px) saturate(140%); -webkit-backdrop-filter: blur(28px) saturate(140%); }
        .ag-card::before { content: ''; position: absolute; top: -140px; right: -120px; width: 320px; height: 260px; border-radius: 50%; background: rgba(64,176,255,.18); filter: blur(42px); pointer-events: none; }
        .ag-card-header { position: relative; margin-bottom: 30px; }
        .ag-card-title { margin: 0 0 10px; font-size: clamp(28px, 4vw, 39px); letter-spacing: -1.8px; }
        .ag-card-subtitle { margin: 0; color: var(--ag-muted); font-size: 14px; }
        .ag-form { position: relative; }
        .ag-field { margin-bottom: 18px; }
        .ag-label { display: block; margin: 0 0 9px; color: #e5efff; font-size: 13px; font-weight: 600; }
        .ag-input-wrap { position: relative; }
        .ag-icon { position: absolute; left: 16px; top: 50%; color: #8bbcff; font-size: 17px; transform: translateY(-50%); pointer-events: none; }
        .ag-input { width: 100%; height: 54px; padding: 0 58px 0 46px; color: var(--ag-text); font: inherit; font-size: 14px; outline: none; border: 1px solid rgba(144,192,247,.25); border-radius: 14px; background: rgba(2,12,29,.43); box-shadow: inset 0 1px 0 rgba(255,255,255,.08); transition: .25s ease; }
        .ag-input::placeholder { color: #8293ad; }
        .ag-input:focus { border-color: #34caff; background: rgba(8,27,56,.68); box-shadow: 0 0 0 4px rgba(31,189,255,.12), 0 0 24px rgba(23,140,255,.16); }
        .ag-toggle { position: absolute; top: 50%; right: 15px; padding: 4px; color: #91b4e8; border: 0; background: transparent; cursor: pointer; transform: translateY(-50%); }
        .ag-toggle:hover { color: #5fe0ff; }
        .ag-submit { position: relative; width: 100%; height: 56px; overflow: hidden; color: white; font: inherit; font-weight: 700; border: 0; border-radius: 14px; cursor: pointer; background: linear-gradient(100deg, #1069ed, #1bbde7); box-shadow: 0 12px 28px rgba(13,126,255,.3), inset 0 1px 0 rgba(255,255,255,.45); transition: transform .2s ease, box-shadow .2s ease; }
        .ag-submit:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 17px 35px rgba(13,126,255,.43), inset 0 1px 0 rgba(255,255,255,.5); }
        .ag-submit:disabled { cursor: wait; opacity: .7; }
        .ag-message { min-height: 18px; margin: 13px 0 0; text-align: center; font-size: 12px; }
        .ag-error { color: #ff7894; }
        .ag-login-prompt { margin: 24px 0 0; color: #9aabc4; text-align: center; font-size: 13px; }
        .ag-login-link { color: #55c9ff; text-decoration: none; }
        .ag-login-link:hover { text-decoration: underline; }
        .ag-float { position: absolute; z-index: 4; padding: 12px 15px; color: #a9c9f2; border: 1px solid rgba(150,211,255,.28); border-radius: 15px; background: rgba(23,55,95,.38); box-shadow: 0 18px 40px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.18); backdrop-filter: blur(16px); font-size: 11px; animation: ag-hover 5s ease-in-out infinite; }
        .ag-float strong { display: block; margin-top: 4px; color: #5fe0ff; font-size: 14px; }
        .ag-float-one { top: 4%; right: -6%; transform: rotate(8deg); }
        .ag-float-two { bottom: 6%; left: -8%; transform: rotate(-8deg); animation-delay: -2s; }
        @keyframes ag-hover { 0%,100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-13px) rotate(1deg); } }
        @keyframes ag-orbit { to { transform: rotateX(66deg) rotateZ(346deg); } }

        @media (max-width: 850px) {
          .ag-signup-page { grid-template-columns: 1fr; width: min(560px, calc(100% - 32px)); min-height: calc(100vh - 70px); padding: 34px 0; }
          .ag-brand { padding-left: 0; text-align: center; }
          .ag-logo { margin-bottom: 38px; }
          .ag-title, .ag-intro { margin-left: auto; margin-right: auto; }
          .ag-orbital-shield { display: none; }
          .ag-float-one { right: -3%; }
          .ag-float-two { left: -3%; }
        }
        @media (max-width: 480px) {
          .ag-card { padding: 26px 20px; border-radius: 24px; }
          .ag-float { display: none; }
        }
      `}</style>

      <main className="ag-signup-page">
        <section className="ag-brand" aria-label="AxiomGuard introduction">
          <div className="ag-logo">
            <span className="ag-logo-mark"><span>⌃</span></span>
            <span>Axiom<strong>Guard</strong></span>
          </div>
          <p className="ag-eyebrow">Next-generation protection</p>
          <h1 className="ag-title">Secure your workspace.</h1>
          <p className="ag-intro">
            Create your AxiomGuard account and bring intelligent threat detection,
            zero-trust access, and continuous visibility into one secure workspace.
          </p>
          <div className="ag-orbital-shield" aria-hidden="true"><div className="ag-shield" /></div>
        </section>

        <section className="ag-card">
          <div className="ag-float ag-float-one">Security posture<strong>Strong</strong></div>
          <div className="ag-float ag-float-two">Encryption<strong>Active</strong></div>

          <header className="ag-card-header">
            <h2 className="ag-card-title">Create account</h2>
            <p className="ag-card-subtitle">Join AxiomGuard today.</p>
          </header>

          <form className="ag-form" onSubmit={handleSubmit}>
            <div className="ag-field">
              <label className="ag-label" htmlFor="signup-name">Full name</label>
              <div className="ag-input-wrap"><span className="ag-icon">♙</span><input className="ag-input" id="signup-name" type="text" placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} required autoComplete="name" /></div>
            </div>

            <div className="ag-field">
              <label className="ag-label" htmlFor="signup-email">Email address</label>
              <div className="ag-input-wrap"><span className="ag-icon">✉</span><input className="ag-input" id="signup-email" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></div>
            </div>

            <div className="ag-field">
              <label className="ag-label" htmlFor="signup-password">Password</label>
              <div className="ag-input-wrap"><span className="ag-icon">♙</span><input className="ag-input" id="signup-password" type={showPassword ? 'text' : 'password'} placeholder="Password (min. 6 characters)" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="new-password" /><button className="ag-toggle" type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button></div>
            </div>

            <div className="ag-field">
              <label className="ag-label" htmlFor="signup-confirm-password">Confirm password</label>
              <div className="ag-input-wrap"><span className="ag-icon">♙</span><input className="ag-input" id="signup-confirm-password" type={showConfirmPassword ? 'text' : 'password'} placeholder="Confirm password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required autoComplete="new-password" /><button className="ag-toggle" type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>{showConfirmPassword ? 'Hide' : 'Show'}</button></div>
            </div>

            {error && <div className="ag-message ag-error" role="alert">{error}</div>}
            <button className="ag-submit" type="submit" disabled={loading}>{loading ? 'CREATING ACCOUNT...' : 'CREATE ACCOUNT'}</button>
          </form>

          <p className="ag-login-prompt">Already have an account? <Link className="ag-login-link" to="/login">Login</Link></p>
        </section>
      </main>
    </>
  );
}
