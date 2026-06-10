import api from './client'

export const sendChat = (form: FormData) => api.post('/chat/send', form)
export const getHistory = (sid: string) => api.get(`/chat/history?session_id=${sid}`)