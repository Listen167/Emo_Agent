import api from './client'
import { BACKEND_ORIGIN } from './client'

export const sendChat = (form: FormData) => api.post('/chat/send', form)
export const getHistory = (sid: string) => api.get(`/chat/history?session_id=${sid}`)

export const getChatStreamUrl = () => {
  const origin = BACKEND_ORIGIN || window.location.origin
  const wsOrigin = origin.replace(/^http/, 'ws')
  return `${wsOrigin}/api/chat/stream`
}
