import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 60000 })

export interface LifeRecordItem {
  id: number
  session_id: string
  title?: string | null
  content: string
  mood_label?: string | null
  location?: string | null
  tags: string[]
  media_url?: string | null
  created_at: string
}

export const createLifeRecord = (form: FormData) =>
  api.post<LifeRecordItem>('/life/records', form)

export const getLifeRecords = (sid: string) =>
  api.get<LifeRecordItem[]>(`/life/records?session_id=${sid}`)

export const deleteLifeRecord = (id: number, sid: string) =>
  api.delete(`/life/records/${id}?session_id=${sid}`)
