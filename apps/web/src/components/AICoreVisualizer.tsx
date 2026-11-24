import { DoctorPortrait } from "./DoctorPortrait";
import { Mic, Square } from "lucide-react";

export type AgentPhase = "idle" | "connecting" | "listening" | "thinking" | "speaking" | "error";

const controls: Record<AgentPhase, { status: string; action: string }> = {
  idle: { status: "Microphone off", action: "Start speaking" },
  connecting: { status: "Connecting…", action: "Start speaking" },
  listening: { status: "Listening · microphone on", action: "Finish speaking" },
  thinking: { status: "Preparing a reply…", action: "Start speaking" },
  speaking: { status: "Q-Doc is speaking", action: "Interrupt and speak" },
  error: { status: "Connection interrupted", action: "Try speaking again" },
};

const signal = [0.2, 0.45, 0.3, 0.68, 0.92, 0.55, 1, 0.52, 0.74, 0.36, 0.5, 0.22];

export function AICoreVisualizer({ phase, audioLevel, onTap, disabled = false }: {
  phase: AgentPhase;
  audioLevel: number;
  onTap?: () => void;
  disabled?: boolean;
}) {
  const { status, action } = controls[phase];
  const level = phase === "listening" ? Math.min(1, Math.max(0, audioLevel)) : 0;

  return (
    <div className="voice-console" data-phase={phase}>
      <div className="doctor-voice-scene" aria-hidden="true">
        <DoctorPortrait />
        <div className="voice-signal">
          {signal.map((height, index) => (
            <span key={index} style={{ transform: `scaleY(${height * (0.45 + level * 0.55)})` }} />
          ))}
        </div>
      </div>
      <div className="voice-console-controls">
        <button type="button" onClick={onTap} disabled={disabled}>
          {phase === "listening" ? <Square size={17} /> : <Mic size={17} />}
          {action}
        </button>
        <span role="status">{status}</span>
      </div>
    </div>
  );
}
