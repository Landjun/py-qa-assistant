import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResp } from '@/types'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000
})

http.interceptors.response.use(
  (res) => {
    const payload = res.data as ApiResp<unknown>
    if (typeof payload?.success === 'boolean') {
      if (!payload.success) {
        ElMessage.error(payload.message || '请求失败')
        return Promise.reject(new Error(payload.message))
      }
      return payload
    }
    return payload
  },
  (err) => {
    ElMessage.error(err?.response?.data?.message || err.message || '网络异常')
    return Promise.reject(err)
  }
)

export default http
