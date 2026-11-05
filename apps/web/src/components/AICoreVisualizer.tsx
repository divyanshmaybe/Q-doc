import React, { useMemo } from "react";
import { motion } from "framer-motion";

/**
 * AICoreVisualizer — VapiBlocks-style Orb + LiveKit-style Aura
 *
 * A single, large fluid orb at the center of the screen that reacts to
 * audio levels. State-driven color shifts:
 *   idle       → muted blue pulse
 *   listening  → bright electric blue, amplitude-reactive spikes
 *   thinking   → neon pink slow morph
 *   speaking   → neon pink amplitude-reactive
 *   error      → red pulse
 */

export type AgentPhase =
  | "idle"
  | "connecting"
  | "listening"
  | "thinking"
  | "speaking"
  | "error";

interface AICoreVisualizerProps {
  phase: AgentPhase;
  /** 0-1 normalized audio level (from AnalyserNode) */
  audioLevel: number;
  /** Tap handler (start / stop listening) */
  onTap?: () => void;
  disabled?: boolean;
}

/* ── Color map by phase (aligned with Q-Doc palette: #4361ee teal/electric + #f72585 accent) ── */
const PHASE_COLORS: Record<AgentPhase, { core: string; glow: string; ring: string }> = {
  idle:       { core: "#3a50d9", glow: "rgba(67,97,238,0.18)",  ring: "rgba(67,97,238,0.28)" },
  connecting: { core: "#3a50d9", glow: "rgba(67,97,238,0.22)",  ring: "rgba(67,97,238,0.38)" },
  listening:  { core: "#4361ee", glow: "rgba(67,97,238,0.40)",  ring: "rgba(67,97,238,0.60)" },
  thinking:   { core: "#d4186e", glow: "rgba(247,37,133,0.30)", ring: "rgba(247,37,133,0.50)" },
  speaking:   { core: "#f72585", glow: "rgba(247,37,133,0.40)", ring: "rgba(247,37,133,0.60)" },
  error:      { core: "#ff3355", glow: "rgba(255,51,85,0.30)",  ring: "rgba(255,51,85,0.50)" },
};

/* ── Status labels ── */
const PHASE_LABELS: Record<AgentPhase, string> = {
  idle:       "TAP TO SPEAK",
  connecting: "INITIALIZING...",
  listening:  "LISTENING",
  thinking:   "ANALYZING...",
  speaking:   "RESPONDING",
  error:      "CONNECTION ERROR",
};

export const AICoreVisualizer: React.FC<AICoreVisualizerProps> = ({
  phase,
  audioLevel,
  onTap,
  disabled = false,
}) => {
  const colors = PHASE_COLORS[phase];
  const label  = PHASE_LABELS[phase];

  // Clamp audio to 0-1 and apply easing curve for visual drama
  const level = Math.min(1, Math.max(0, audioLevel));
  const easedLevel = Math.pow(level, 0.7); // gamma < 1 → more responsive to quiet input

  // The orb size oscillates with audio
  const baseSize = 180;
  const orbSize = baseSize + easedLevel * 70; // grows up to +70px on loud input

  // Outer aura ring scale
  const auraScale = 1.0 + easedLevel * 0.35;

  // Generate slightly randomized blob border-radius for organic feel
  const blobRadius = useMemo(() => {
    const r = () => 38 + Math.random() * 24; // 38-62%
    return `${r()}% ${r()}% ${r()}% ${r()}% / ${r()}% ${r()}% ${r()}% ${r()}%`;
  }, [phase]); // re-randomize per phase change

  const isInteractive = phase === "idle" || phase === "listening" || phase === "error";

  return (
    <div className="relative flex flex-col items-center justify-center select-none">
      {/* ── OUTER AURA (LiveKit-style energy field) ── */}
      <motion.div
        animate={{
          scale: phase === "idle" ? [1, 1.06, 1] : auraScale,
          opacity: phase === "idle" ? [0.15, 0.3, 0.15] : 0.25 + easedLevel * 0.45,
        }}
        transition={{
          scale: phase === "idle"
            ? { repeat: Infinity, duration: 4, ease: "easeInOut" }
            : { type: "spring", stiffness: 120, damping: 12 },
          opacity: phase === "idle"
            ? { repeat: Infinity, duration: 4, ease: "easeInOut" }
            : { duration: 0.08 },
        }}
        style={{ borderRadius: blobRadius }}
        className="absolute w-72 h-72 pointer-events-none"
      >
        <div
          className="w-full h-full rounded-[inherit]"
          style={{
            background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
            filter: "blur(40px)",
          }}
        />
      </motion.div>

      {/* ── MIDDLE RING (pulsing orbital) ── */}
      <motion.div
        animate={{
          scale: phase === "idle" ? [1, 1.04, 1] : 0.95 + easedLevel * 0.15,
          rotate: phase === "thinking" ? 360 : 0,
          opacity: 0.35 + easedLevel * 0.4,
        }}
        transition={{
          scale: phase === "idle"
            ? { repeat: Infinity, duration: 5, ease: "easeInOut" }
            : { type: "spring", stiffness: 180, damping: 14 },
          rotate: phase === "thinking"
            ? { repeat: Infinity, duration: 8, ease: "linear" }
            : { duration: 0.4 },
          opacity: { duration: 0.08 },
        }}
        className="absolute w-56 h-56 rounded-full border border-dashed pointer-events-none"
        style={{ borderColor: colors.ring }}
      />

      {/* ── CORE ORB (VapiBlocks-style reactive blob) ── */}
      <motion.button
        onClick={isInteractive ? onTap : undefined}
        whileHover={isInteractive && !disabled ? { scale: 1.04 } : {}}
        whileTap={isInteractive && !disabled ? { scale: 0.93 } : {}}
        animate={{
          width: orbSize,
          height: orbSize,
          borderRadius: blobRadius,
          boxShadow: `0 0 ${30 + easedLevel * 60}px ${8 + easedLevel * 20}px ${colors.glow}`,
        }}
        transition={{
          width:  { type: "spring", stiffness: 200, damping: 18 },
          height: { type: "spring", stiffness: 200, damping: 18 },
          borderRadius: { duration: 1.5, ease: "easeInOut" },
          boxShadow: { duration: 0.08 },
        }}
        disabled={disabled}
        className={`relative z-10 flex items-center justify-center overflow-hidden focus:outline-none ${
          isInteractive && !disabled ? "cursor-pointer" : "cursor-default"
        }`}
        style={{
          background: `radial-gradient(circle at 40% 35%, ${colors.core}ee, ${colors.core}88 50%, ${colors.core}44 100%)`,
        }}
      >
        {/* Inner bright hotspot */}
        <div
          className="absolute w-2/5 h-2/5 rounded-full opacity-60"
          style={{
            background: `radial-gradient(circle, white 0%, transparent 70%)`,
            filter: "blur(18px)",
            top: "22%",
            left: "25%",
          }}
        />

        {/* Audio waveform bars (only when listening/speaking) */}
        {(phase === "listening" || phase === "speaking") && (
          <div className="flex items-center gap-[3px] z-10">
            {Array.from({ length: 7 }).map((_, i) => {
              // Stagger heights for organic waveform
              const barLevel = easedLevel * (0.5 + 0.5 * Math.sin(Date.now() / 200 + i * 1.2));
              const h = 6 + barLevel * 42;
              return (
                <motion.span
                  key={i}
                  animate={{ height: h }}
                  transition={{ duration: 0.06 }}
                  className="w-[3px] rounded-full bg-white/80"
                  style={{ minHeight: 6 }}
                />
              );
            })}
          </div>
        )}

        {/* Thinking spinner */}
        {phase === "thinking" && (
          <div className="w-10 h-10 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        )}

        {/* Connecting pulse */}
        {phase === "connecting" && (
          <div className="w-4 h-4 rounded-full bg-white/60 animate-ping" />
        )}
      </motion.button>

      {/* ── PHASE LABEL ── */}
      <motion.div
        key={phase}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.3 }}
        className="mt-8 flex flex-col items-center gap-1.5"
      >
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              phase === "listening"  ? "bg-electric animate-ping" :
              phase === "thinking"   ? "bg-neon animate-pulse" :
              phase === "speaking"   ? "bg-neon animate-pulse" :
              phase === "error"      ? "bg-red-500 animate-ping" :
              "bg-electric/60 animate-pulse"
            }`}
          />
          <span className="font-mono text-[11px] font-bold tracking-[0.2em] uppercase text-white/70">
            {label}
          </span>
        </div>
      </motion.div>
    </div>
  );
};

