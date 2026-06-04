export interface FileMetadata {
  page_count: number;
  confidence_score: number;
}

export interface FileUploadResult {
  file_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  raw_text: string;
  metadata: FileMetadata;
  error?: string;
}

export interface BatchUploadResponse {
  batch_id: string;
  results: FileUploadResult[];
}

export interface AskRequest {
  query: string;
  language?: "en" | "hi";
}

export interface AskResponse {
  answer: string;
  source: string;
  method: string;
  confidence?: number;
}

export interface HealthResponse {
  status: string;
  service: string;
  llm_mode: string;
}

// --- Document Summary ---

export interface SummaryRequest {
  document_text: string;
  language?: "en" | "hi";
  detail_level?: "brief" | "standard" | "detailed";
}

export interface SummaryResponse {
  summary: string;
  key_points: string[];
  word_count: number;
  status: string;
}

// --- Timeline Generator ---

export interface TimelineRequest {
  document_text: string;
  language?: "en" | "hi";
}

export interface TimelineResponse {
  timeline: TimelineEntry[];
  event_count: number;
  status: string;
}

export interface TimelineEntry {
  date: string;
  event: string;
}

// --- Voice Assistant ---

export interface VoiceQueryRequest {
  transcript: string;
  language?: "en" | "hi";
}

export interface VoiceQueryResponse {
  answer: string;
  source: string;
  method: string;
  confidence?: number;
  transcript: string;
}

// --- Judgement Prediction ---

export interface JudgementRequest {
  case_description: string;
  case_type?: string;
  language?: "en" | "hi";
}

export interface JudgementResponse {
  prediction: string;
  relevant_sections: string[];
  confidence_level: string;
  disclaimer: string;
  status: string;
}
