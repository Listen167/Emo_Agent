import axios from 'axios'
const api = axios.create({ baseURL: '/api', timeout: 60000 })

export const sendChat = (form: FormData) => api.post('/chat/send', form)
export const getHistory = (sid: string) => api.get(`/chat/history?session_id=${sid}`)