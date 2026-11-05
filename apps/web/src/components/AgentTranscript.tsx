import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Volume2, Mic } from "lucide-react";

/**
 * AgentTranscript — minimal floating transcript overlay.
 * Shows live user speech and agent responses in a clean, floating, glassmorphism card.
 */

interface AgentTranscriptProps {
  /** Most recent agent utterance */
  agentMessage: string | null;
  /** The user's interim speech (live) */
  interimTranscript: string;
  /** The last confirmed user speech received by agent */
  lastUserSpeech?: string | null;
  /** Replay speech */
  onReplay?: (text: string) => void;
}

export const AgentTranscript: React.FC<AgentTranscriptProps> = ({
  agentMessage,
  interimTranscript,
  lastUserSpeech,
  onReplay,
}) => {
  return (
    <div className="w-full max-w-md mx-auto flex flex-col items-center gap-2.5 min-h-[60px] px-2">
      {/* Live Speech Preview (Interim Transcript while speaking) */}
      <AnimatePresence>
        {interimTranscript && (
          <motion.div
            key="interim"
            initial={{ opacity: 0, y: 6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.95 }}
            className="px-4 py-2 rounded-2xl bg-electric/20 border border-electric/50 text-electric-light shadow-electric-glow flex items-center gap-2 max-w-sm text-center"
          >
            <Mic className="w-3.5 h-3.5 animate-pulse text-electric shrink-0" />
            <span className="font-mono text-xs font-semibold leading-snug break-words">
              "{interimTranscript}"
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confirmed What Agent Heard Pill */}
      <AnimatePresence>
        {lastUserSpeech && !interimTranscript && (
          <motion.div
            key={lastUserSpeech}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-300 flex items-center gap-1.5 max-w-sm text-center text-[11px] font-mono"
            title="What Q-Doc heard from you"
          >
            <span className="text-electric-light font-bold">You said:</span>
            <span className="truncate italic">"{lastUserSpeech}"</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Agent Response Card */}
      <AnimatePresence mode="wait">
        {agentMessage && !interimTranscript && (
          <motion.div
            key={agentMessage}
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="glass-panel rounded-2xl px-5 py-4 text-center max-w-md w-full relative group shadow-hud-card"
          >
            <p className="text-sm text-white/90 leading-relaxed font-sans font-medium">
              {agentMessage}
            </p>

            {/* Replay button — appears on hover */}
            {onReplay && (
              <button
                onClick={() => onReplay(agentMessage)}
                className="absolute top-2.5 right-2.5 p-1.5 rounded-lg bg-white/5 hover:bg-white/15 text-white/60 hover:text-white transition flex items-center justify-center opacity-0 group-hover:opacity-100"
                title="Replay Voice Audio"
              >
                <Volume2 className="w-3.5 h-3.5" />
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
