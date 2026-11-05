import React, { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, RefreshCw, Upload, CheckCircle2, AlertTriangle, Eye, ShieldAlert } from "lucide-react";

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  qualityPassed?: boolean;
  qualityGuidance?: string;
  isProcessing?: boolean;
}

export const CameraCapture: React.FC<CameraCaptureProps> = ({
  onCapture,
  qualityPassed,
  qualityGuidance,
  isProcessing = false,
}) => {
  const [streamActive, setStreamActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [liveWarning, setLiveWarning] = useState<string | null>(null);
  const [opticsCalibrated, setOpticsCalibrated] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const monitorTimerRef = useRef<any>(null);

  // Stop camera tracks and release hardware
  const stopCamera = useCallback(() => {
    if (monitorTimerRef.current) {
      clearInterval(monitorTimerRef.current);
      monitorTimerRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      streamRef.current = null;
    }
    setStreamActive(false);
    setLiveWarning(null);
  }, []);

  // Real-time frame luminance and blur estimation
  const sampleFrameQuality = useCallback(() => {
    if (!videoRef.current || !streamActive) return;
    const video = videoRef.current;
    if (video.videoWidth === 0 || video.videoHeight === 0) return;

    try {
      const offCanvas = document.createElement("canvas");
      offCanvas.width = 160;
      offCanvas.height = 120;
      const ctx = offCanvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) return;

      ctx.drawImage(video, 0, 0, 160, 120);
      const imgData = ctx.getImageData(0, 0, 160, 120);
      const data = imgData.data;

      let totalBrightness = 0;
      const pixelCount = data.length / 4;

      for (let i = 0; i < data.length; i += 4) {
        // Luminance formula
        const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
        totalBrightness += lum;
      }

      const avgBrightness = totalBrightness / pixelCount;

      if (avgBrightness < 35) {
        setLiveWarning("WARNING: LOW ILLUMINATION (< 35 LUX)");
        setOpticsCalibrated(false);
      } else if (avgBrightness > 230) {
        setLiveWarning("WARNING: EXPOSURE BLOWN OUT / GLARE");
        setOpticsCalibrated(false);
      } else {
        setLiveWarning(null);
        setOpticsCalibrated(true);
      }
    } catch (e) {
      // Ignore sampling errors
    }
  }, [streamActive]);

  const startCamera = async () => {
    stopCamera();
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => {});
      }
      setStreamActive(true);
      setPreviewUrl(null);

      // Start periodic optical sampler
      monitorTimerRef.current = setInterval(sampleFrameQuality, 600);
    } catch (err: any) {
      console.warn("Direct camera access failed:", err);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setCameraError("Camera permission denied. Allow optical sensor access or upload a lesion file below.");
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        setCameraError("No optical camera sensor detected on this device. Please upload an image.");
      } else {
        setCameraError("Unable to initialize optical sensor. Fallback to image upload.");
      }
      stopCamera();
    }
  };

  const takeSnapshot = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth || 1280;
    canvas.height = videoRef.current.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (blob) {
          stopCamera();
          const file = new File([blob], `lesion_capture_${Date.now()}.jpg`, {
            type: "image/jpeg",
          });
          setPreviewUrl(URL.createObjectURL(blob));
          onCapture(file);
        }
      },
      "image/jpeg",
      0.95
    );
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      stopCamera();
      setPreviewUrl(URL.createObjectURL(file));
      onCapture(file);
    }
  };

  // Cleanup on unmount: ALWAYS stop video tracks
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return (
    <div className="w-full glass-panel rounded-2xl p-4 sm:p-5 flex flex-col items-center gap-4 border border-white/10 relative overflow-hidden">
      {/* Background Ambient HUD Grid */}
      <div className="absolute inset-0 scanner-grid opacity-30 pointer-events-none" />

      {/* Header Bar */}
      <div className="w-full flex items-center justify-between text-xs z-10">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-electric animate-pulse" />
          <span className="font-mono font-bold tracking-widest uppercase text-slate-200">
            OPTICAL SCANNER MODULE
          </span>
        </div>
        <span className="font-mono text-[10px] text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
          MACRO FOCUS 10-15 CM
        </span>
      </div>

      {/* Hardware Error Fallback Notification */}
      <AnimatePresence>
        {cameraError && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2.5 z-10"
          >
            <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
            <span className="font-mono text-[11px] leading-tight">{cameraError}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* SCANNER VIEWPORT / TARGETING RETICLE */}
      <div
        className={`w-full aspect-[4/3] max-h-72 bg-black rounded-xl border relative overflow-hidden flex items-center justify-center transition-all duration-300 z-10 ${
          liveWarning || qualityPassed === false
            ? "border-neon shadow-neon-glow"
            : opticsCalibrated
            ? "border-electric shadow-electric-glow"
            : "border-white/15"
        }`}
      >
        {/* Live Camera Stream Video */}
        <video
          ref={videoRef}
          playsInline
          muted
          className={`w-full h-full object-cover ${streamActive ? "block" : "hidden"}`}
        />

        {/* Captured Preview Image */}
        {!streamActive && previewUrl && (
          <img
            src={previewUrl}
            alt="Target Lesion"
            className="w-full h-full object-cover"
          />
        )}

        {/* Standby Camera Prompt */}
        {!streamActive && !previewUrl && (
          <div className="flex flex-col items-center gap-2 text-slate-500 p-6 text-center">
            <Camera className="w-10 h-10 stroke-[1.5] text-slate-600 mb-1" />
            <span className="font-mono text-xs uppercase tracking-wider text-slate-400">
              OPTICAL SENSOR IN STANDBY
            </span>
            <p className="text-[11px] text-slate-500 max-w-xs">
              Align camera perpendicularly to the skin lesion under uniform diffuse lighting.
            </p>
          </div>
        )}

        {/* HIGH-TECH BIOMETRIC TARGETING RETICLE OVERLAY (Dashed Oval & Crosshairs) */}
        {streamActive && (
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            {/* Corner Bracket Reticles */}
            <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-electric" />
            <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-electric" />
            <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-electric" />
            <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-electric" />

            {/* Elliptical Alignment Guide */}
            <div
              className={`w-44 h-56 rounded-[50%] border-2 border-dashed transition-all duration-300 flex items-center justify-center ${
                liveWarning
                  ? "border-[#FF007F] animate-pulse"
                  : "border-[#2E89FF]/80 shadow-[0_0_15px_rgba(46,137,255,0.4)]"
              }`}
            >
              <div className="w-2 h-2 rounded-full bg-electric/60" />
            </div>

            {/* Monospace HUD Crosshair Coordinates */}
            <div className="absolute bottom-2 left-3 font-mono text-[9px] text-electric/70">
              FOV: 78° | LENS: MULTISPECTRAL
            </div>
            <div className="absolute top-2 right-3 font-mono text-[9px] text-electric/70">
              FPS: 30 | RES: 1080P
            </div>
          </div>
        )}

        {/* DYNAMIC WARNING OVERLAY (Live Low-light or Backend Blur/Brightness Reject) */}
        {(liveWarning || (qualityPassed === false && qualityGuidance)) && (
          <div className="absolute top-3 inset-x-3 bg-neon/90 text-white font-mono text-[10px] font-bold py-1.5 px-3 rounded-lg shadow-neon-glow flex items-center justify-center gap-2 z-20 animate-pulse">
            <AlertTriangle className="w-3.5 h-3.5 text-white shrink-0" />
            <span>{liveWarning || qualityGuidance}</span>
          </div>
        )}

        {/* OPTIMAL STATUS BADGE */}
        {streamActive && !liveWarning && opticsCalibrated && (
          <div className="absolute top-3 inset-x-3 bg-electric/80 text-white font-mono text-[10px] font-bold py-1 px-3 rounded-lg shadow-electric-glow flex items-center justify-center gap-1.5 z-20">
            <CheckCircle2 className="w-3 h-3 text-white" />
            <span>OPTICS CALIBRATED: READY FOR CAPTURE</span>
          </div>
        )}
      </div>

      {/* QUALITY REJECTION FEEDBACK NOTICE */}
      {qualityPassed === false && qualityGuidance && (
        <div className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2.5 z-10">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <div className="flex-1">
            <span className="font-mono font-bold block text-[10px] uppercase text-rose-400">
              QUALITY GATE REJECTION (BLUR/LIGHTING)
            </span>
            <span className="text-[11px] leading-tight">{qualityGuidance}</span>
          </div>
        </div>
      )}

      {/* CONTROLS BAR (Tactile DeepTech Buttons) */}
      <div className="w-full flex items-center justify-between gap-3 pt-1 z-10">
        {!streamActive ? (
          <button
            onClick={startCamera}
            disabled={isProcessing}
            className="flex-1 py-2.5 px-4 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-white/5 hover:bg-white/10 text-white border border-white/15 transition flex items-center justify-center gap-2 active:scale-98"
          >
            <Camera className="w-4 h-4 text-electric" />
            <span>Launch Scanner</span>
          </button>
        ) : (
          <button
            onClick={takeSnapshot}
            disabled={isProcessing}
            className="flex-1 py-2.5 px-4 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-blue-600 to-electric hover:from-electric hover:to-blue-400 text-white shadow-electric-glow transition flex items-center justify-center gap-2 active:scale-98"
          >
            <Camera className="w-4 h-4" />
            <span>Acquire Target</span>
          </button>
        )}

        {/* Upload Fallback Button */}
        <label
          className={`py-2.5 px-4 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-white/5 hover:bg-white/10 text-slate-300 border border-white/15 transition flex items-center justify-center gap-2 cursor-pointer active:scale-98 ${
            isProcessing ? "opacity-50 pointer-events-none" : ""
          }`}
        >
          <Upload className="w-3.5 h-3.5 text-slate-400" />
          <span>Upload</span>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>

        {streamActive && (
          <button
            onClick={stopCamera}
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 border border-white/10 transition"
            title="Standby optical sensor"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
