import http from './http'
import type { ApiResp, Student } from '@/types'

export interface DashboardSummary {
  total_students: number
  high_intent_count: number
  pending_follow_count: number
  closed_deals_count: number
  weekly_new_followups: number
  recent_followed_students: Student[]
  pending_follow_students: Student[]
}

export const getDashboardSummary = async () =>
  (await http.get<ApiResp<DashboardSummary>>('/dashboard/summary')).data
