import client from "./client";

export interface LogStep {
  id: number;
  step_name: string;
  service_name: string;
  input_json: string;
  output_json: string;
  duration_ms: number;
  status: "SUCCESS" | "FAILED";
  error_message: string;
  created_at: string;
}

export interface LogItem {
  id: number;
  conversation_id: number | null;
  question: string;
  resolved_question: string;
  intent: string;
  status: "SUCCESS" | "FAILED";
  total_duration_ms: number;
  source_count: number;
  final_answer: string;
  created_at: string;
}

export interface LogDetail extends LogItem {
  steps: LogStep[];
}

export interface LogListResponse {
  total: number;
  page: number;
  page_size: number;
  items: LogItem[];
}

export async function listLogs(params: {
  keyword?: string;
  intent?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<LogListResponse> {
  const query: Record<string, string | number> = {};
  if (params.keyword) query.keyword = params.keyword;
  if (params.intent) query.intent = params.intent;
  if (params.status) query.status = params.status;
  if (params.page) query.page = params.page;
  if (params.page_size) query.page_size = params.page_size;
  const res = await client.get<LogListResponse>("/logs", { params: query });
  return res.data;
}

export async function getLog(logId: number): Promise<LogDetail> {
  const res = await client.get<LogDetail>(`/logs/${logId}`);
  return res.data;
}
