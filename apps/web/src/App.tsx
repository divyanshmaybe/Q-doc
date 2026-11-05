import React, { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Zap,
  UserCheck,
  ClipboardList,
  Camera,
  RotateCcw,
  AlertCircle,
  Sparkles,
  Send,
  CornerDownLeft,
  ArrowLeft,
  Volume2,
} from "lucide-react";

import { AICoreVisualizer, AgentPhase } from "./components/AICoreVisualizer";
import { useVoiceEngine } from "./components/useVoiceEngine";
import { AgentTranscript } from "./components/AgentTranscript";
import { SlotDrawer } from "./components/SlotDrawer";
import { CameraCapture } from "./components/CameraCapture";
import { ClinicianBrief } from "./components/ClinicianBrief";
import { LandingPage } from "./components/LandingPage";

import {
  startSession,
  sendTurn,
  uploadPhoto,
  analyzeSession,
  getAdminMode,
  setAdminMode,
  listAllBriefs,
  ClinicianBriefItem,
} from "./services/api";

const DEFAULT_WELCOME_EN =
  "Hello, I am Q-Doc, your skin screening assistant. Please note: I am a screening aid, not a doctor. What skin issue are you experiencing, and where on your body is it located?";
const DEFAULT_WELCOME_HI =
  "नमस्ते, मैं क्यू-डॉक हूँ, आपका त्वचा स्क्रीनिंग सहायक। कृपया ध्यान दें: यह एक स्क्रीनिंग सहायता है, डॉक्टर नहीं। बताइए, आपकी त्वचा में क्या परेशानी हो रही है और यह किस अंग पर है?";

const b64ToBlobUrl = (base64: string): string => {
  try {
    const cleanB64 = base64.replace(/^data:audio\/\w+;base64,/, "");
    const binary = atob(cleanB64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: "audio/wav" });
    return URL.createObjectURL(blob);
  } catch (err) {
    return "data:audio/wav;base64," + base64;
  }
};

// ─────────────────────────────────────────────
//  App — Voice-First Minimalist Ambient Interface
// ─────────────────────────────────────────────

export const App: React.FC = () => {
  // ── View state ──
  const [view, setView] = useState<"landing" | "voice" | "camera" | "clinician">(() => {
    if (typeof window !== "undefined") {
      if (window.location.hash === "#clinician") return "clinician";
      if (window.location.hash === "#demo" || window.location.hash === "#voice") return "voice";
    }
    return "landing";
  });
  const [mode, setMode] = useState<"autonomous" | "supervised">("autonomous");

  // ── Session state ──
  const [sessionId, setSessionId] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const [sessionLang, setSessionLang] = useState<string>("en-IN");
  const sessionLangRef = useRef<string>("en-IN");

  const [agentMessage, setAgentMessage] = useState<string | null>(DEFAULT_WELCOME_EN);
  const agentMessageRef = useRef<string | null>(DEFAULT_WELCOME_EN);
  const [latestAudioB64, setLatestAudioB64] = useState<string | null>(() => {
    try {
      return localStorage.getItem("qdoc_welcome_b64_en-IN") || null;
    } catch (_) {
      return null;
    }
  });
  const latestAudioB64Ref = useRef<string | null>(latestAudioB64);
  const [autoplayBlocked, setAutoplayBlocked] = useState(false);
  const [lastUserSpeech, setLastUserSpeech] = useState<string | null>(null);
  const [slots, setSlots] = useState<Record<string, any>>({});
  const [photoReady, setPhotoReady] = useState(false);
  const [uploadedPhotoId, setUploadedPhotoId] = useState<string | null>(null);
  const [verdictData, setVerdictData] = useState<any>(null);

  // ── UI state ──
  const [agentPhase, setAgentPhase] = useState<AgentPhase>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [manualText, setManualText] = useState("");

  // ── Clinician portal ──
  const [briefs, setBriefs] = useState<ClinicianBriefItem[]>([]);
  const [selectedBrief, setSelectedBrief] = useState<ClinicianBriefItem | null>(null);

  const activeAudioRef = useRef<HTMLAudioElement | null>(null);
  const voicesRef = useRef<SpeechSynthesisVoice[]>([]);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  useEffect(() => {
    sessionLangRef.current = sessionLang;
  }, [sessionLang]);

  // Pre-load available system speech synthesis voices to prevent empty list race condition
  useEffect(() => {
    if (!("speechSynthesis" in window)) return;
    const updateVoices = () => {
      const v = window.speechSynthesis.getVoices();
      if (v && v.length > 0) {
        voicesRef.current = v;
      }
    };
    updateVoices();
    window.speechSynthesis.onvoiceschanged = updateVoices;
  }, []);

  const getPreferredVoice = (isHi: boolean): SpeechSynthesisVoice | null => {
    if (!("speechSynthesis" in window)) return null;
    const voices = voicesRef.current.length > 0 ? voicesRef.current : window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    if (isHi) {
      const hindi = voices.find((v) => {
        const n = v.name.toLowerCase();
        const l = v.lang.toLowerCase();
        return l.includes("hi") || n.includes("hindi") || n.includes("kalpana") || n.includes("hemant");
      });
      if (hindi) return hindi;
    }

    // Indian English Male voice matching (Rohan / Ravi priority)
    // 1. Explicit search for "Rohan"
    const rohan = voices.find((v) => v.name.toLowerCase().includes("rohan"));
    if (rohan) return rohan;

    // 2. Microsoft Ravi (English India, natural male clinician)
    const ravi = voices.find((v) => v.name.toLowerCase().includes("ravi"));
    if (ravi) return ravi;

    // 3. Any Indian male voice
    const indianMale = voices.find((v) => {
      const n = v.name.toLowerCase();
      const l = v.lang.toLowerCase();
      return (l.includes("in") || n.includes("india")) && (n.includes("male") || n.includes("prabhat") || n.includes("madhav"));
    });
    if (indianMale) return indianMale;

    // 4. Any Indian English voice (e.g. Google English India, Heera, etc.)
    const indianGeneral = voices.find((v) => {
      const n = v.name.toLowerCase();
      const l = v.lang.toLowerCase().replace("_", "-");
      return l.includes("en-in") || n.includes("india") || n.includes("heera") || n.includes("veena");
    });
    if (indianGeneral) return indianGeneral;

    return null;
  };

  // ── Speech Playback (Sarvam base64 audio priority + WebSpeech fallback) ──
  const playSpeech = (text: string, audioB64?: string | null) => {
    // 1. Stop any previously playing audio or speech
    if (activeAudioRef.current) {
      try {
        activeAudioRef.current.pause();
        activeAudioRef.current.currentTime = 0;
      } catch (_) {}
      activeAudioRef.current = null;
    }
    if ("speechSynthesis" in window) {
      try {
        (window as any).__currentUtterance = null;
        window.speechSynthesis.cancel();
      } catch (_) {}
    }

    setAgentPhase("speaking");

    // 2. Play Sarvam synthesized audio if present
    const b64 = audioB64 || latestAudioB64Ref.current;
    if (b64) {
      try {
        const audioUrl = b64ToBlobUrl(b64);
        const audio = new Audio(audioUrl);
        activeAudioRef.current = audio;
        audio.onended = () => {
          setAgentPhase("idle");
          setAutoplayBlocked(false);
        };
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setAutoplayBlocked(false);
            })
            .catch((err) => {
              console.warn("[App] Audio play error / autoplay blocked:", err);
              if (err.name === "NotAllowedError") {
                setAutoplayBlocked(true);
              }
              if (err.name !== "AbortError") {
                speakSynthesisFallback(text);
              }
            });
        }
        return;
      } catch (err) {
        console.warn("[App] Error creating Audio object:", err);
      }
    }

    // 3. Fallback to browser SpeechSynthesis only if no audioB64 provided
    speakSynthesisFallback(text);
  };

  const speakSynthesisFallback = (text: string) => {
    if (!("speechSynthesis" in window)) return;
    try {
      (window as any).__currentUtterance = null;
      window.speechSynthesis.cancel();

      // Split long paragraph into natural sentences to prevent Chromium 15s freeze
      const rawSentences = text.match(/[^.!?\n।]+[.!?\n।]+|[^.!?\n।]+/g) || [text];
      const sentences = rawSentences.map((s) => s.trim()).filter(Boolean);
      if (sentences.length === 0) return;

      let currentIndex = 0;
      const activeLang = sessionLangRef.current || sessionLang;
      const isHi = activeLang.toLowerCase().includes("hi");
      const matchedVoice = getPreferredVoice(isHi);

      const speakNextChunk = () => {
        if (currentIndex >= sentences.length) {
          (window as any).__currentUtterance = null;
          return;
        }

        const chunkText = sentences[currentIndex];
        const u = new SpeechSynthesisUtterance(chunkText);
        u.lang = matchedVoice ? matchedVoice.lang : (isHi ? "hi-IN" : "en-IN");
        u.rate = 0.98;
        u.pitch = 0.95;
        if (matchedVoice) {
          u.voice = matchedVoice;
        }

        // Retain reference on window to prevent Chrome garbage collector from killing it mid-speech
        (window as any).__currentUtterance = u;

        u.onend = () => {
          currentIndex++;
          speakNextChunk();
        };

        u.onerror = (e) => {
          console.warn("[SpeechSynthesis] Chunk error, advancing:", e);
          currentIndex++;
          speakNextChunk();
        };

        window.speechSynthesis.speak(u);
      };

      speakNextChunk();
    } catch (err) {
      console.warn("[SpeechSynthesis] Error:", err);
    }
  };

  // ── Turn Handler (Used by both Voice Engine and Manual Input) ──
  const handleFinalTranscript = useCallback(
    async (text: string, audioBase64?: string) => {
      const trimmed = text.trim();
      if (!trimmed && !audioBase64) return;

      const currentLang = sessionLangRef.current || sessionLang;
      let activeSessionId = sessionIdRef.current || sessionId;
      if (!activeSessionId) {
        console.warn("[App] Initializing session first...");
        try {
          const res = await startSession(currentLang, mode);
          activeSessionId = res.session_id;
          setSessionId(activeSessionId);
          sessionIdRef.current = activeSessionId;
          if (res.language) setSessionLang(res.language);
        } catch (e: any) {
          setErrorMsg("Could not connect to session. Ensure backend server is running.");
          setAgentPhase("error");
          return;
        }
      }

      console.log("[App] Sending intake turn -> text:", trimmed, "lang:", currentLang, "audio attached:", !!audioBase64);
      setLastUserSpeech(trimmed);
      setErrorMsg(null);
      setAgentPhase("thinking");
      setAgentMessage(currentLang.startsWith("hi") ? "लक्षणों का विश्लेषण हो रहा है..." : "Analyzing symptoms...");

      try {
        const res = await sendTurn(activeSessionId, trimmed, currentLang, audioBase64);
        setSlots(res.slots || {});

        // Automatically update session language if language switch detected
        if (res.language && res.language !== currentLang) {
          console.log("[App] Dynamic language switch detected ->", res.language);
          setSessionLang(res.language);
          sessionLangRef.current = res.language;
        }

        setAgentPhase("speaking");
        setAgentMessage(res.agent_response);
        agentMessageRef.current = res.agent_response;
        setLatestAudioB64(res.audio?.audio_base64 || null);
        latestAudioB64Ref.current = res.audio?.audio_base64 || null;
        playSpeech(res.agent_response, res.audio?.audio_base64);

        if (res.verdict_data) {
          setVerdictData(res.verdict_data);
        }

        if (res.is_ready_for_photo || res.confirmation_prompt) {
          setPhotoReady(true);
        }

        setTimeout(() => setAgentPhase("idle"), 3500);
      } catch (err: any) {
        console.error("[App] Turn error:", err);
        setErrorMsg(err.message || "Turn submission failed.");
        setAgentPhase("error");
        setTimeout(() => setAgentPhase("idle"), 3000);
      }
    },
    [sessionId, mode, sessionLang]
  );

  const voice = useVoiceEngine({ onFinalTranscript: handleFinalTranscript, language: sessionLang });

  // Sync voice engine state → agentPhase
  useEffect(() => {
    if (voice.isListening && agentPhase !== "thinking" && agentPhase !== "speaking") {
      setAgentPhase("listening");
    }
  }, [voice.isListening, agentPhase]);

  // ── Speech Controller helpers ──
  const stopSpeech = () => {
    if (activeAudioRef.current) {
      try {
        activeAudioRef.current.pause();
        activeAudioRef.current.currentTime = 0;
      } catch (_) {}
      activeAudioRef.current = null;
    }
    if ("speechSynthesis" in window) {
      try {
        (window as any).__currentUtterance = null;
        window.speechSynthesis.cancel();
      } catch (_) {}
    }
    setAgentPhase("idle");
  };

  // ── Init (prevent double firing in React StrictMode) ──
  const initializedRef = useRef(false);
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;
    initApp();
  }, []);

  const initApp = async () => {
    try {
      const modeData = await getAdminMode();
      if (modeData?.mode) setMode(modeData.mode);
    } catch (_) {}

    // Check if this navigation was a page reload (F5 / Refresh)
    const isReload = typeof window !== "undefined" && (
      (window.performance?.getEntriesByType?.('navigation')?.[0] as any)?.type === 'reload' ||
      (window.performance as any)?.navigation?.type === 1
    );

    // If reload: NEVER auto-speak!
    // If directly arriving via #demo link (e.g. from visiting page): speak!
    const isDirectDemoLaunch = !isReload && typeof window !== "undefined" && window.location.hash.includes("demo");
    await handleNewSession(undefined, isDirectDemoLaunch);
  };

  const handleNewSession = async (langOverride?: string, shouldSpeak: boolean = false) => {
    stopSpeech();
    setErrorMsg(null);
    setSlots({});
    setPhotoReady(false);
    setUploadedPhotoId(null);
    setVerdictData(null);

    const targetLang = langOverride || sessionLangRef.current || sessionLang;
    const defaultMsg = targetLang.toLowerCase().includes("hi") ? DEFAULT_WELCOME_HI : DEFAULT_WELCOME_EN;
    setAgentMessage(defaultMsg);
    agentMessageRef.current = defaultMsg;

    // Load cached audio from localStorage if available
    try {
      const cachedB64 = localStorage.getItem("qdoc_welcome_b64_" + targetLang);
      if (cachedB64) {
        setLatestAudioB64(cachedB64);
        latestAudioB64Ref.current = cachedB64;
      }
    } catch (_) {}

    setAgentPhase(shouldSpeak ? "connecting" : "idle");

    try {
      const res = await startSession(targetLang, mode);
      setSessionId(res.session_id);
      sessionIdRef.current = res.session_id;
      if (res.language) {
        setSessionLang(res.language);
        sessionLangRef.current = res.language;
      }
      setSlots(res.slots || {});
      setAgentMessage(res.agent_message);
      agentMessageRef.current = res.agent_message;
      setLatestAudioB64(res.audio?.audio_base64 || null);
      latestAudioB64Ref.current = res.audio?.audio_base64 || null;

      // Save to localStorage for instant subsequent launches
      if (res.audio?.audio_base64) {
        try {
          localStorage.setItem("qdoc_welcome_b64_" + (res.language || targetLang), res.audio.audio_base64);
        } catch (_) {}
      }

      if (shouldSpeak) {
        playSpeech(res.agent_message, res.audio?.audio_base64);
      } else {
        setAgentPhase("idle");
      }
    } catch (err: any) {
      console.error("[App] Session initialization failed:", err);
      setErrorMsg(err.message || "Failed to start session. Ensure server is online.");
      setAgentPhase("error");
    }
  };

  // ── Explicit launch handler from visiting page ──
  const handleLaunchDemo = () => {
    setView("voice");
    if (typeof window !== "undefined") window.location.hash = "#demo";

    const targetLang = sessionLangRef.current || sessionLang;
    const defaultMsg = targetLang.toLowerCase().includes("hi") ? DEFAULT_WELCOME_HI : DEFAULT_WELCOME_EN;
    const msg = agentMessageRef.current || agentMessage || defaultMsg;
    const b64 = latestAudioB64Ref.current || latestAudioB64;

    // Direct synchronous speech launch inside the user's click gesture
    playSpeech(msg, b64);

    // If session is still initializing or missing, ensure it starts in parallel
    if (!sessionIdRef.current) {
      handleNewSession(undefined, false);
    }
  };

  const handleReturnHome = () => {
    stopSpeech();
    setView("landing");
    if (typeof window !== "undefined") window.location.hash = "";
  };

  const handleModeToggle = async (m: "autonomous" | "supervised") => {
    setMode(m);
    try { await setAdminMode(m); } catch (_) {}
  };

  // ── Photo flow ──
  const handlePhotoCapture = async (file: File) => {
    const activeSessionId = sessionIdRef.current || sessionId;
    if (!activeSessionId) return;

    setErrorMsg(null);
    setAgentPhase("thinking");
    setView("voice");
    setAgentMessage("Inspecting lesion image morphology...");

    try {
      const photoRes = await uploadPhoto(activeSessionId, file);
      if (!photoRes.quality_passed) {
        setAgentMessage(photoRes.message);
        setAgentPhase("speaking");
        playSpeech(photoRes.message);
        setTimeout(() => setAgentPhase("idle"), 2500);
        return;
      }

      setUploadedPhotoId(photoRes.image_id);
      if (photoRes.slots) setSlots(photoRes.slots);

      // If early photo intake delivered condition-specific question, continue dialogue
      if (photoRes.agent_question) {
        const nextMsg = photoRes.agent_question;
        setAgentMessage(nextMsg);
        agentMessageRef.current = nextMsg;
        setLatestAudioB64(photoRes.audio?.audio_base64 || null);
        latestAudioB64Ref.current = photoRes.audio?.audio_base64 || null;
        playSpeech(nextMsg, photoRes.audio?.audio_base64);
        setPhotoReady(false);
      } else {
        // Fallback or immediate analysis
        setAgentMessage("Computing differential diagnosis & Bayesian posteriors...");
        const analysisRes = await analyzeSession(activeSessionId, photoRes.image_id);
        setVerdictData(analysisRes);
        const msg = analysisRes.policy_decision.spoken_patient_message;
        setAgentMessage(msg);
        agentMessageRef.current = msg;
        setLatestAudioB64(analysisRes.audio?.audio_base64 || null);
        latestAudioB64Ref.current = analysisRes.audio?.audio_base64 || null;
        playSpeech(msg, analysisRes.audio?.audio_base64);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Analysis failed.");
      setAgentPhase("error");
      setTimeout(() => setAgentPhase("idle"), 3000);
    }
  };

  const handleRunFinalAnalysis = async () => {
    const activeSessionId = sessionIdRef.current || sessionId;
    const targetImageId = uploadedPhotoId;
    if (!activeSessionId || !targetImageId) return;

    setErrorMsg(null);
    setAgentPhase("thinking");
    setAgentMessage("Computing differential diagnosis & Bayesian posteriors...");

    try {
      const analysisRes = await analyzeSession(activeSessionId, targetImageId);
      setVerdictData(analysisRes);

      const msg = analysisRes.policy_decision.spoken_patient_message;
      setAgentMessage(msg);
      setLatestAudioB64(analysisRes.audio?.audio_base64 || null);
      setAgentPhase("speaking");
      playSpeech(msg, analysisRes.audio?.audio_base64);
      setTimeout(() => setAgentPhase("idle"), 4000);
    } catch (err: any) {
      setErrorMsg(err.message || "Analysis failed.");
      setAgentPhase("error");
      setTimeout(() => setAgentPhase("idle"), 3000);
    }
  };

  const loadBriefs = async () => {
    try {
      const list = await listAllBriefs();
      setBriefs(list);
      if (list.length > 0 && !selectedBrief) setSelectedBrief(list[0]);
    } catch (_) {}
  };

  // ── Orb tap handler ──
  const handleOrbTap = () => {
    if (autoplayBlocked) {
      setAutoplayBlocked(false);
      const msg = agentMessageRef.current || agentMessage;
      const b64 = latestAudioB64Ref.current || latestAudioB64;
      if (msg) playSpeech(msg, b64);
      return;
    }
    if (agentPhase === "idle" || agentPhase === "error") {
      voice.startListening();
    } else if (agentPhase === "listening") {
      voice.stopListening();
    }
  };

  // ── Manual Input Submit ──
  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualText.trim() || agentPhase === "thinking") return;
    const text = manualText.trim();
    setManualText("");
    handleFinalTranscript(text);
  };

  // ──────────────────────────────────────────────
  //  RENDER
  // ──────────────────────────────────────────────

  if (view === "landing") {
    return (
      <LandingPage
        onLaunchDemo={handleLaunchDemo}
        onOpenClinician={() => {
          setView("clinician");
          loadBriefs();
          if (typeof window !== "undefined") window.location.hash = "#clinician";
        }}
      />
    );
  }

  return (
    <div className={`min-h-screen ${view === "clinician" ? "h-auto min-h-screen overflow-y-auto" : "h-screen overflow-hidden"} flex flex-col bg-[#0a0a0a] text-[#eaeaea] relative selection:bg-[#f72585] selection:text-white`}>
      {/* Ambient background aura */}
      <div className="orb-ambient-bg" />

      {/* ── TOP BAR (ultra-minimal) ── */}
      <header className="relative z-20 px-4 sm:px-6 py-3 flex items-center justify-between shrink-0 border-b border-[#1f1f1f] bg-[#0a0a0a]/90 backdrop-blur-md">
        {/* Brand + Return to Landing */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleReturnHome}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md font-sans text-xs font-semibold text-[#888888] hover:text-[#eaeaea] bg-[#111111] border border-[#1f1f1f] hover:border-[#333333] transition"
            title="Return to Q-Doc Visiting Page"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Home</span>
          </button>

          <div
            className="flex items-center gap-2.5 cursor-pointer"
            onClick={handleReturnHome}
          >
            <svg className="w-7 h-7 shrink-0" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="17" cy="17" r="15.5" stroke="#4361ee" strokeWidth="2" />
              <rect x="15.25" y="8.5" width="3.5" height="17" rx="1.75" fill="#f72585" />
              <rect x="8.5" y="15.25" width="17" height="3.5" rx="1.75" fill="#f72585" />
            </svg>
            <span className="font-head text-base font-bold tracking-tight text-[#eaeaea]">
              Q-Doc
            </span>
          </div>
        </div>

        {/* Mode toggle + nav */}
        <div className="flex items-center gap-2">
          {/* Autonomy switch */}
          <div className="flex items-center bg-white/5 border border-white/10 rounded-full p-0.5 font-mono text-[10px]">
            <button
              onClick={() => handleModeToggle("autonomous")}
              className={`px-2.5 py-1 rounded-full font-bold transition-all ${
                mode === "autonomous"
                  ? "bg-electric text-white shadow-electric-glow"
                  : "text-white/40 hover:text-white/70"
              }`}
            >
              <Zap className="w-3 h-3 inline -mt-0.5 mr-0.5" /> AUTO
            </button>
            <button
              onClick={() => handleModeToggle("supervised")}
              className={`px-2.5 py-1 rounded-full font-bold transition-all ${
                mode === "supervised"
                  ? "bg-amber-500 text-black"
                  : "text-white/40 hover:text-white/70"
              }`}
            >
              <UserCheck className="w-3 h-3 inline -mt-0.5 mr-0.5" /> SUP
            </button>
          </div>

          {/* Multilingual auto-switch indicator / toggle */}
          <button
            onClick={() => {
              const next = sessionLang.startsWith("hi") ? "en-IN" : "hi-IN";
              setSessionLang(next);
              sessionLangRef.current = next;
              handleNewSession(next, true);
            }}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 font-mono text-[10px] text-white/70 hover:text-white transition"
            title="Auto-switches language when you speak Hindi or English. Tap to switch."
          >
            <span className="text-[11px]">🇮🇳</span>
            <span className="font-semibold tracking-wide">
              {sessionLang.startsWith("hi") ? "हिंदी (Auto)" : "EN (Auto)"}
            </span>
          </button>

          {/* Clinician Portal */}
          <button
            onClick={() => {
              if (view === "clinician") {
                setView("voice");
              } else {
                setView("clinician");
                loadBriefs();
              }
            }}
            className={`p-2 rounded-full transition ${
              view === "clinician"
                ? "bg-electric/20 text-electric-light"
                : "bg-white/5 text-white/50 hover:text-white/80"
            }`}
            title="Doctor Portal"
          >
            <ClipboardList className="w-4 h-4" />
          </button>

          {/* Reset */}
          <button
            onClick={() => handleNewSession(undefined, true)}
            className="p-2 rounded-full bg-white/5 text-white/50 hover:text-white/80 transition"
            title="New Session"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* ── ERROR BANNER ── */}
      <AnimatePresence>
        {(errorMsg || voice.permissionError) && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="relative z-20 mx-4 sm:mx-auto max-w-md mb-2"
          >
            <div className="glass-panel-danger rounded-xl p-2.5 flex items-center gap-2 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span className="font-mono text-[11px]">{errorMsg || voice.permissionError}</span>
              <button
                onClick={() => { setErrorMsg(null); }}
                className="ml-auto text-rose-400/60 hover:text-rose-300 text-[10px] font-bold"
              >
                ×
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── MAIN CONTENT ── */}
      <main className={`relative z-10 flex-1 flex flex-col items-center ${view === "clinician" ? "justify-start w-full min-h-0 overflow-y-auto py-4" : "justify-center"} px-4`}>
        <AnimatePresence mode="wait">
          {/* ════════════════════════════════════════════ */}
          {/*  VOICE VIEW — Ambient AI Core               */}
          {/* ════════════════════════════════════════════ */}
          {view === "voice" && (
            <motion.div
              key="voice"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="flex flex-col items-center justify-center gap-6 w-full"
            >
              {/* THE ORB */}
              <AICoreVisualizer
                phase={agentPhase}
                audioLevel={voice.audioLevel}
                onTap={handleOrbTap}
                disabled={agentPhase === "thinking" || agentPhase === "connecting"}
              />

              {/* Autoplay unlock prompt (if browser blocked sound) */}
              <AnimatePresence>
                {autoplayBlocked && (
                  <motion.button
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    onClick={() => {
                      setAutoplayBlocked(false);
                      const msg = agentMessageRef.current || agentMessage;
                      const b64 = latestAudioB64Ref.current || latestAudioB64;
                      if (msg) playSpeech(msg, b64);
                    }}
                    className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#f72585] text-white text-xs font-semibold shadow-[0_2px_14px_rgba(247,37,133,0.4)] hover:bg-[#d4186e] transition animate-pulse cursor-pointer -mt-2 z-20"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                    <span>Click here to enable voice greeting</span>
                  </motion.button>
                )}
              </AnimatePresence>

              {/* AGENT TRANSCRIPT (floating below orb) */}
              <AgentTranscript
                agentMessage={agentMessage}
                interimTranscript={voice.interimTranscript}
                lastUserSpeech={lastUserSpeech}
                onReplay={() => agentMessage && playSpeech(agentMessage, latestAudioB64)}
              />

              {/* VERDICT CARD (appears after analysis) */}
              <AnimatePresence>
                {verdictData && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 16 }}
                    className="glass-panel-glow rounded-2xl p-4 max-w-sm w-full flex flex-col gap-2"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-mono text-[9px] font-bold text-electric-light uppercase tracking-wider">
                          SCREENING RESULT
                        </span>
                        <h3 className="text-base font-black text-white capitalize">
                          {String(verdictData.reasoner_output.top_diagnosis).replace("_", " ")}
                        </h3>
                      </div>
                      <span className="px-2 py-0.5 rounded-full font-mono text-[10px] font-bold bg-electric/20 text-electric-light border border-electric/30">
                        {(verdictData.reasoner_output.final_confidence * 100).toFixed(0)}%
                      </span>
                    </div>

                    {verdictData.reasoner_output.gain_from_voice_history && (
                      <div className="flex items-center gap-2 text-[11px] text-electric-light bg-electric/10 rounded-lg px-3 py-1.5 border border-electric/20">
                        <Sparkles className="w-3.5 h-3.5 shrink-0" />
                        <span>{verdictData.reasoner_output.gain_from_voice_history}</span>
                      </div>
                    )}

                    {verdictData.doctor_brief_id && (
                      <button
                        onClick={() => { setView("clinician"); loadBriefs(); }}
                        className="text-[10px] font-mono text-white/50 hover:text-electric-light transition text-center pt-1"
                      >
                        View Clinician Brief →
                      </button>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* PHOTO TRIGGER & ATTACHED STATUS */}
              <AnimatePresence>
                {photoReady && !uploadedPhotoId && !verdictData && (
                  <motion.button
                    initial={{ opacity: 0, y: 12, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 12, scale: 0.95 }}
                    onClick={() => setView("camera")}
                    className="glass-panel rounded-full px-5 py-2.5 font-mono text-xs font-bold text-white/90 hover:text-white flex items-center gap-2 transition hover:border-electric/50 active:scale-95 shadow-electric-glow animate-pulse"
                  >
                    <Camera className="w-4 h-4 text-electric" />
                    <span>Take Lesion Photo (Early Intake)</span>
                  </motion.button>
                )}

                {uploadedPhotoId && !verdictData && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3"
                  >
                    <div className="glass-panel rounded-full px-4 py-2 font-mono text-[11px] text-emerald-400 flex items-center gap-2 border border-emerald-500/30">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                      <span>Lesion Photo Analyzed & In Context</span>
                    </div>
                    <button
                      onClick={handleRunFinalAnalysis}
                      className="glass-panel rounded-full px-4 py-2 font-mono text-[11px] text-electric-light hover:text-white flex items-center gap-1.5 border border-electric/30 hover:border-electric/70 transition shadow-electric-glow"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Finalize Clinical Report →</span>
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* ════════════════════════════════════════════ */}
          {/*  CAMERA VIEW                                */}
          {/* ════════════════════════════════════════════ */}
          {view === "camera" && (
            <motion.div
              key="camera"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="w-full max-w-md flex flex-col gap-4"
            >
              <button
                onClick={() => setView("voice")}
                className="self-start font-mono text-[11px] text-white/50 hover:text-white/80 flex items-center gap-1 transition"
              >
                ← Back to Voice
              </button>
              <CameraCapture
                onCapture={handlePhotoCapture}
                qualityPassed={verdictData?.image_prediction?.quality_passed}
                isProcessing={agentPhase === "thinking"}
              />
            </motion.div>
          )}

          {/* ════════════════════════════════════════════ */}
          {/*  CLINICIAN PORTAL                           */}
          {/* ════════════════════════════════════════════ */}
          {view === "clinician" && (
            <motion.div
              key="clinician"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="w-full max-w-6xl flex flex-col gap-4 pb-20"
            >
              <button
                onClick={() => setView("voice")}
                className="self-start font-mono text-[11px] text-white/50 hover:text-white/80 flex items-center gap-1 transition"
              >
                ← Back to Voice
              </button>

              <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                {/* Queue */}
                <div className="md:col-span-4 glass-panel rounded-2xl p-4 border border-white/10 flex flex-col gap-3 max-h-[700px] overflow-y-auto">
                  <div className="flex items-center justify-between pb-2 border-b border-white/10">
                    <span className="font-mono text-xs font-bold text-slate-300 uppercase tracking-wider">
                      QUEUE
                    </span>
                    <span className="font-mono text-[10px] text-electric-light bg-electric/15 px-2 py-0.5 rounded border border-electric/30">
                      {briefs.length}
                    </span>
                  </div>
                  {briefs.length === 0 ? (
                    <p className="text-xs text-white/30 font-mono text-center py-8">
                      No cases yet.
                    </p>
                  ) : (
                    briefs.map((b) => {
                      const t = b.brief_data?.triage_verdict || ({} as any);
                      return (
                        <div
                          key={b.id}
                          onClick={() => setSelectedBrief(b)}
                          className={`p-3 rounded-xl border cursor-pointer transition ${
                            selectedBrief?.id === b.id
                              ? "glass-panel-glow border-electric"
                              : "bg-white/5 border-white/10 hover:border-white/20"
                          }`}
                        >
                          <div className="flex justify-between text-[10px] font-mono text-white/50">
                            <span>#{String(b.session_id).slice(-6)}</span>
                            <span
                              className={`font-bold uppercase ${
                                t.urgency === "emergency"
                                  ? "text-rose-400"
                                  : t.urgency === "seek_opd"
                                  ? "text-amber-400"
                                  : "text-emerald-400"
                              }`}
                            >
                              {t.urgency || "ROUTINE"}
                            </span>
                          </div>
                          <h4 className="text-xs font-bold text-white capitalize mt-1 font-mono">
                            {String(t.top_diagnosis || "Pending").replace("_", " ")}
                          </h4>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* Brief HUD */}
                <div className="md:col-span-8">
                  <ClinicianBrief briefData={selectedBrief} onRefresh={loadBriefs} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ── BOTTOM DRAWER & INTUITIVE INPUT FALLBACK ── */}
      {view === "voice" && (
        <div className="relative z-20 pb-5 px-4 flex flex-col items-center gap-3 max-w-md mx-auto w-full shrink-0">
          {/* Biomarker Pills Drawer */}
          <SlotDrawer slots={slots} visible={Object.keys(slots).length > 0} />

          {/* Minimalist Instant Text Input */}
          <form
            onSubmit={handleManualSubmit}
            className="w-full flex items-center gap-2 bg-white/5 hover:bg-white/10 focus-within:bg-white/10 border border-white/10 focus-within:border-electric/50 rounded-2xl px-3.5 py-2 transition backdrop-blur-xl"
          >
            <input
              type="text"
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              placeholder="Speak to AI Core or type here..."
              className="bg-transparent text-xs text-white placeholder-white/35 focus:outline-none flex-1 font-sans"
              disabled={agentPhase === "thinking"}
            />
            {manualText.trim() && (
              <button
                type="submit"
                disabled={agentPhase === "thinking"}
                className="p-1 rounded-lg bg-electric text-white shadow-electric-glow transition active:scale-90"
                title="Send"
              >
                <CornerDownLeft className="w-3.5 h-3.5" />
              </button>
            )}
          </form>
        </div>
      )}
    </div>
  );
};

export default App;
