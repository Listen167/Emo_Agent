import api from './client'

export interface UserProfile {
  id: number
  session_id: string
  nickname?: string | null
  avatar_url?: string | null
  motto?: string | null
  gender?: string | null
  ebti_type?: string | null
  ebti_name?: string | null
  ebti_avatar?: string | null
  created_at: string
  updated_at: string
}

export interface ProfileUpdatePayload {
  session_id: string
  nickname?: string | null
  motto?: string | null
  gender?: string | null
  current_state?: string | null
  focus?: string | null
  personality?: string | null
  weekly_goal?: string | null
  setup_completed?: boolean
}

export interface ProfileEbtiPayload {
  session_id: string
  ebti_type: string
  ebti_name?: string | null
  ebti_avatar?: string | null
}

export const getProfile = (sessionId: string) =>
  api.get<UserProfile>(`/profile?session_id=${encodeURIComponent(sessionId)}`)

export const updateProfile = (payload: ProfileUpdatePayload) =>
  api.put<UserProfile>('/profile', payload)

export const uploadProfileAvatar = (form: FormData) =>
  api.post<UserProfile>('/profile/avatar', form)

export const updateProfileEbti = (payload: ProfileEbtiPayload) =>
  api.put<UserProfile>('/profile/ebti', payload)
