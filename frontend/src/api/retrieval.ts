import client from "./client";

export interface RetrievalResult {
  content: string;
  source: string;
  document_id: number;
  chunk_id: number;
  score: number;
  image_path?: string | null;
}

export interface SearchResponse {
  query: string;
  results: RetrievalResult[];
  duration_ms: number;
}

export async function retrievalSearch(
  query: string,
  top_k = 3,
  score = 0.5,
): Promise<SearchResponse> {
  const res = await client.post<SearchResponse>("/retrieval/search", {
    query,
    top_k,
    score,
  });
  return res.data;
}
