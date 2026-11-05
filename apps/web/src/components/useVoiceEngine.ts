import React, { useState, useRef, useEffect, useCallback } from "react";

/**
 * useVoiceEngine — Dual-Engine Voice Capture:
 * 1. Primary: Browser Web Speech API (`SpeechRecognition`) for instant live transcription.
 * 2. Secondary: MediaRecorder WAV/WebM recording sent to Sarvam AI STT (`saaras:v3`)
 *    if the browser STT doesn't return text or is blocked.
 * 3. AnalyserNode metering for real-time reactive orb visualizer.
 */

export interface VoiceEngineState {
  isListening: boolean;
  audioLevel: number; // 0-1 normalized RMS from AnalyserNode
  interimTranscript: string;
  permissionError: string | null;
  startListening: () => void;
  stopListening: () => void;
  toggleListening: () => void;
}

interface UseVoiceEngineOptions {
  onFinalTranscript: (text: string, audioBase64?: string) => void;
  language?: string;
}

export function useVoiceEngine({ onFinalTranscript, language = "en-IN" }: UseVoiceEngineOptions): VoiceEngineState {
  const [isListening, setIsListening] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [interimTranscript, setInterimTranscript] = useState("");
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const langRef = useRef<string>(language);
  useEffect(() => {
    langRef.current = language;
  }, [language]);

  const recognitionRef = useRef<any>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const rafRef = useRef<number>(0);
  const dataArrayRef = useRef<Uint8Array<ArrayBuffer> | null>(null);

  // Audio Recorder for Sarvam STT fallback
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Track latest speech buffer and silence timer
  const latestSpeechRef = useRef<string>("");
  const silenceTimerRef = useRef<any>(null);
  const isFlushedRef = useRef<boolean>(false);

  // Always keep latest callback ref
  const onFinalTranscriptRef = useRef(onFinalTranscript);
  useEffect(() => {
    onFinalTranscriptRef.current = onFinalTranscript;
  }, [onFinalTranscript]);

  // ── Convert Blob to Base64 helper ──
  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = (reader.result as string).split(",")[1];
        resolve(base64String);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  // ── Flush speech buffer upstream ──
  const flushTranscript = useCallback(async () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    if (isFlushedRef.current) return;

    const textToSubmit = latestSpeechRef.current.trim();

    // Check if we also recorded audio chunks
    let recordedBase64 = "";
    if (audioChunksRef.current.length > 0) {
      try {
        const mimeType = mediaRecorderRef.current?.mimeType || "audio/webm";
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        if (audioBlob.size > 2000) {
          recordedBase64 = await blobToBase64(audioBlob);
        }
      } catch (err) {
        console.warn("[useVoiceEngine] Blob encoding error:", err);
      }
    }

    // Submit if we have either text transcript OR recorded audio
    if (textToSubmit || recordedBase64) {
      isFlushedRef.current = true;
      console.log("[useVoiceEngine] Submitting turn -> Text:", textToSubmit, "Audio size:", recordedBase64.length);
      onFinalTranscriptRef.current(textToSubmit, recordedBase64 || undefined);
      latestSpeechRef.current = "";
      setInterimTranscript("");
      audioChunksRef.current = [];
    }
  }, []);

  // ── Meter loop: sample AnalyserNode and push audioLevel ──
  const meterLoop = useCallback(() => {
    if (!analyserRef.current || !dataArrayRef.current) return;
    analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
    const data = dataArrayRef.current;

    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      const v = (data[i] - 128) / 128;
      sum += v * v;
    }
    const rms = Math.sqrt(sum / data.length);
    const scaled = Math.min(1, rms * 3.5);
    setAudioLevel(scaled);

    rafRef.current = requestAnimationFrame(meterLoop);
  }, []);

  // ── Tear down audio pipeline ──
  const teardownAudio = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = 0;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      try {
        mediaRecorderRef.current.stop();
      } catch (_) {}
      mediaRecorderRef.current = null;
    }

    if (sourceRef.current) {
      try { sourceRef.current.disconnect(); } catch (_) {}
      sourceRef.current = null;
    }
    if (analyserRef.current) {
      try { analyserRef.current.disconnect(); } catch (_) {}
      analyserRef.current = null;
    }
    if (audioCtxRef.current && audioCtxRef.current.state !== "closed") {
      audioCtxRef.current.close().catch(() => {});
      audioCtxRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    dataArrayRef.current = null;
    setAudioLevel(0);
  }, []);

  // ── Stop listening ──
  const stopListening = useCallback(async () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (_) {}
      recognitionRef.current = null;
    }
    await flushTranscript();
    teardownAudio();
    setIsListening(false);
  }, [flushTranscript, teardownAudio]);

  // ── Start listening ──
  const startListening = useCallback(async () => {
    setPermissionError(null);
    latestSpeechRef.current = "";
    isFlushedRef.current = false;
    setInterimTranscript("");
    audioChunksRef.current = [];

    // 1. Acquire microphone stream
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err: any) {
      setPermissionError(
        err.name === "NotAllowedError" || err.name === "PermissionDeniedError"
          ? "Microphone access denied. Please allow microphone permissions in your browser bar."
          : "Unable to access microphone on this device."
      );
      return;
    }
    streamRef.current = stream;

    // 2. Build Web Audio pipeline for visual meter
    try {
      const ctx = new AudioContext();
      audioCtxRef.current = ctx;
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.6;
      analyserRef.current = analyser;
      const source = ctx.createMediaStreamSource(stream);
      source.connect(analyser);
      sourceRef.current = source;
      dataArrayRef.current = new Uint8Array(analyser.fftSize);
      rafRef.current = requestAnimationFrame(meterLoop);
    } catch (_) {}

    // 3. Start MediaRecorder as backup audio stream
    try {
      const mime = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : MediaRecorder.isTypeSupported("audio/mp4")
        ? "audio/mp4"
        : "";
      const mr = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };
      mr.start(250);
      mediaRecorderRef.current = mr;
    } catch (err) {
      console.warn("[useVoiceEngine] MediaRecorder init failed:", err);
    }

    // 4. Start Speech Recognition
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = langRef.current || "en-IN";

      recognition.onstart = () => {
        setIsListening(true);
        isFlushedRef.current = false;
      };

      recognition.onresult = (event: any) => {
        let interim = "";
        let finalAccum = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalAccum += transcriptPart + " ";
          } else {
            interim += transcriptPart;
          }
        }

        const activeText = (finalAccum + interim).trim();
        if (activeText) {
          latestSpeechRef.current = activeText;
          setInterimTranscript(activeText);

          // Auto-flush after 1.8 seconds of silence
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = setTimeout(() => {
            console.log("[useVoiceEngine] Auto-flushing on pause");
            stopListening();
          }, 1800);
        }
      };

      recognition.onerror = (e: any) => {
        console.warn("[useVoiceEngine] Web Speech API error:", e.error);
        if (e.error === "not-allowed" || e.error === "permission-denied") {
          setPermissionError("Microphone access denied. Please allow microphone permission in the address bar.");
        }
      };

      recognition.onend = () => {
        console.log("[useVoiceEngine] SpeechRecognition ended");
      };

      recognitionRef.current = recognition;

      try {
        recognition.start();
      } catch (err) {
        console.warn("[useVoiceEngine] SpeechRecognition start error:", err);
      }
    } else {
      console.warn("[useVoiceEngine] Browser SpeechRecognition not present; using MediaRecorder Sarvam fallback.");
      setIsListening(true);
    }
  }, [meterLoop, teardownAudio, stopListening]);

  // ── Toggle ──
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (_) {}
      }
      teardownAudio();
    };
  }, [teardownAudio]);

  return {
    isListening,
    audioLevel,
    interimTranscript,
    permissionError,
    startListening,
    stopListening,
    toggleListening,
  };
}
