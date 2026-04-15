import http from './http'
import type { ApiResp, ChatRecord } from '@/types'

export const getChatRecords = async (studentId: number) =>
  (await http.get<ApiResp<ChatRecord[]>>(`/chat-records/${studentId}`)).data

export const createChatRecord = async (payload: { student_id: number; content: string; source?: string }) =>
  (await http.post<ApiResp<ChatRecord>>('/chat-records', payload)).data

export const deleteChatRecord = async (id: number) =>
  (await http.delete<ApiResp<null>>(`/chat-records/${id}`)).data
