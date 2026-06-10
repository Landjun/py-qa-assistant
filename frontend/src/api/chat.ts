import client from "./client";

export interface QAData {
  question_type: string;
  answer: string;
  beginner_explanation: string;
  code_example: string;
  need_more_info: boolean;
  need_more_info_fields: string[];
}

export interface QAResponse {
  success: boolean;
  data: QAData | null;
  error: string;
  duration_ms: number;
  conversation_id: number | null;
}

export async function simpleAsk(
  message: string,
  conversationId?: number,
): Promise<QAResponse> {
  const res = await client.post<QAResponse>("/chat/simple", {
    message,
    conversation_id: conversationId ?? null,
  });
  return res.data;
}

// ─── RAG /ask ────────────────────────────────────────────────────────────────

export interface SourceInfo {
  document_id: number;
  chunk_id: number;
  source: string;
  score: number;
  image_path?: string | null;
}

export interface BugDetail {
  error_type: string;
  plain_explanation: string;
  likely_causes: string[];
  fix_steps: string[];
  before_code: string;
  after_code: string;
  need_more_info: boolean;
  need_more_info_fields: string[];
}

export interface RAGAnswer {
  useful: boolean;
  content: string;
  beginner_explanation: string;
  code_example: string;
  sources: SourceInfo[];
  bug_detail?: BugDetail;
}

export interface ImageUnderstanding {
  image_type: string;
  ocr_text: string;
  summary: string;
  detected_error: string;
}

export interface LessonAssetRef {
  asset_type: string;
  filename: string;
  url: string;
}

export interface LessonContext {
  lesson_no: number;
  title: string;
  summary: string | null;
  assets: LessonAssetRef[];
  fallback: boolean;
}

export interface RAGResponse {
  success: boolean;
  answer: RAGAnswer | null;
  error: string;
  duration_ms: number;
  conversation_id: number | null;
  intent: string;
  confidence: number;
  resolved_question: string;
  image_understanding: ImageUnderstanding | null;
  lesson_context: LessonContext | null;
}

export async function ask(
  message: string,
  conversationId?: number,
  imageBase64?: string,
): Promise<RAGResponse> {
  const res = await client.post<RAGResponse>("/chat/ask", {
    message,
    conversation_id: conversationId ?? null,
    image_base64: imageBase64 ?? null,
  });
  return res.data;
}
