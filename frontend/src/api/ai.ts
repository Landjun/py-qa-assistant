import http from './http'
import type { AIAnalysis, ApiResp } from '@/types'

export interface AnalyzePayload {
  chat_record_id?: number
  chat_content?: string
}

export const triggerAIAnalysis = async (studentId: number, payload: AnalyzePayload = {}) =>
  (await http.post<ApiResp<AIAnalysis>>(`/ai/analyze/${studentId}`, payload)).data

export const getAIAnalyses = async (studentId: number) =>
  (await http.get<ApiResp<AIAnalysis[]>>(`/ai/analyses/${studentId}`)).data

export const syncAnalysisToProfile = async (analysisId: number) =>
  (await http.post<ApiResp<{ student_id: number; profile_id: number }>>(`/ai/analyses/${analysisId}/sync-profile`)).data
