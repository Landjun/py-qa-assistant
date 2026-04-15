import http from './http'
import type { ApiResp, FollowUp } from '@/types'

export const getFollowups = async (studentId: number) =>
  (await http.get<ApiResp<FollowUp[]>>(`/follow-ups/${studentId}`)).data

export const createFollowup = async (payload: {
  student_id: number
  follow_time: string
  follow_method?: string
  content: string
  student_feedback?: string
  judgment?: string
  next_action?: string
  next_follow_time?: string
}) => (await http.post<ApiResp<FollowUp>>('/follow-ups', payload)).data
