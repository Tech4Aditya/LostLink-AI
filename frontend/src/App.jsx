import React, { useEffect, useMemo, useState } from "react";
import { Routes, Route, Link, useNavigate, Navigate, useLocation } from "react-router-dom";
import {
  ArrowRight, Check, ChevronRight, CircleUserRound, FilePlus2, ImagePlus,
  LayoutDashboard, LogIn, LogOut, MapPin, Moon, PackageSearch, Search,
  ShieldCheck, Sun, UserRound, X
} from "lucide-react";
import { api, assetUrl, token } from "./api";

const THEME_KEY = "lostlink_theme";

function useTheme() {
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || "light");
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);
  return [theme, () => setTheme((v) => v === "dark" ? "light" : "dark")];
}

function ThemeButton() {
  const [theme, toggle] = useTheme();
  return <button className="theme-btn" onClick={toggle} title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`} aria-label="Toggle theme">
    {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
  </button>;
}

function Shell({ children, user, setUser }) {
  const nav = useNavigate();
  const location = useLocation();
  function logout() {
    localStorage.removeItem("lostlink_token");
    setUser(null);
    nav("/login");
  }
  return <div className="app">
    <header className="topbar">
      <Link className="brand" to="/" aria-label="LostLink home">
        <span className="brandmark">L</span>
        <span>lostlink</span>
      </Link>
      <nav className="mainnav">
        <Link className={location.pathname === "/" ? "active" : ""} to="/"><LayoutDashboard size={16}/> Overview</Link>
        <Link className={location.pathname === "/report" ? "active" : ""} to="/report"><FilePlus2 size={16}/> Report</Link>
        <Link className={location.pathname === "/matches" ? "active" : ""} to="/matches"><Search size={16}/> Matches</Link>
      </nav>
      <div className="top-actions">
        <ThemeButton />
        <span className="user-chip"><CircleUserRound size={16}/>{user?.name || "Account"}</span>
        <button className="logout-btn" onClick={logout} title="Sign out"><LogOut size={16}/></button>
      </div>
    </header>
    <main className="content">{children}</main>
  </div>;
}

function Auth({ setUser }) {
  const nav = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(key, value) { setForm((v) => ({ ...v, [key]: value })); }

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const payload = mode === "register" ? form : { email: form.email, password: form.password };
      const result = mode === "login" ? await api.login(payload) : await api.register(payload);
      localStorage.setItem("lostlink_token", result.access_token);
      const me = await api.me();
      setUser(me);
      nav("/");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  return <div className="auth-page">
    <div className="auth-wrap">
      <div className="auth-side">
        <div className="brand auth-brand"><span className="brandmark">L</span><span>lostlink</span></div>
        <div className="auth-side-copy">
          <p className="kicker">LOST & FOUND WORKSPACE</p>
          <h1>Find the item.<br/><em>Return it home.</em></h1>
          <p>Report a loss, add a clear description, and let LostLink surface the most relevant found reports.</p>
          <div className="trust-row"><ShieldCheck size={17}/><span>Private details stay private.</span></div>
        </div>
      </div>
      <div className="auth-card">
        <div className="auth-card-head">
          <div><p className="kicker">{mode === "login" ? "WELCOME BACK" : "GET STARTED"}</p><h2>{mode === "login" ? "Sign in" : "Create your account"}</h2></div>
          <ThemeButton />
        </div>
        <p className="auth-sub">{mode === "login" ? "Access your reports and recovery matches." : "A simple account is all you need to start reporting."}</p>
        <form onSubmit={submit} className="auth-form">
          {mode === "register" && <label>Name<input autoComplete="name" value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="Your name" minLength={2} required /></label>}
          <label>Email<input autoComplete="email" type="email" value={form.email} onChange={(e) => update("email", e.target.value)} placeholder="you@example.com" required /></label>
          <label>Password<input autoComplete={mode === "login" ? "current-password" : "new-password"} type="password" value={form.password} onChange={(e) => update("password", e.target.value)} placeholder="At least 8 characters" minLength={8} required /></label>
          {error && <div className="error" role="alert"><X size={16}/><span>{error}</span></div>}
          <button className="primary wide" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? <><LogIn size={17}/> Sign in</> : <><UserRound size={17}/> Create account</>}</button>
        </form>
        <button className="switch-auth" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "New here? Create an account" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  </div>;
}

function PageHeader({ eyebrow, title, description, action }) {
  return <section className="page-header">
    <div><p className="kicker">{eyebrow}</p><h1>{title}</h1>{description && <p className="page-desc">{description}</p>}</div>
    {action}
  </section>;
}

function Dashboard() {
  const [reports, setReports] = useState([]);
  const [matches, setMatches] = useState([]);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");
  const load = () => Promise.all([api.reports(), api.matches(), api.health()]).then(([r, m, h]) => { setReports(r); setMatches(m); setHealth(h); }).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);
  return <div>
    <PageHeader eyebrow="OVERVIEW" title="Recovery, without the clutter." description="Keep lost and found reports together, then review the strongest candidate connections." action={<Link className="primary" to="/report"><FilePlus2 size={17}/> New report</Link>} />
    {error && <Notice text={error} onClose={() => setError("")} />}
    <div className="stats">
      <Stat label="Your reports" value={reports.length}/>
      <Stat label="Candidate matches" value={matches.length}/>
      <Stat label="Service" value={health ? "Online" : "Checking"}/>
      <Stat label="Privacy" value="Protected"/>
    </div>
    <div className="dashboard-grid">
      <section className="panel">
        <PanelHead title="Recent reports" link="/report" linkText="Add report" />
        {reports.slice(0, 6).map((r) => <ReportRow key={r.id} r={r}/>)}
        {!reports.length && <Empty title="No reports yet" text="Start with a lost or found report."/>}
      </section>
      <section className="panel">
        <PanelHead title="Candidate matches" link="/matches" linkText="View all" />
        {matches.slice(0, 5).map((m) => <MatchRow key={m.id} m={m}/>)}
        {!matches.length && <Empty title="No matches yet" text="Create a report to start comparing evidence."/>}
      </section>
    </div>
  </div>;
}

function Stat({ label, value }) { return <div className="stat"><span>{label}</span><strong>{value}</strong></div>; }
function PanelHead({ title, link, linkText }) { return <div className="panel-head"><h2>{title}</h2><Link to={link}>{linkText}<ChevronRight size={15}/></Link></div>; }
function ReportRow({ r }) { return <div className="report-row"><div className="thumb">{r.image_url ? <img src={assetUrl(r.image_url)} alt=""/> : <PackageSearch size={19}/>}</div><div className="row-main"><strong>{r.category}</strong><span>{r.description}</span><small><MapPin size={12}/>{r.location_name}</small></div><span className={`status ${r.type}`}>{r.type}</span></div>; }
function MatchRow({ m }) { const pct = Math.round((m.final_score || 0) * 100); return <Link className="candidate-row" to="/matches"><div className="candidate-top"><strong>{pct}%</strong><span>candidate</span></div><div className="meter"><i style={{width: `${pct}%`}}/></div></Link>; }
function Empty({ title, text }) { return <div className="empty"><Search size={20}/><strong>{title}</strong><span>{text}</span></div>; }
function Notice({ text, onClose }) { return <div className="notice"><span>{text}</span><button onClick={onClose}><X size={15}/></button></div>; }

function Report() {
  const nav = useNavigate();
  const [form, setForm] = useState({ type: "lost", category: "", description: "", color: "", location_name: "", latitude: "", longitude: "", event_time: "" });
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  function update(k, v) { setForm((x) => ({ ...x, [k]: v })); }
  async function submit(e) {
    e.preventDefault(); setBusy(true); setError("");
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => { if (v !== "") fd.append(k, v); });
    if (file) fd.append("image", file);
    try { await api.createReport(fd); nav("/matches"); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <div>
    <PageHeader eyebrow="NEW REPORT" title="Tell us what happened." description="A clear photo and a few concrete details give the matching system more useful evidence." />
    <div className="form-layout">
      <aside className="info-panel">
        <div className="info-icon"><ShieldCheck size={20}/></div>
        <h3>Keep ownership private</h3>
        <p>Don't include passwords, financial information, or other secrets. Private verification happens only after a candidate match.</p>
        <div className="steps"><div><b>01</b><span>Describe the item</span></div><div><b>02</b><span>Add context</span></div><div><b>03</b><span>Review candidates</span></div></div>
      </aside>
      <form className="panel report-form" onSubmit={submit}>
        <div className="type-switch"><button type="button" className={form.type === "lost" ? "active" : ""} onClick={() => update("type", "lost")}>I lost it</button><button type="button" className={form.type === "found" ? "active" : ""} onClick={() => update("type", "found")}>I found it</button></div>
        <Field label="Category"><input required value={form.category} onChange={(e) => update("category", e.target.value)} placeholder="e.g. backpack, wallet, phone"/></Field>
        <Field label="Description"><textarea required value={form.description} onChange={(e) => update("description", e.target.value)} placeholder="Brand, color, marks, stickers, scratches, distinctive details…"/></Field>
        <div className="field-grid"><Field label="Color"><input value={form.color} onChange={(e) => update("color", e.target.value)} placeholder="Black, blue…"/></Field><Field label="Location"><input required value={form.location_name} onChange={(e) => update("location_name", e.target.value)} placeholder="Library, cafeteria…"/></Field></div>
        <div className="field-grid"><Field label="Latitude"><input type="number" step="any" value={form.latitude} onChange={(e) => update("latitude", e.target.value)} placeholder="Optional"/></Field><Field label="Longitude"><input type="number" step="any" value={form.longitude} onChange={(e) => update("longitude", e.target.value)} placeholder="Optional"/></Field></div>
        <Field label="When"><input type="datetime-local" value={form.event_time} onChange={(e) => update("event_time", e.target.value)}/></Field>
        <label className="upload-box"><ImagePlus size={20}/><span>{file ? file.name : "Add a photo (optional)"}</span><small>JPEG, PNG or WebP · up to 10 MB</small><input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => setFile(e.target.files?.[0] || null)}/></label>
        {error && <div className="error" role="alert"><X size={16}/><span>{error}</span></div>}
        <button className="primary wide" disabled={busy}>{busy ? "Saving report…" : "Submit report"}<ArrowRight size={17}/></button>
      </form>
    </div>
  </div>;
}
function Field({ label, children }) { return <label className="field"><span>{label}</span>{children}</label>; }

function Matches() {
  const [matches, setMatches] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => { api.matches().then(setMatches).catch((e) => setError(e.message)); }, []);
  async function claim() {
    if (!selected || !detail.trim()) return;
    setBusy(true); setError("");
    try { await api.claim(selected.id, detail.trim()); setDetail(""); alert("Claim submitted for private verification."); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  return <div>
    <PageHeader eyebrow="MATCHES" title="Review candidate connections." description="Scores are evidence to review, not proof of ownership. Confirm a match using private details only." />
    {error && <Notice text={error} onClose={() => setError("")} />}
    {!matches.length ? <div className="panel"><Empty title="No candidate matches" text="Create both lost and found reports to generate candidates."/></div> : <div className="match-grid">{matches.map((m) => <MatchCard key={m.id} m={m} selected={selected?.id === m.id} onClick={() => setSelected(m)}/>)}</div>}
    {selected && <section className="panel verify"><div><p className="kicker">PRIVATE VERIFICATION</p><h2>Know a harmless detail?</h2><p>Use a detail that a genuine owner could provide without exposing passwords, payment details, or sensitive information.</p></div><div><textarea value={detail} onChange={(e) => setDetail(e.target.value)} placeholder="Example: a sticker hidden inside the front pocket…"/><button className="primary" disabled={busy || !detail.trim()} onClick={claim}>{busy ? "Submitting…" : "Submit claim"}</button></div></section>}
  </div>;
}
function MatchCard({ m, selected, onClick }) { const pct = Math.round((m.final_score || 0) * 100); const signals = [["Visual", m.visual_score], ["Text", m.text_score], ["Details", m.attribute_score], ["Place", m.location_score], ["Time", m.time_score]]; return <button className={`match-card ${selected ? "selected" : ""}`} onClick={onClick}><div className="match-score"><strong>{pct}%</strong><span>candidate evidence</span></div><div className="meter"><i style={{width: `${pct}%`}}/></div><div className="signals">{signals.map(([name, value]) => <div key={name}><span>{name}</span><b>{Math.round((value || 0) * 100)}%</b></div>)}</div><div className="reason-list">{(m.explanation?.reasons || []).map((x) => <span key={x}><Check size={13}/>{x}</span>)}</div></button>; }

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!token()) { setLoading(false); return; }
    api.me().then(setUser).catch(() => localStorage.removeItem("lostlink_token")).finally(() => setLoading(false));
  }, []);
  if (loading) return <div className="loader"><span className="brandmark">L</span><b>Loading LostLink</b></div>;
  return user ? <Shell user={user} setUser={setUser}><Routes><Route path="/" element={<Dashboard/>}/><Route path="/report" element={<Report/>}/><Route path="/matches" element={<Matches/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></Shell> : <Routes><Route path="*" element={<Auth setUser={setUser}/>}/></Routes>;
}
