import api from './client'

export interface ResumePolishRequest {
  section: string
  content: string
  job_description?: string
}

export interface ResumePolishResponse {
  text: string
}

export interface ResumeAnalyzeRequest {
  resume_text: string
  job_description: string
}

export interface ResumeAnalyzeResponse {
  analysis: string
}

export interface ResumeAssistantMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ResumeAssistantPayload {
  text?: string
  audio?: Blob
  session_id: string
  resume_text: string
  job_description?: string
  interview_role?: string
  history: ResumeAssistantMessage[]
  enable_tts?: boolean
}

export interface ResumeAssistantResponse {
  text: string
  user_text: string
  mode: 'resume' | 'interview' | 'interview_summary'
  interview_question_index?: number | null
  interview_total: number
  tts_audio_url?: string | null
}

export const polishResumeText = (payload: ResumePolishRequest) =>
  api.post<ResumePolishResponse>('/resume/polish', payload)

export const analyzeResumeMatch = (payload: ResumeAnalyzeRequest) =>
  api.post<ResumeAnalyzeResponse>('/resume/analyze', payload)

export const sendResumeAssistant = (payload: ResumeAssistantPayload) => {
  const form = new FormData()
  if (payload.text) form.append('text', payload.text)
  if (payload.audio) form.append('audio', payload.audio, 'recording.wav')
  form.append('session_id', payload.session_id)
  form.append('resume_text', payload.resume_text)
  if (payload.job_description) form.append('job_description', payload.job_description)
  if (payload.interview_role) form.append('interview_role', payload.interview_role)
  form.append('history', JSON.stringify(payload.history))
  form.append('enable_tts', String(payload.enable_tts ?? true))
  return api.post<ResumeAssistantResponse>('/resume/assistant', form)
}
