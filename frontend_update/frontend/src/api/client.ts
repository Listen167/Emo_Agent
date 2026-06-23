import axios from 'axios'

/**
 * 统一 Axios 客户端
 *
 * 开发环境 (npm run dev):
 *   VITE_API_BASE_URL 未设置 → baseURL = '/api'
 *   Vite 代理将 /api -> http://localhost:8000
 *
 * 生产环境 (CloudBase 部署):
 *   在 .env.production 中设置 VITE_API_BASE_URL
 *   例如: VITE_API_BASE_URL=https://your-ngrok-url/api
 *   前端直接向该地址发请求
 */

/** 后端根地址（不含 /api 后缀）—— 用于静态资源 /data/... */
export const BACKEND_ORIGIN: string = import.meta.env.VITE_BACKEND_ORIGIN || ''
const baseURL: string = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL,
  timeout: 60000,
})

/**
 * 将后端返回的相对资源 URL 转换为可访问的完整 URL
 * 例如 /data/tts/xxx.wav → https://your-ngrok-url/data/tts/xxx.wav
 * 仅在设置了 VITE_BACKEND_ORIGIN 时生效
 */
export function resolveAssetUrl(url: string | null | undefined): string {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (!BACKEND_ORIGIN) return url
  return BACKEND_ORIGIN + url
}

export default apiClient
