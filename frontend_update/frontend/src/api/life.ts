import api from './client'

export interface LifeRecordItem {
  id: number
  session_id: string
  title?: string | null
  content: string
  mood_label?: string | null
  location?: string | null
  tags: string[]
  media_url?: string | null
  visibility: 'private' | 'public'
  like_count: number
  comment_count: number
  repost_count: number
  published_at?: string | null
  created_at: string
}

export const createLifeRecord = (form: FormData) =>
  api.post<LifeRecordItem>('/life/records', form)

export const getLifeRecords = (sid: string) =>
  api.get<LifeRecordItem[]>(`/life/records?session_id=${sid}`)

export const deleteLifeRecord = (id: number, sid: string) =>
  api.delete(`/life/records/${id}?session_id=${sid}`)
