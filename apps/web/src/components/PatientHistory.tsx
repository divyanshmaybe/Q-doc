import { useEffect, useRef, useState } from "react";
import { CareWorkflow } from "./CareWorkflow";

export function PatientHistory({ sessionId, email, onEmail }: { sessionId: string | null; email: string; onEmail: (value: string) => void }) {
  const [input, setInput] = useState(email);
  const [history, setHistory] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const requestVersion = useRef(0);
  useEffect(() => { setInput(email); }, [email]);
  useEffect(() => { requestVersion.current += 1; setHistory(null); setSelected(null); setBusy(false); setError(""); return () => { requestVersion.current += 1; }; }, [sessionId]);
  const post = async (path: string, normalized: string) => {
    const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: normalized }) });
    const data = await res.json();
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Please enter a valid email address.");
    return data;
  };
  return <details className="patient-history-card glass-panel rounded-2xl p-4 w-full max-w-sm text-sm text-white/80">
    <summary className="cursor-pointer font-semibold text-white"><span>Patient history<small>{email || "Keep your visits connected with email"}</small></span></summary>
    <p className="mt-3 text-xs text-white/60">Use the same email for each visit. Every screening stays separate in your timeline.</p>
    <form className="space-y-2 mt-3" onSubmit={async e => {
      e.preventDefault(); setBusy(true); setError(""); setSelected(null);
      const version = ++requestVersion.current;
      const normalized = input.trim().toLowerCase();
      try {
        if (sessionId) await post(`/api/v1/session/${sessionId}/patient`, normalized);
        if (version !== requestVersion.current) return;
        const result = await post("/api/v1/patients/history", normalized);
        if (version !== requestVersion.current) return;
        onEmail(normalized);
        setHistory(result);
      } catch (err) { if (version === requestVersion.current) { setHistory(null); setError(err instanceof Error ? err.message : "Could not load history."); } }
      finally { if (version === requestVersion.current) setBusy(false); }
    }}>
      <label className="block">Patient email<input required type="email" autoComplete="email" value={input} onChange={e => setInput(e.target.value)} className="block mt-1 w-full rounded border border-white/20 bg-black/30 p-2 text-white" /></label>
      <button disabled={busy} className="text-electric-light">{busy ? "Loading…" : "Save email & load history"}</button>
    </form>
    {error && <p role="alert" className="mt-2 text-red-300">{error}</p>}
    {history && <div className="mt-3 space-y-3">
      <p>{history.encounters.length} consultation(s) recorded.</p>
      {history.encounters.map((visit: any) => <article key={visit.session_id} className="border-t border-white/10 pt-3 space-y-1">
        <p className="text-xs text-white/50">{new Date(visit.created_at).toLocaleString()} {visit.session_id === sessionId ? "· current visit" : ""}</p>
        <h4 className="font-semibold">{visit.condition_name || (visit.screening_complete ? "Skin screening" : "History in progress")}</h4>
        {visit.complaint && <p>{visit.complaint}</p>}
        {visit.screening?.patient_spoken_message && <p className="text-xs">{visit.screening.patient_spoken_message}</p>}
        <p className="text-xs text-white/50">{visit.followups.length} follow-up update(s)</p>
        {visit.screening_complete && <button className="text-electric-light" onClick={() => setSelected(selected === visit.session_id ? null : visit.session_id)}>{selected === visit.session_id ? "Close visit" : "Open care & follow-up"}</button>}
        {selected === visit.session_id && <CareWorkflow key={visit.session_id} sessionId={visit.session_id} />}
      </article>)}
    </div>}
  </details>;
}
