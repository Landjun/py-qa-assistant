import http from './http'
import type { ApiResp, Student } from '@/types'

export const getStudents = async () => (await http.get<ApiResp<Student[]>>('/students')).data
export const getStudent = async (id: number) => (await http.get<ApiResp<Student>>(`/students/${id}`)).data
export const createStudent = async (payload: Partial<Student>) =>
  (await http.post<ApiResp<Student>>('/students', payload)).data
export const updateStudent = async (id: number, payload: Partial<Student>) =>
  (await http.put<ApiResp<Student>>(`/students/${id}`, payload)).data
export const updateStudentStage = async (id: number, to_stage: string, remark = '') =>
  (await http.post<ApiResp<unknown>>(`/students/${id}/stage`, { to_stage, remark })).data
