import client from "./client";

export interface SystemStatus {
  document_count: number;
  chunk_count: number;
  faiss_vector_count: number;
  deepseek_configured: boolean;
  dashscope_configured: boolean;
  deepseek_model: string;
  embedding_model: string;
  rerank_model: string;
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const res = await client.get<SystemStatus>("/settings/status");
  return res.data;
}
