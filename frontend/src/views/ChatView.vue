<template>
  <div class="min-h-screen bg-slate-100 flex flex-col">
    <header class="bg-white border-b shadow-sm p-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-sky-700">大学生成长情绪 Agent</h1>
      <span class="text-xs text-slate-500">会话 {{ sid.slice(0, 8) }}</span>
    </header>

    <div ref="container" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div
        v-for="message in msgs"
        :key="message.id"
        :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-[80%] p-3 rounded-2xl shadow-sm',
            message.role === 'user' ? 'bg-sky-100 text-slate-900' : 'bg-white text-slate-900'
          ]"
        >
          <div class="flex items-center gap-2 mb-1">
            <span
              v-if="message.role === 'user' && message.contentType === 'audio'"
              class="text-[11px] px-2 py-0.5 rounded-full bg-sky-200 text-sky-800"
            >
              语音输入
            </span>
            <span class="text-[11px] text-slate-400">{{ formatTime(message.createdAt) }}</span>
          </div>

          <p class="text-sm whitespace-pre-wrap leading-6">{{ message.content }}</p>

          <a
            v-if="message.role === 'assistant' && shouldShowEbtiLink(message.content)"
            href="/ebti-test/index.html"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-3 inline-flex items-center rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-amber-600"
          >
            开始 EBTI 测试
          </a>

          <div v-if="message.role === 'assistant' && message.ttsAudioUrl" class="mt-3">
            <audio :src="message.ttsAudioUrl" controls preload="none" class="w-full h-10"></audio>
          </div>

          <span v-if="message.role === 'user' && message.emotionLabel" class="text-xs text-slate-500 mt-2 block">
            情绪 {{ message.emotionLabel }}
            <template v-if="typeof message.emotionConf === 'number'">
              ({{ (message.emotionConf * 100).toFixed(0) }}%)
            </template>
          </span>
        </div>
      </div>
    </div>

    <div class="bg-white p-4 border-t flex gap-2">
      <button
        @click="toggleRec"
        :class="[
          'px-4 py-2 rounded-lg text-white transition min-w-24',
          rec ? 'bg-red-500 animate-pulse' : 'bg-slate-700'
        ]"
      >
        {{ rec ? '停止录音' : '开始录音' }}
      </button>
      <input
        v-model="txt"
        placeholder="输入文字，或点击录音说话"
        class="flex-1 px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-sky-200"
        @keyup.enter="sendTxt"
      />
      <button @click="sendTxt" class="px-4 py-2 bg-sky-600 text-white rounded-lg">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'

import { getHistory, sendChat } from '../api/chat'

type Role = 'user' | 'assistant'
type ContentType = 'text' | 'audio'

interface ViewMessage {
  id: string | number
  role: Role
  content: string
  contentType: ContentType
  emotionLabel?: string | null
  emotionConf?: number | null
  ttsAudioUrl?: string | null
  createdAt: string
}

const TARGET_SAMPLE_RATE = 16000
const APP_TIME_ZONE = 'Asia/Shanghai'
const EBTI_LINK_PATTERN = /(\/ebti-test\/|\/ebti-test\/index\.html|EBTI 测试|开始 EBTI|测一测 EBTI|人格测试)/

const msgs = ref<ViewMessage[]>([])
const txt = ref('')
const rec = ref(false)
const sid = ref(localStorage.getItem('sid') || crypto.randomUUID())
const container = ref<HTMLElement>()

let recorder: MediaRecorder | null = null
let chunks: Blob[] = []
let mediaStream: MediaStream | null = null
let currentAudio: HTMLAudioElement | null = null

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  void loadHistory()
})

const toggleRec = async () => {
  if (!rec.value) {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm'

    recorder = new MediaRecorder(mediaStream, { mimeType })
    recorder.ondataavailable = event => chunks.push(event.data)
    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: mimeType })
      chunks = []
      mediaStream?.getTracks().forEach(track => track.stop())
      const wavBlob = await convertToWav(blob)
      await submitAudio(wavBlob)
    }
    recorder.start()
    rec.value = true
    return
  }

  recorder?.stop()
  rec.value = false
}

const convertToWav = async (blob: Blob): Promise<Blob> => {
  const arrayBuffer = await blob.arrayBuffer()
  const audioContext = new AudioContext()

  try {
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer.slice(0))
    const monoData = mixToMono(audioBuffer)
    const resampled = resampleAudio(monoData, audioBuffer.sampleRate, TARGET_SAMPLE_RATE)
    const wavBuffer = encodeWav(resampled, TARGET_SAMPLE_RATE)
    return new Blob([wavBuffer], { type: 'audio/wav' })
  } finally {
    await audioContext.close()
  }
}

const mixToMono = (buffer: AudioBuffer): Float32Array => {
  if (buffer.numberOfChannels === 1) {
    return buffer.getChannelData(0).slice()
  }

  const mono = new Float32Array(buffer.length)
  for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
    const channelData = buffer.getChannelData(channel)
    for (let i = 0; i < buffer.length; i += 1) {
      mono[i] += channelData[i] / buffer.numberOfChannels
    }
  }
  return mono
}

const resampleAudio = (input: Float32Array, inputRate: number, targetRate: number): Float32Array => {
  if (inputRate === targetRate) {
    return input
  }

  const outputLength = Math.round(input.length * targetRate / inputRate)
  const output = new Float32Array(outputLength)
  const ratio = inputRate / targetRate

  for (let i = 0; i < outputLength; i += 1) {
    const position = i * ratio
    const left = Math.floor(position)
    const right = Math.min(left + 1, input.length - 1)
    const weight = position - left
    output[i] = input[left] * (1 - weight) + input[right] * weight
  }

  return output
}

const encodeWav = (samples: Float32Array, sampleRate: number): ArrayBuffer => {
  const numChannels = 1
  const format = 1
  const bitDepth = 16
  const bytesPerSample = bitDepth / 8
  const blockAlign = numChannels * bytesPerSample
  const byteRate = sampleRate * blockAlign
  const dataSize = samples.length * bytesPerSample
  const totalSize = 44 + dataSize

  const arrayBuffer = new ArrayBuffer(totalSize)
  const view = new DataView(arrayBuffer)

  const writeString = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i += 1) {
      view.setUint8(offset + i, value.charCodeAt(i))
    }
  }

  writeString(0, 'RIFF')
  view.setUint32(4, totalSize - 8, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, format, true)
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, byteRate, true)
  view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitDepth, true)
  writeString(36, 'data')
  view.setUint32(40, dataSize, true)

  let offset = 44
  for (let i = 0; i < samples.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
    offset += 2
  }

  return arrayBuffer
}

const sendTxt = () => {
  const content = txt.value.trim()
  if (!content) return
  txt.value = ''
  void submitText(content)
}

const submitAudio = async (blob: Blob) => {
  const form = new FormData()
  form.append('audio', blob, 'rec.wav')
  form.append('session_id', sid.value)
  await send(form)
}

const submitText = async (content: string) => {
  const form = new FormData()
  form.append('text', content)
  form.append('session_id', sid.value)
  await send(form)
}

const send = async (form: FormData) => {
  const { data } = await sendChat(form)
  const isAudio = form.get('audio') !== null

  msgs.value.push({
    id: `user-${data.user_created_at}`,
    role: 'user',
    content: data.user_text || String(form.get('text') || ''),
    contentType: isAudio ? 'audio' : 'text',
    emotionLabel: data.emotion.label,
    emotionConf: data.emotion.confidence,
    createdAt: data.user_created_at
  })

  msgs.value.push({
    id: `assistant-${data.assistant_created_at}`,
    role: 'assistant',
    content: data.text,
    contentType: 'text',
    ttsAudioUrl: data.tts_audio_url,
    createdAt: data.assistant_created_at
  })

  await scrollToBottom()
  await playAssistantAudio(data.tts_audio_url)
}

const loadHistory = async () => {
  const { data } = await getHistory(sid.value)
  msgs.value = data.map((item: any) => ({
    id: item.id,
    role: item.role,
    content: item.content,
    contentType: item.content_type,
    emotionLabel: item.emotion_label,
    emotionConf: item.emotion_conf,
    ttsAudioUrl: item.tts_audio_url,
    createdAt: item.created_at
  }))
  await scrollToBottom()
}

const playAssistantAudio = async (url?: string | null) => {
  if (!url) return

  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
  }

  try {
    currentAudio = new Audio(url)
    await currentAudio.play()
  } catch {
    currentAudio = null
  }
}

const formatTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: APP_TIME_ZONE,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(date)
}

const shouldShowEbtiLink = (content: string) => EBTI_LINK_PATTERN.test(content)

const scrollToBottom = async () => {
  await nextTick()
  container.value?.scrollTo({ top: container.value.scrollHeight, behavior: 'smooth' })
}
</script>
