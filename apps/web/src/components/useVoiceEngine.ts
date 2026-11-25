import { useCallback, useEffect, useRef, useState } from "react";

interface Capture {
  stream: MediaStream;
  recorder: MediaRecorder;
  context?: AudioContext;
  frame?: number;
}

function release(capture: Capture) {
  if (capture.frame !== undefined) cancelAnimationFrame(capture.frame);
  capture.stream.getTracks().forEach(track => track.stop());
  if (capture.context) void capture.context.close().catch(() => {});
}

export function useVoiceEngine({ onFinalTranscript }: {
  onFinalTranscript: (text: string, audioBase64?: string) => void;
}) {
  const [isListening, setIsListening] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [permissionError, setPermissionError] = useState<string | null>(null);
  const active = useRef<Capture | null>(null);
  const busy = useRef(false);
  const generation = useRef(0);
  const submit = useRef(onFinalTranscript);
  useEffect(() => { submit.current = onFinalTranscript; }, [onFinalTranscript]);

  const cancelListening = useCallback(() => {
    generation.current++;
    busy.current = false;
    const capture = active.current;
    active.current = null;
    if (capture) {
      if (capture.recorder.state !== "inactive") capture.recorder.stop();
      release(capture);
    }
    setIsListening(false);
    setAudioLevel(0);
  }, []);

  useEffect(() => cancelListening, [cancelListening]);

  const stopListening = () => {
    const recorder = active.current?.recorder;
    if (recorder?.state === "recording") recorder.stop();
  };

  const startListening = async () => {
    if (busy.current) return;
    busy.current = true;
    const token = ++generation.current;
    setPermissionError(null);
    let stream: MediaStream | undefined;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (generation.current !== token) {
        stream.getTracks().forEach(track => track.stop());
        return;
      }
      const recorder = new MediaRecorder(stream);
      const capture: Capture = { stream, recorder };
      active.current = capture;
      const chunks: Blob[] = [];
      recorder.ondataavailable = event => {
        if (event.data.size) chunks.push(event.data);
      };
      recorder.onerror = () => {
        if (generation.current !== token) return;
        cancelListening();
        setPermissionError("Microphone recording failed. Please start recording again.");
      };
      stream.getAudioTracks()[0].onended = () => {
        if (generation.current !== token || recorder.state !== "recording") return;
        cancelListening();
        setPermissionError("The microphone disconnected during recording.");
      };
      recorder.onstop = () => {
        if (generation.current !== token) return;
        active.current = null;
        release(capture);
        setIsListening(false);
        setAudioLevel(0);
        const reader = new FileReader();
        reader.onloadend = () => {
          if (generation.current !== token) return;
          busy.current = false;
          const encoded = typeof reader.result === "string" && reader.result.split(",")[1];
          if (encoded) submit.current("", encoded);
          else setPermissionError("No microphone audio was captured.");
        };
        reader.readAsDataURL(new Blob(chunks, { type: recorder.mimeType }));
      };
      recorder.start(250);
      setIsListening(true);
      // The level meter is visual only. Recording ends when the patient presses Finish.
      try {
        const context = new AudioContext();
        capture.context = context;
        const analyser = context.createAnalyser();
        analyser.fftSize = 512;
        context.createMediaStreamSource(stream).connect(analyser);
        const samples = new Uint8Array(analyser.fftSize);
        const meter = () => {
          analyser.getByteTimeDomainData(samples);
          const energy = samples.reduce((sum, n) => sum + ((n - 128) / 128) ** 2, 0);
          setAudioLevel(Math.min(1, 3.5 * Math.sqrt(energy / samples.length)));
          capture.frame = requestAnimationFrame(meter);
        };
        meter();
      } catch { /* Recording also works without an audio meter. */ }
    } catch (error) {
      stream?.getTracks().forEach(track => track.stop());
      if (generation.current !== token) return;
      cancelListening();
      setPermissionError(error instanceof DOMException && error.name === "NotAllowedError"
        ? "Microphone permission was denied. Allow microphone access in your browser."
        : "Could not start recording from this microphone.");
    }
  };

  return { isListening, audioLevel, permissionError, startListening, stopListening, cancelListening };
}
