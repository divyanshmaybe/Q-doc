import React from "react";
import { motion } from "framer-motion";
import { Bot, User, Volume2, CheckCircle2, ArrowRight, ShieldCheck, Clock, MapPin, AlertCircle } from "lucide-react";

export interface Message {
  speaker: "agent" | "patient";
  text: string;
  timestamp?: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  slots: Record<string, any>;
  onPlaySpeech?: (text: string) => void;
  confirmationPrompt?: string | null;
  onConfirm?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  slots,
  onPlaySpeech,
  confirmationPrompt,
  onConfirm,
}) => {
  return (
    <div className="w-full flex flex-col gap-4">
      {/* REAL-TIME EXTRACTED CLINICAL SLOTS HUD (Pill-shaped glowing badges) */}
      <div className="w-full glass-panel rounded-xl p-3 border border-white/10 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-electric" />
            <span>EXTRACTED CLINICAL BIOMARKERS</span>
          </div>
          <span className="font-mono text-[9px] text-slate-500">
            TURN {slots.turn_count || messages.filter((m) => m.speaker === "patient").length}
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
          {/* Body Site */}
          <span
            className={`px-2.5 py-1 rounded-lg border transition-all duration-300 flex items-center gap-1.5 ${
              slots.body_site
                ? "bg-electric/15 text-electric-light border-electric/40 shadow-[0_0_12px_rgba(46,137,255,0.25)] font-bold"
                : "bg-white/5 text-slate-500 border-white/5"
            }`}
          >
            <MapPin className="w-3 h-3" />
            SITE: {slots.body_site ? String(slots.body_site).toUpperCase() : "--"}
          </span>

          {/* Duration */}
          <span
            className={`px-2.5 py-1 rounded-lg border transition-all duration-300 flex items-center gap-1.5 ${
              slots.duration_days !== undefined && slots.duration_days !== null
                ? "bg-electric/15 text-electric-light border-electric/40 shadow-[0_0_12px_rgba(46,137,255,0.25)] font-bold"
                : "bg-white/5 text-slate-500 border-white/5"
            }`}
          >
            <Clock className="w-3 h-3" />
            DURATION: {slots.duration_days !== undefined && slots.duration_days !== null ? `${slots.duration_days}D` : "--"}
          </span>

          {/* Itching */}
          <span
            className={`px-2.5 py-1 rounded-lg border transition-all duration-300 ${
              slots.has_itching !== undefined && slots.has_itching !== null
                ? "bg-electric/15 text-electric-light border-electric/40 font-bold"
                : "bg-white/5 text-slate-500 border-white/5"
            }`}
          >
            PRURITUS: {slots.has_itching ? "YES" : slots.has_itching === false ? "NO" : "--"}
          </span>

          {/* Household Contacts (Scabies Indicator) */}
          <span
            className={`px-2.5 py-1 rounded-lg border transition-all duration-300 ${
              slots.household_contacts_affected !== undefined && slots.household_contacts_affected !== null
                ? slots.household_contacts_affected
                  ? "bg-neon/15 text-neon-light border-neon/40 shadow-neon-glow font-bold"
                  : "bg-electric/15 text-electric-light border-electric/40 font-bold"
                : "bg-white/5 text-slate-500 border-white/5"
            }`}
          >
            CONTACTS: {slots.household_contacts_affected ? "AFFECTED" : slots.household_contacts_affected === false ? "CLEAR" : "--"}
          </span>

          {/* Fever (Red Flag Sentinel) */}
          <span
            className={`px-2.5 py-1 rounded-lg border transition-all duration-300 flex items-center gap-1 ${
              slots.has_fever !== undefined && slots.has_fever !== null
                ? slots.has_fever
                  ? "bg-rose-500/25 text-rose-300 border-rose-500/60 shadow-[0_0_15px_rgba(255,51,85,0.4)] font-bold animate-pulse"
                  : "bg-white/5 text-slate-400 border-white/5 font-semibold"
                : "bg-white/5 text-slate-500 border-white/5"
            }`}
          >
            {slots.has_fever && <AlertCircle className="w-3 h-3 text-rose-400" />}
            FEVER: {slots.has_fever ? "POSITIVE" : slots.has_fever === false ? "NEGATIVE" : "--"}
          </span>
        </div>
      </div>

      {/* CHRONOLOGICAL CLINICAL EVENT FEED (Linear Issue History Style) */}
      <div className="flex flex-col gap-2.5 max-h-80 overflow-y-auto pr-1">
        {messages.map((m, idx) => {
          const isAgent = m.speaker === "agent";
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: isAgent ? -6 : 6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              className={`rounded-xl p-3 border transition-all duration-200 ${
                isAgent
                  ? "bg-[#10121A]/80 border-white/10 text-slate-200 mr-4"
                  : "bg-electric/10 border-electric/30 text-white ml-4 shadow-sm"
              }`}
            >
              {/* Event Header */}
              <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-white/5 text-[10px] font-mono">
                <div className="flex items-center gap-1.5">
                  {isAgent ? (
                    <>
                      <div className="w-4 h-4 rounded-full bg-electric/20 text-electric-light flex items-center justify-center">
                        <Bot className="w-2.5 h-2.5" />
                      </div>
                      <span className="font-bold text-electric-light tracking-wide">
                        CLINICAL INTAKE AGENT
                      </span>
                    </>
                  ) : (
                    <>
                      <div className="w-4 h-4 rounded-full bg-neon/20 text-neon-light flex items-center justify-center">
                        <User className="w-2.5 h-2.5" />
                      </div>
                      <span className="font-bold text-slate-300 tracking-wide">
                        PATIENT UTTERANCE
                      </span>
                    </>
                  )}
                </div>

                <div className="flex items-center gap-2 text-slate-500">
                  <span>EVT #{String(idx + 1).padStart(2, "0")}</span>
                  {isAgent && onPlaySpeech && (
                    <button
                      onClick={() => onPlaySpeech(m.text)}
                      className="p-1 hover:text-electric transition rounded"
                      title="Play speech synthesis"
                    >
                      <Volume2 className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>

              {/* Event Body Text */}
              <p className="text-xs leading-relaxed font-sans">{m.text}</p>
            </motion.div>
          );
        })}
      </div>

      {/* INTAKE COMPLETION / PHOTO CONFIRMATION BANNER */}
      {confirmationPrompt && (
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-4 rounded-xl glass-panel-glow border border-electric/40 flex flex-col sm:flex-row items-center justify-between gap-3"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-electric/20 text-electric-light flex items-center justify-center shadow-electric-glow shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <span className="font-mono text-[10px] font-bold text-electric-light tracking-wider uppercase block">
                INTAKE COMPLETE: TRANSITION TO OPTICAL SCAN
              </span>
              <p className="text-xs text-slate-300 font-medium">{confirmationPrompt}</p>
            </div>
          </div>

          {onConfirm && (
            <button
              onClick={onConfirm}
              className="w-full sm:w-auto px-4 py-2 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-electric hover:bg-electric-light text-white shadow-electric-glow transition flex items-center justify-center gap-2 shrink-0 active:scale-95"
            >
              <span>Activate Scanner</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </motion.div>
      )}
    </div>
  );
};
