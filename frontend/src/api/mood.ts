import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 60000 })

export interface MoodDay {
  date: string
  mood_label: string
  mood_score?: number | null
  count: number
  source_count: Record<string, number>
}

export interface MoodSummary {
  days: MoodDay[]
  total_count: number
  mood_count: Record<string, number>
}

export const getMoodCalendar = (sid: string, year: number, month: number) =>
  api.get<MoodSummary>(`/mood/calendar?session_id=${sid}&year=${year}&month=${month}`)
