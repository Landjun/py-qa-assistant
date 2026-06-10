import client from "./client";

export interface Document {
  id: number;
  filename: string;
  title: string;
  file_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface Chunk {
  id: number;
  document_id: number;
  faiss_id: number | null;
  title_path: string;
  content: string;
  char_count: number;
  created_at: string;
}

export async function uploadDocument(file: File): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  const res = await client.post<Document>("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function listDocuments(): Promise<Document[]> {
  const res = await client.get<Document[]>("/documents");
  return res.data;
}

export async function getChunks(documentId: number): Promise<Chunk[]> {
  const res = await client.get<Chunk[]>(`/documents/${documentId}/chunks`);
  return res.data;
}

export async function deleteDocument(documentId: number): Promise<void> {
  await client.delete(`/documents/${documentId}`);
}
