/**
 * API Service Client for Q-Doc MVP DeepTech Clinical Inference Engine.
 * Strictly English-only communications protocol (en-US / en-IN).
 */

export interface StartSessionResponse {
  session_id: string;
  language: string;
  mode: "autonomous" | "supervised";
  agent_message: string;
  audio?: any;
  slots: Record<string, any>;
}

export interface TurnResponse {
  session_id: string;
  transcript_received: string;
  agent_response: string;
  slots: Record<string, any>;
  is_ready_for_photo: boolean;
  is_final_verdict_ready?: boolean;
  confirmation_prompt?: string;
  turn_count: number;
  missing_slots: string[];
  audio?: any;
  language?: string;
  verdict_data?: AnalyzeResponse;
}

export interface PhotoResponse {
  session_id: string;
  image_id: string;
  quality: {
    quality_score: number;
    quality_passed: boolean;
    blur_score: number;
    brightness_score: number;
    guidance_en: string;
    guidance_hi?: string;
  };
  quality_passed: boolean;
  message: string;
  agent_question?: string;
  audio?: any;
  slots?: Record<string, any>;
  suspected_differentials?: string[];
  photo_analyzed?: boolean;
}

export interface AnalyzeResponse {
  session_id: string;
  image_id: string;
  image_prediction: {
    probabilities: Record<string, number>;
    top_condition: string;
    confidence: number;
    image_quality_score: number;
    quality_passed: boolean;
  };
  reasoner_output: {
    differential: Array<{
      condition: string;
      probability: number;
      clinical_justification: string;
    }>;
    top_diagnosis: string;
    final_confidence: number;
    identified_red_flags: string[];
    synthesized_explanation: string;
    gain_from_voice_history?: string;
  };
  policy_decision: {
    action: "speak_verdict" | "refer_only" | "supervised_queue" | "retake_image";
    abstain: boolean;
    urgency: "routine" | "seek_opd" | "emergency";
    spoken_patient_message: string;
    doctor_brief_id?: string;
    applied_rules: string[];
  };
  audio?: any;
  doctor_brief_id: string;
}

export interface ClinicianBriefItem {
  id: string;
  session_id: string;
  created_at: string;
  brief_data: {
    session_id: string;
    patient_metadata: {
      primary_language: string;
      consultation_timestamp: string;
    };
    history_slots: Record<string, any>;
    image_metrics?: {
      quality_score: number;
      quality_passed: boolean;
      probabilities: Record<string, number>;
    };
    ranked_differential: Array<{
      condition: string;
      probability: number;
      clinical_justification: string;
    }>;
    detected_red_flags: string[];
    synthesized_explanation: string;
    gain_from_voice_history?: string;
    triage_verdict: {
      top_diagnosis: string;
      confidence: number;
      urgency: "routine" | "seek_opd" | "emergency";
      action: string;
      abstain: boolean;
      applied_safety_rules: string[];
      patient_spoken_message: string;
    };
  };
  doctor_review?: {
    reviewed: boolean;
    approved: boolean;
    doctor_notes: string;
    reviewed_at: string;
  };
}

export interface DemoCase {
  id: string;
  title: string;
  language: string;
  utterance: string;
  slots: Record<string, any>;
  condition: string;
  mode: "autonomous" | "supervised";
  description: string;
  is_blurry?: boolean;
}

const BASE_URL = "";

export async function startSession(
  language: string = "en-IN",
  mode: "autonomous" | "supervised" = "autonomous"
): Promise<StartSessionResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, mode }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Failed to initialize session.`);
  }
  return res.json();
}

export async function sendTurn(
  sessionId: string,
  transcript: string,
  language: string = "en-IN",
  audioBase64?: string
): Promise<TurnResponse> {
  const payload: any = { transcript, language };
  if (audioBase64) {
    payload.audio_base64 = audioBase64;
  }
  const res = await fetch(`${BASE_URL}/api/v1/session/${sessionId}/turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Failed to submit clinical turn.`);
  }
  return res.json();
}

export async function uploadPhoto(sessionId: string, file: File): Promise<PhotoResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/api/v1/session/${sessionId}/photo`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Failed to upload lesion imagery.`);
  }
  return res.json();
}

export async function analyzeSession(
  sessionId: string,
  imageId?: string,
  file?: File
): Promise<AnalyzeResponse> {
  const formData = new FormData();
  if (imageId) formData.append("image_id", imageId);
  if (file) formData.append("file", file);

  const res = await fetch(`${BASE_URL}/api/v1/session/${sessionId}/analyze`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Inference pipeline error.`);
  }
  return res.json();
}

export async function getClinicianBrief(sessionId: string): Promise<ClinicianBriefItem> {
  const res = await fetch(`${BASE_URL}/api/v1/session/${sessionId}/brief`);
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Failed to fetch clinician brief.`);
  }
  return res.json();
}

export async function listAllBriefs(): Promise<ClinicianBriefItem[]> {
  const res = await fetch(`${BASE_URL}/api/v1/briefs`);
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Failed to list clinical briefs.`);
  }
  return res.json();
}

export async function reviewBrief(
  sessionId: string,
  approved: boolean,
  notes: string = ""
): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/v1/session/${sessionId}/brief/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved, notes }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP failure ${res.status}: Failed to submit clinician review.`);
  }
  return res.json();
}

export async function getAdminMode(): Promise<{ mode: "autonomous" | "supervised" }> {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mode`);
  if (!res.ok) throw new Error("Failed to load policy configuration");
  return res.json();
}

export async function setAdminMode(
  mode: "autonomous" | "supervised"
): Promise<{ success: boolean; mode: string }> {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mode`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
  if (!res.ok) throw new Error("Failed to update autonomy mode");
  return res.json();
}

export async function getDemoCases(): Promise<DemoCase[]> {
  const res = await fetch(`${BASE_URL}/api/v1/demo/cases`);
  if (!res.ok) throw new Error("Failed to fetch validation demo cases");
  return res.json();
}

export async function getEvalReport(): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/v1/eval/report`);
  if (!res.ok) throw new Error("Failed to fetch evaluation benchmark report");
  return res.json();
}
