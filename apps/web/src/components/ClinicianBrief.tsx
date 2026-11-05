import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Check,
  X,
  AlertOctagon,
  Printer,
  ShieldAlert,
  Sparkles,
  Activity,
  FileText,
  Clock,
  UserCheck,
  CheckCircle2,
  Stethoscope,
  BookOpen,
} from "lucide-react";
import { reviewBrief, ClinicianBriefItem } from "../services/api";

interface ClinicianBriefProps {
  briefData: any;
  onRefresh?: () => void;
}

export const ClinicianBrief: React.FC<ClinicianBriefProps> = ({
  briefData,
  onRefresh,
}) => {
  const [overrideActive, setOverrideActive] = useState(false);
  const [overrideDiag, setOverrideDiag] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [reviewNotice, setReviewNotice] = useState<string | null>(null);

  if (!briefData) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center flex flex-col items-center justify-center gap-3 border border-white/5">
        <Stethoscope className="w-10 h-10 text-slate-600 stroke-[1.5]" />
        <span className="font-mono text-xs uppercase tracking-wider text-slate-400">
          CLINICAL HUD INACTIVE
        </span>
        <p className="text-xs text-slate-500 max-w-sm">
          No active case selected from incoming queue. Select a screening session to review the multimodal telemetry.
        </p>
      </div>
    );
  }

  const data = briefData.brief_data || briefData;
  const triage = data.triage_verdict || {};
  const demo = data.patient_metadata || {};
  const hist = data.history_slots || {};
  const diff: Array<{
    condition: string;
    probability: number;
    clinical_justification: string;
  }> = data.ranked_differential || [];
  const redFlags: string[] = data.detected_red_flags || [];
  const doctorReview = briefData.doctor_review || data.doctor_review;

  const handleApprove = async () => {
    setSubmitting(true);
    setReviewNotice(null);
    try {
      await reviewBrief(data.session_id || briefData.session_id, true, notes);
      setReviewNotice("CASE APPROVED: Triage verdict validated by attending clinician.");
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert("Failed to submit review: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleOverride = async () => {
    if (!overrideDiag.trim()) {
      alert("Please select or enter an overridden primary diagnosis.");
      return;
    }
    setSubmitting(true);
    setReviewNotice(null);
    try {
      await reviewBrief(
        data.session_id || briefData.session_id,
        false,
        `[OVERRIDE: ${overrideDiag.toUpperCase()}] ${notes}`
      );
      setReviewNotice(`CASE OVERRIDDEN: Diagnosis modified to ${overrideDiag.toUpperCase()}`);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert("Failed to record override: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const urgency = triage.urgency || "routine";
  const isEmergency = urgency === "emergency";
  const isSeekOpd = urgency === "seek_opd";

  return (
    <div className="w-full glass-panel rounded-2xl p-5 sm:p-7 flex flex-col gap-6 text-slate-200 border border-white/10 shadow-hud-card relative">
      {/* Background Accent Mesh */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-electric/5 rounded-full blur-3xl pointer-events-none" />

      {/* TOP HUD BAR */}
      <div className="flex flex-wrap justify-between items-start gap-4 border-b border-white/10 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="font-mono text-[10px] font-bold tracking-widest uppercase text-electric-light">
              PALANTIR MEDICAL TELEMETRY HUD // Q-DOC CORE
            </span>
            <span
              className={`px-2.5 py-0.5 rounded font-mono text-[10px] font-black uppercase tracking-wider ${
                isEmergency
                  ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 animate-pulse shadow-neon-glow"
                  : isSeekOpd
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                  : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
              }`}
            >
              TRIAGE: {urgency.toUpperCase()}
            </span>
          </div>

          <h1 className="text-xl font-black text-white tracking-tight mt-1 flex items-center gap-2">
            <span>Session Brief #{String(data.session_id || briefData.session_id).slice(-8)}</span>
          </h1>

          <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 mt-1">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-500" />
              TIMESTAMP: {demo.consultation_timestamp || new Date().toISOString()}
            </span>
            <span>LANG: {demo.primary_language || "en-US"}</span>
          </div>
        </div>

        <button
          onClick={() => window.print()}
          className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 font-mono text-xs flex items-center gap-1.5 transition active:scale-95"
          title="Print official clinical brief"
        >
          <Printer className="w-3.5 h-3.5" />
          <span>Export HUD</span>
        </button>
      </div>

      {/* REVIEW STATUS BANNER */}
      {doctorReview?.reviewed && (
        <div className={`p-3.5 rounded-xl border flex items-center justify-between text-xs font-mono ${
          doctorReview.approved
            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
            : "bg-neon/10 border-neon/30 text-neon-light"
        }`}>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>
              STATUS: {doctorReview.approved ? "CLINICALLY APPROVED" : "OVERRIDDEN BY CLINICIAN"} • {doctorReview.doctor_notes || "No notes appended"}
            </span>
          </div>
          <span className="text-[10px] text-slate-400">{doctorReview.reviewed_at}</span>
        </div>
      )}

      {reviewNotice && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 rounded-xl bg-electric/15 border border-electric/40 text-electric-light font-mono text-xs flex items-center gap-2"
        >
          <Check className="w-4 h-4" />
          <span>{reviewNotice}</span>
        </motion.div>
      )}

      {/* BENTO-BOX GRID LAYOUT */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* TILE 1: TOP DIAGNOSIS & CONFIDENCE (5 cols) */}
        <div className="md:col-span-5 glass-panel rounded-xl p-4 border border-white/10 flex flex-col justify-between relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              PRIMARY HYPOTHESIS
            </span>
            <span className="font-mono text-xs font-black text-electric-light px-2 py-0.5 rounded bg-electric/10 border border-electric/20">
              {((triage.confidence || 0) * 100).toFixed(1)}% POSTERIOR
            </span>
          </div>

          <div className="my-3">
            <h2 className="text-2xl font-black text-white capitalize tracking-tight">
              {String(triage.top_diagnosis || "Undetermined").replace("_", " ")}
            </h2>
            <p className="font-mono text-[11px] text-slate-400 mt-1">
              ACTION: <span className="text-white font-bold">{triage.action || "SPEAK_VERDICT"}</span>
            </p>
          </div>

          {/* Applied Safety Rules */}
          {triage.applied_safety_rules && triage.applied_safety_rules.length > 0 && (
            <div className="pt-2 border-t border-white/5 font-mono text-[10px] text-slate-400 flex flex-wrap gap-1">
              {triage.applied_safety_rules.map((rule: string, i: number) => (
                <span key={i} className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">
                  {rule}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* TILE 2: MULTIMODAL SYNTHESIS & GAIN FROM VOICE HISTORY (7 cols) */}
        <div className="md:col-span-7 glass-panel rounded-xl p-4 border border-white/10 flex flex-col gap-2.5">
          <div className="flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-electric" />
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              CLINICAL SYNTHESIS
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            {data.synthesized_explanation || triage.patient_spoken_message || "Clinical reasoning active."}
          </p>

          {/* Clinical Knowledge Reference (IADVL / AAD Deep Spec) */}
          {data.clinical_reference && (
            <div className="p-3 rounded-lg bg-white/5 border border-white/10 text-xs flex flex-col gap-1.5 mt-1">
              <div className="flex items-center gap-1.5 text-electric-light font-mono text-[10px] uppercase font-bold">
                <BookOpen className="w-3.5 h-3.5" />
                <span>DERMATOLOGY REFERENCE: {data.clinical_reference.name} ({data.clinical_reference.icd10})</span>
              </div>
              <p className="text-[11px] text-slate-300 italic">
                {data.clinical_reference.pathophysiology}
              </p>
              {data.clinical_reference.differentials && data.clinical_reference.differentials.length > 0 && (
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  <span className="font-bold text-slate-300">KEY DIFFERENTIAL CLUES: </span>
                  {data.clinical_reference.differentials.map((d: any, idx: number) => (
                    <span key={idx} className="mr-2">[{d.condition}: {d.clue}]</span>
                  ))}
                </div>
              )}
            </div>
          )}

          {data.gain_from_voice_history && (
            <div className="mt-auto p-2.5 rounded-lg bg-electric/10 border border-electric/30 flex items-start gap-2 shadow-sm">
              <Sparkles className="w-4 h-4 text-electric-light shrink-0 mt-0.5" />
              <div>
                <span className="font-mono text-[10px] font-bold uppercase text-electric-light block">
                  GAIN FROM VOICE HISTORY (BAYESIAN SHIFT)
                </span>
                <span className="text-xs text-slate-200">
                  {data.gain_from_voice_history}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* TILE 3: RANKED DIFFERENTIAL DIAGNOSIS (7 cols) */}
        <div className="md:col-span-7 glass-panel rounded-xl p-4 border border-white/10 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              RANKED DIFFERENTIAL POSTERIORS
            </span>
            <span className="font-mono text-[10px] text-slate-500">CLOSED TAXONOMY (N=8)</span>
          </div>

          <div className="flex flex-col gap-2.5">
            {diff.map((item, idx) => {
              const pct = Math.round(item.probability * 100);
              const isTop = idx === 0;
              return (
                <div key={idx} className="flex flex-col gap-1">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className={`capitalize font-bold ${isTop ? "text-white" : "text-slate-300"}`}>
                      {item.condition.replace("_", " ")}
                    </span>
                    <span className={isTop ? "text-electric-light font-bold" : "text-slate-400"}>
                      {pct}%
                    </span>
                  </div>

                  {/* Sleek Horizontal Progress Bar */}
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.6, ease: "easeOut" }}
                      className={`h-full rounded-full ${
                        isTop
                          ? "bg-gradient-to-r from-blue-600 to-electric shadow-electric-glow"
                          : "bg-slate-600"
                      }`}
                    />
                  </div>

                  {/* Justification citation */}
                  <span className="text-[10px] text-slate-400 italic">
                    {item.clinical_justification}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* TILE 4: CLINICAL RED FLAGS & SAFETY ALERTS (5 cols) */}
        <div className="md:col-span-5 glass-panel rounded-xl p-4 border border-white/10 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-neon" />
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              SAFETY SENTINEL & RED FLAGS
            </span>
          </div>

          {redFlags.length === 0 ? (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-mono flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>ZERO RED FLAGS IDENTIFIED</span>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {redFlags.map((flag, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-rose-500/15 border border-rose-500/40 text-rose-300 flex items-center gap-2 text-xs font-mono shadow-neon-glow animate-pulse"
                >
                  <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />
                  <span className="font-bold uppercase tracking-wider">{flag}</span>
                </div>
              ))}
            </div>
          )}

          {/* Intake Slots Monospace Summary */}
          <div className="mt-auto pt-3 border-t border-white/5 font-mono text-[11px] text-slate-300 grid grid-cols-2 gap-y-1 gap-x-2">
            <div>SITE: <span className="text-white font-bold">{hist.body_site || "--"}</span></div>
            <div>DURATION: <span className="text-white font-bold">{hist.duration_days ? `${hist.duration_days}d` : "--"}</span></div>
            <div>PRURITUS: <span className="text-white font-bold">{hist.has_itching ? "YES" : hist.has_itching === false ? "NO" : "--"}</span></div>
            <div>FEVER: <span className={`font-bold ${hist.has_fever ? "text-rose-400" : "text-white"}`}>{hist.has_fever ? "YES" : "NO"}</span></div>
            <div className="col-span-2">
              CONTACTS: <span className={`font-bold ${hist.household_contacts_affected ? "text-neon-light" : "text-white"}`}>
                {hist.household_contacts_affected ? "AFFECTED (SCABIES VECTOR)" : "NONE"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ATTENDING CLINICIAN TACTILE DECISION ACTIONS (Palantir Action Matrix) */}
      <div className="glass-panel rounded-xl p-4 sm:p-5 border border-white/10 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-electric" />
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-white">
              ATTENDING CLINICIAN GATE
            </span>
          </div>
          <span className="font-mono text-[10px] text-slate-400">
            AUDIT TRAIL LOGGED WITH SHA-256 SIGNATURE
          </span>
        </div>

        {/* Doctor Notes Input */}
        <textarea
          rows={2}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Append clinical telemetry notes or override rationale..."
          className="w-full bg-[#08080C] border border-white/10 rounded-xl p-3 text-xs font-mono text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-electric transition"
        />

        {/* Override Drawer */}
        <AnimatePresence>
          {overrideActive && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="p-3 rounded-xl bg-neon/10 border border-neon/30 flex flex-col gap-2"
            >
              <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-neon-light">
                SELECT OVERRIDE TAXONOMY TARGET:
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  "eczema",
                  "psoriasis",
                  "acne",
                  "urticaria",
                  "tinea",
                  "scabies",
                  "other_unclear",
                  "possible_malignancy",
                ].map((cond) => (
                  <button
                    key={cond}
                    onClick={() => setOverrideDiag(cond)}
                    className={`py-1.5 px-2 rounded-lg font-mono text-[11px] font-bold uppercase border transition ${
                      overrideDiag === cond
                        ? "bg-neon text-white border-neon shadow-neon-glow"
                        : "bg-white/5 text-slate-300 border-white/10 hover:border-white/20"
                    }`}
                  >
                    {cond.replace("_", " ")}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons: Geometric Sharp Tactile */}
        <div className="flex flex-wrap items-center justify-end gap-3 pt-2 border-t border-white/5">
          <button
            onClick={() => setOverrideActive(!overrideActive)}
            disabled={submitting}
            className={`px-4 py-2.5 rounded-xl font-mono text-xs font-bold uppercase tracking-wider border transition-all duration-200 flex items-center gap-1.5 active:scale-95 ${
              overrideActive
                ? "bg-neon/20 text-neon-light border-neon/50 shadow-neon-glow"
                : "bg-white/5 hover:bg-neon/10 text-slate-300 border-white/10 hover:border-neon/30"
            }`}
          >
            <X className="w-3.5 h-3.5" />
            <span>{overrideActive ? "Cancel Override" : "Flag Override"}</span>
          </button>

          {overrideActive ? (
            <button
              onClick={handleOverride}
              disabled={submitting}
              className="px-6 py-2.5 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-pink-600 to-neon hover:from-neon hover:to-pink-500 text-white shadow-neon-glow transition-all duration-200 flex items-center gap-2 active:scale-95"
            >
              <Check className="w-4 h-4" />
              <span>Confirm Override</span>
            </button>
          ) : (
            <button
              onClick={handleApprove}
              disabled={submitting}
              className="px-6 py-2.5 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-blue-600 to-electric hover:from-electric hover:to-blue-400 text-white shadow-electric-glow transition-all duration-200 flex items-center gap-2 active:scale-95"
            >
              <Check className="w-4 h-4" />
              <span>Approve Triage Verdict</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
