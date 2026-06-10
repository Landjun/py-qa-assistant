import client from "./client";

export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
  extra_json: string | null;
  created_at: string;
}

export interface MessageExtra {
  // simple ask fields
  question_type?: string;
  need_more_info?: boolean;
  need_more_info_fields?: string[];
  // rag / intent fields
  type?: string;
  intent?: string;
  useful?: boolean;
  beginner_explanation?: string;
  code_example?: string;
  sources?: { document_id: number; chunk_id: number; source: string; score: number }[];
  bug_detail?: {
    error_type: string;
    plain_explanation: string;
    likely_causes: string[];
    fix_steps: string[];
    before_code: string;
    after_code: string;
    need_more_info: boolean;
    need_more_info_fields: string[];
  };
  no_retrieval?: boolean;
  duration_ms?: number;
}

export function parseExtra(msg: Message): MessageExtra | null {
  if (!msg.extra_json) return null;
  try {
    return JSON.parse(msg.extra_json) as MessageExtra;
  } catch {
    return null;
  }
}

export async function createConversation(): Promise<Conversation> {
  const res = await client.post<Conversation>("/conversations");
  return res.data;
}

export async function listConversations(): Promise<Conversation[]> {
  const res = await client.get<Conversation[]>("/conversations");
  return res.data;
}

export async function getMessages(conversationId: number): Promise<Message[]> {
  const res = await client.get<Message[]>(`/conversations/${conversationId}/messages`);
  return res.data;
}

export async function deleteConversation(conversationId: number): Promise<void> {
  await client.delete(`/conversations/${conversationId}`);
}
