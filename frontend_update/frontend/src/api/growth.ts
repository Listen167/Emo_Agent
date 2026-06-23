import api from './client'

export interface GrowthProfileItem {
  session_id: string
  nickname?: string | null
  current_state?: string | null
  focus?: string | null
  personality: string
  weekly_goal?: string | null
  setup_completed: boolean
  private_mode: boolean
  anonymous_default: boolean
  crisis_guard: boolean
  created_at: string
  updated_at: string
}

export interface GrowthMemoryItem {
  id: number
  category: string
  content: string
  created_at: string
}

export interface GrowthStateItem {
  profile: GrowthProfileItem
  memories: GrowthMemoryItem[]
}

export interface GrowthProfileUpdate {
  session_id: string
  nickname?: string | null
  current_state?: string | null
  focus?: string | null
  personality?: string | null
  weekly_goal?: string | null
  setup_completed?: boolean
  private_mode?: boolean
  anonymous_default?: boolean
  crisis_guard?: boolean
}

export const getGrowthState = (sid: string) =>
  api.get<GrowthStateItem>(`/growth?session_id=${encodeURIComponent(sid)}`)

export const updateGrowthProfile = (payload: GrowthProfileUpdate) =>
  api.put<GrowthStateItem>('/growth', payload)

export const createGrowthMemory = (sid: string, category: string, content: string) =>
  api.post<GrowthMemoryItem>('/growth/memories', {
    session_id: sid,
    category,
    content,
  })

export const deleteGrowthMemory = (id: number, sid: string) =>
  api.delete(`/growth/memories/${id}?session_id=${encodeURIComponent(sid)}`)

export const clearGrowthState = (sid: string) =>
  api.delete(`/growth?session_id=${encodeURIComponent(sid)}`)
