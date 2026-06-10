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

export const polishResumeText = (payload: ResumePolishRequest) =>
  api.post<ResumePolishResponse>('/resume/polish', payload)

export const analyzeResumeMatch = (payload: ResumeAnalyzeRequest) =>
  api.post<ResumeAnalyzeResponse>('/resume/analyze', payload)
