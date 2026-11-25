import { useEffect, useState } from "react";
import { careRequest } from "../services/api";
import { CLINICIAN_WORKFLOW_ENABLED } from "../features";

export function CareWorkflow({ sessionId, reviewer = false }: { sessionId: string; reviewer?: boolean }) {
  const [care, setCare] = useState<any>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [key, setKey] = useState("");
  const [form, setForm] = useState({ reviewer_name: "", registration_id: "", diagnosis: "", instructions: "", follow_up: "", return_precautions: "", language: "en-IN" });
  const [draftVersion, setDraftVersion] = useState("");
  const [checks, setChecks] = useState("");
  const [progress, setProgress] = useState("same");
  const [notes, setNotes] = useState("");
  const [urgent, setUrgent] = useState(false);
  const [referral, setReferral] = useState<string>("");
  const refresh = async () => setCare(await careRequest(sessionId));
  useEffect(() => { let live = true; careRequest(sessionId).then(value => { if (live) setCare(value); }).catch(e => { if (live) setError(e.message); }); return () => { live = false; window.speechSynthesis?.cancel(); }; }, [sessionId]);
  const perform = async (action: () => Promise<void>) => {
    setBusy(true); setError(""); setNotice("");
    try { await action(); } catch (e) { setError(e instanceof Error ? e.message : "Request failed"); }
    finally { setBusy(false); }
  };
  const input = "w-full rounded bg-black/30 border border-white/20 p-2 text-sm text-white";
  return <section className="glass-panel rounded-2xl p-4 w-full max-w-sm space-y-3" aria-label="Care plan and follow-up">
    <h3 className="font-bold text-white">Care guidance & follow-up</h3>
    {error && <p role="alert" className="text-red-300 text-sm">{error}</p>}
    {notice && <p role="status" className="text-sm text-white">{notice}</p>}
    <button disabled={busy} onClick={() => perform(refresh)} className="text-sm text-electric-light">Refresh guidance</button>
    {care && <>
      {!CLINICIAN_WORKFLOW_ENABLED && <div className="space-y-2 text-sm text-white/80">
        <p>{care.screening?.needs_update ? "Your symptoms have changed. Update your screening before relying on the earlier guidance." : "Your screening is complete. Explore the supported care information below."}</p>
        {care.screening?.basic_care?.length > 0 && <><h4 className="font-semibold text-white">Basic care</h4>{care.screening.basic_care.map((line: string) => <p key={line}>{line}</p>)}</>}
        {!care.screening?.needs_update && <details><summary>Treatment information and sources</summary>
          <p className="pt-2">{care.draft?.treatment_summary}</p>
          <p className="text-xs text-white/50">General treatment information, not an individualized prescription.</p>
          {(care.draft?.sources || []).map((url: string) => <a key={url} href={url} target="_blank" rel="noreferrer" className="block text-electric-light break-all">{new URL(url).hostname}</a>)}
        </details>}
      </div>}
      {CLINICIAN_WORKFLOW_ENABLED && <p className="text-sm text-white/70">{care.status === "signed" ? "Reviewed plan available" : care.status === "needs_review" ? "New information needs review before this plan can be used." : "Screening recorded. A care plan has not been signed yet."}</p>}
      {care.plan && <div className="space-y-2 text-sm text-white/90">
        <h4 className="font-semibold">{care.plan.diagnosis}</h4>
        <p className="whitespace-pre-wrap">{care.plan.instructions}</p>
        <p>Follow-up: {care.plan.follow_up}</p><p>Seek help if: {care.plan.return_precautions}</p>
        <p className="text-white/50">Reviewed by {care.plan.reviewer_name} · {care.plan.registration_id}</p>
        <button onClick={() => {
          window.speechSynthesis.cancel();
          const speech = new SpeechSynthesisUtterance(`${care.plan.diagnosis}. ${care.plan.instructions}. ${care.plan.follow_up}. ${care.plan.return_precautions}`);
          speech.lang = care.plan.language; window.speechSynthesis.speak(speech);
        }} className="text-electric-light">Listen to the signed plan</button>
      </div>}
      {CLINICIAN_WORKFLOW_ENABLED && reviewer && <details className="text-sm text-white/80"><summary>Reviewer workspace</summary>
        <div className="space-y-2 pt-3">
          <p>Draft reference — review and individualize before signing.</p>
          <p>{care.draft?.display_name}</p><p>{care.draft?.treatment_summary}</p>
          {(care.draft?.basic_care || []).map((line: string) => <p key={line}>{line}</p>)}
          {(care.draft?.sources || []).map((url: string) => <a key={url} href={url} target="_blank" rel="noreferrer" className="block text-electric-light break-all">Reference: {new URL(url).hostname}</a>)}
          <label>Reviewer credential<input type="password" autoComplete="off" className={input} value={key} onChange={e => setKey(e.target.value)} /></label>
          <button disabled={busy || !key || care.screening?.needs_update} className="text-electric-light" onClick={() => perform(async () => {
            const result = await careRequest(sessionId, "/prepare", {}, key);
            const {reasoning_and_checks, ...draft} = result.draft;
            setForm(prev => ({ ...prev, ...draft, language: result.language }));
            setChecks(reasoning_and_checks);
            setDraftVersion(result.evidence_version);
          })}>Open clinical draft for review</button>
          {checks && <p><strong>Clinical reasoning and checks before signing</strong><br />{checks}</p>}
          {([['reviewer_name', 'Reviewer name'], ['registration_id', 'Registration ID'], ['diagnosis', 'Clinical assessment'], ['instructions', 'Patient instructions'], ['follow_up', 'Follow-up timing and action'], ['return_precautions', 'When to seek help']] as const).map(([name, label]) =>
            <label className="block" key={name}>{label}<textarea className={input} value={form[name]} onChange={e => setForm({ ...form, [name]: e.target.value })} /></label>)}
          <label>Plan language<select className={input} value={form.language} onChange={e => setForm({ ...form, language: e.target.value })}><option value="en-IN">English</option><option value="hi-IN">Hindi</option></select></label>
          <button disabled={busy || !key} className="text-electric-light" onClick={() => perform(async () => {
            await careRequest(sessionId, "/sign", { ...form, evidence_version: draftVersion || care.evidence_version }, key);
            setKey(""); await refresh(); setNotice("Plan signed and available to the patient.");
          })}>Sign and release plan</button>
        </div>
      </details>}
      <details className="text-sm text-white/80"><summary>Share a progress update</summary><div className="space-y-2 pt-3">
        <label>How is it now?<select className={input} value={progress} onChange={e => setProgress(e.target.value)}><option value="better">Better</option><option value="same">About the same</option><option value="worse">Worse</option></select></label>
        <label>Changes, treatment response, or questions<textarea className={input} value={notes} onChange={e => setNotes(e.target.value)} /></label>
        <label className="block"><input type="checkbox" checked={urgent} onChange={e => setUrgent(e.target.checked)} /> New urgent symptoms</label>
        {urgent && <p role="alert">Seek urgent medical assessment now. Do not wait for this update to be reviewed.</p>}
        <label className="block">Recommended examination, if any<select className={input} value={referral} onChange={e => setReferral(e.target.value)}><option value="">Not applicable / not answered</option><option value="yes">Completed</option><option value="no">Not yet completed</option></select></label>
        <button disabled={busy} className="text-electric-light" onClick={() => perform(async () => {
          const result = await careRequest(sessionId, "/follow-up", { progress, notes, urgent_symptoms: urgent, referral_completed: referral === "" ? null : referral === "yes" });
          await refresh(); setNotice(result.message); setNotes("");
        })}>Save update</button>
      </div></details>
      {care.followups?.length > 0 && <p className="text-xs text-white/60">{care.followups.length} progress update(s) recorded.</p>}
    </>}
  </section>;
}
