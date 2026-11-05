import React, { useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Volume2, Mic, ChevronDown } from "lucide-react";

/**
 * AgentTranscript — minimal floating transcript overlay.
 * Shows live user speech and agent responses in a clean, scrollable glassmorphism card.
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
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollDown, setCanScrollDown] = useState(false);

  // Check if content exceeds scroll height
  const checkScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    // Show scroll indicator if there's more than 16px of hidden content below
    setCanScrollDown(scrollHeight - (scrollTop + clientHeight) > 16);
  };

  useEffect(() => {
    checkScroll();
    // Scroll to top on new message
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [agentMessage]);

  return (
    <div className="w-full max-w-lg sm:max-w-xl mx-auto flex flex-col items-center gap-2.5 min-h-[60px] px-2 z-10">
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

      {/* Agent Response Card — Scrollable with subtle glass container */}
      <AnimatePresence mode="wait">
        {agentMessage && !interimTranscript && (
          <motion.div
            key={agentMessage}
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="glass-panel rounded-2xl px-5 py-4 w-full relative group shadow-hud-card border border-white/10 overflow-hidden"
          >
            {/* Replay button — pinned top right */}
            {onReplay && (
              <button
                onClick={() => onReplay(agentMessage)}
                className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white/70 hover:text-white transition flex items-center justify-center opacity-80 hover:opacity-100 z-20 backdrop-blur-sm"
                title="Replay Voice Audio"
              >
                <Volume2 className="w-3.5 h-3.5" />
              </button>
            )}

            {/* Scrollable text body */}
            <div
              ref={scrollRef}
              onScroll={checkScroll}
              className="max-h-[190px] sm:max-h-[250px] overflow-y-auto overscroll-contain pr-4 select-text"
            >
              <p className="text-sm text-white/95 leading-relaxed font-sans font-normal text-left whitespace-pre-line">
                {agentMessage}
              </p>
            </div>

            {/* Scroll-down visual indicator pill if text overflows */}
            <AnimatePresence>
              {canScrollDown && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 4 }}
                  onClick={() => {
                    if (scrollRef.current) {
                      scrollRef.current.scrollBy({ top: 90, behavior: "smooth" });
                    }
                  }}
                  className="absolute bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-white/15 hover:bg-white/25 border border-white/20 text-white/80 text-[10px] font-mono tracking-wide cursor-pointer backdrop-blur-md shadow-md transition"
                >
                  <span>Scroll for more</span>
                  <ChevronDown className="w-3 h-3 animate-bounce" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
