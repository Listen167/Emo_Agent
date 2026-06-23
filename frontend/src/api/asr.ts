import axios from 'axios'

import { LOCAL_ASR_BASE_URL } from './client'

export interface ASRTranscribeResponse {
  text: string
}

const localAsrClient = axios.create({
  baseURL: LOCAL_ASR_BASE_URL,
  timeout: 120000,
})

export const transcribeLocalAudio = (audio: Blob) => {
  const form = new FormData()
  form.append('audio', audio, 'recording.wav')
  return localAsrClient.post<ASRTranscribeResponse>('/asr/transcribe', form)
}
