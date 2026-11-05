import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff, AlertCircle, RefreshCw, AudioWaveform } from "lucide-react";

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscript,
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [permissionError, setPermissionError] = useState<string | null>(null);
  const [isHovered, setIsHovered] = useState(false);
  const recognitionRef = useRef<any>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // Initialize Speech Recognition once
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setPermissionError("Speech recognition engine not supported in this browser. Please use keyboard input.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsRecording(true);
      setPermissionError(null);
    };

    recognition.onresult = (event: any) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      if (final.trim()) {
        setInterimText("");
        setIsRecording(false);
        onTranscript(final.trim());
      } else if (interim) {
        setInterimText(interim);
      }
    };

    recognition.onerror = (event: any) => {
      console.warn("Speech recognition error:", event.error);
      setIsRecording(false);
      setInterimText("");
      if (event.error === "not-allowed" || event.error === "permission-denied") {
        setPermissionError("Microphone access denied. Grant permissions in browser settings.");
      } else if (event.error === "no-speech") {
        // No speech detected, silently revert
      } else {
        setPermissionError(`Audio capture error (${event.error}). Please retry.`);
      }
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
    };
  }, [onTranscript]);

  const startListening = async () => {
    if (disabled) return;
    setPermissionError(null);

    // Request stream to verify permission and catch explicit denials
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;
      }
    } catch (err: any) {
      setPermissionError("Microphone permission denied. Please allow microphone access to speak.");
      return;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (err) {
        // Recognition might already be running
        console.warn("Speech recognition start warning:", err);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    setIsRecording(false);
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Waveform heights for animated equalizer bars
  const waveHeights = isRecording
    ? [28, 48, 64, 40, 56, 32, 50, 24]
    : [8, 12, 16, 12, 18, 14, 10, 8];

  return (
    <div className="w-full flex flex-col items-center gap-3">
      {/* Microphone Hardware Error Banner */}
      <AnimatePresence>
        {permissionError && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="w-full p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-xs text-rose-300"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span className="font-mono text-[11px]">{permissionError}</span>
            </div>
            <button
              onClick={startListening}
              className="p-1 hover:bg-rose-500/20 rounded text-rose-200 transition"
              title="Retry microphone initialization"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* AI CORE INTERFACE (Framer Motion Fluid Orb) */}
      <div className="relative flex items-center justify-center py-4">
        {/* Outer Orbital Pulse Field (Electric Blue when Idle, Neon Pink when Listening) */}
        <motion.div
          animate={{
            scale: isRecording ? [1, 1.28, 1.05, 1.35, 1] : isHovered ? 1.15 : [1, 1.08, 1],
            opacity: isRecording ? [0.4, 0.85, 0.4] : [0.15, 0.35, 0.15],
            borderColor: isRecording ? "#FF007F" : "#2E89FF",
          }}
          transition={{
            repeat: Infinity,
            duration: isRecording ? 1.6 : 3,
            ease: "easeInOut",
          }}
          className={`absolute w-36 h-36 rounded-full border border-dashed pointer-events-none transition-colors duration-500 ${
            isRecording ? "shadow-neon-glow" : "shadow-electric-glow"
          }`}
        />

        {/* Middle Resonance Ring */}
        <motion.div
          animate={{
            scale: isRecording ? [1.1, 1.22, 1.1] : [1, 1.04, 1],
            rotate: isRecording ? 180 : 0,
            opacity: isRecording ? 0.6 : 0.25,
          }}
          transition={{
            repeat: Infinity,
            duration: isRecording ? 2.2 : 6,
            ease: "linear",
          }}
          className={`absolute w-28 h-28 rounded-full border pointer-events-none ${
            isRecording ? "border-[#FF007F]/40" : "border-[#2E89FF]/30"
          }`}
        />

        {/* Central Tactile AI Core */}
        <motion.button
          onClick={toggleRecording}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.94 }}
          disabled={disabled}
          className={`relative z-10 w-20 h-20 rounded-full flex flex-col items-center justify-center transition-all duration-500 focus:outline-none ${
            isRecording
              ? "bg-gradient-to-tr from-[#FF007F] via-[#FF2A8D] to-[#FF6BAE] text-white shadow-neon-glow"
              : "bg-gradient-to-tr from-[#1468DB] via-[#2E89FF] to-[#68AAFF] text-white shadow-electric-glow"
          } ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
        >
          {/* Animated Core Icons / Waveform */}
          {isRecording ? (
            <div className="flex items-center justify-center gap-1 h-7">
              {waveHeights.map((h, i) => (
                <motion.span
                  key={i}
                  animate={{
                    height: [h * 0.35, h * 0.95, h * 0.45],
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 0.4 + i * 0.08,
                    repeatType: "mirror",
                    ease: "easeInOut",
                  }}
                  className="w-1 bg-white rounded-full"
                  style={{ height: `${h * 0.5}px` }}
                />
              ))}
            </div>
          ) : (
            <Mic className="w-8 h-8 stroke-[2.2] drop-shadow-md" />
          )}
        </motion.button>
      </div>

      {/* Voice Status & Micro-Interaction Label */}
      <div className="flex flex-col items-center gap-1">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              isRecording ? "bg-[#FF007F] animate-ping" : "bg-[#2E89FF] animate-pulse"
            }`}
          />
          <span className="font-mono text-xs font-semibold tracking-wider uppercase text-slate-300">
            {isRecording ? "LISTENING TO INTAKE..." : "AI VOICE INTAKE READY"}
          </span>
        </div>
        <p className="text-[11px] font-mono text-slate-400">
          {isRecording ? "Speak lesion history clearly • Tap to stop" : "Tap Core to Speak"}
        </p>

        {/* Real-time Interim Transcription HUD */}
        {interimText && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-1 px-3 py-1.5 rounded-lg bg-black/60 border border-white/10 text-xs font-mono text-electric-light max-w-sm text-center italic"
          >
            "{interimText}"
          </motion.div>
        )}
      </div>
    </div>
  );
};
