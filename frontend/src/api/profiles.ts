import http from './http'
import type { ApiResp, Profile } from '@/types'

export const getProfile = async (studentId: number) =>
  (await http.get<ApiResp<Profile | null>>(`/profiles/${studentId}`)).data

export const saveProfile = async (studentId: number, payload: Partial<Profile>) =>
  (await http.put<ApiResp<Profile>>(`/profiles/${studentId}`, payload)).data
