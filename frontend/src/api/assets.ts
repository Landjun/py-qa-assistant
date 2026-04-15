import http from './http'
import type { ApiResp, Asset } from '@/types'

export const getAssets = async () => (await http.get<ApiResp<Asset[]>>('/assets')).data
export const createAsset = async (payload: Partial<Asset>) => (await http.post<ApiResp<Asset>>('/assets', payload)).data
export const updateAsset = async (id: number, payload: Partial<Asset>) =>
  (await http.put<ApiResp<Asset>>(`/assets/${id}`, payload)).data
export const deleteAsset = async (id: number) => (await http.delete<ApiResp<null>>(`/assets/${id}`)).data
