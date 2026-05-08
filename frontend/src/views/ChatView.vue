<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <header class="bg-white shadow p-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-blue-600">🎓 学生情感语音Agent</h1>
      <span class="text-xs text-gray-500">会话: {{ sid.slice(0,8) }}</span>
    </header>

    <div ref="container" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div v-for="(m, idx) in msgs" :key="idx" :class="['flex', m.role==='user'?'justify-end':'justify-start']">
        <div :class="['max-w-[75%] p-3 rounded-xl shadow', m.role==='user'?'bg-blue-100':'bg-white']">
          <p class="text-sm whitespace-pre-wrap">{{ m.content }}</p>
          <p v-if="m.role==='user' && m.user_text" class="text-xs text-gray-400 mt-1 italic">识别: {{ m.user_text }}</p>
          <div v-if="m.role==='assistant' && m.tts_audio_url" class="mt-2">
            <audio :src="m.tts_audio_url" controls class="w-full h-8"></audio>
          </div>
          <span v-if="m.emotion_label" class="text-xs text-gray-500 mt-1 block">🎭 {{ m.emotion_label }} ({{ (m.emotion_conf*100).toFixed(0) }}%)</span>
        </div>
      </div>
    </div>

    <div class="bg-white p-4 border-t flex gap-2">
      <button @click="toggleRec" :class="['px-4 py-2 rounded-lg text-white transition', rec?'bg-red-500 animate-pulse':'bg-gray-600']">
        {{ rec?'⏹ 停止':'🎤 录音' }}
      </button>
      <input v-model="txt" placeholder="输入文字或按Enter发送..." class="flex-1 px-4 py-2 border rounded-lg" @keyup.enter="sendTxt" />
      <button @click="sendTxt" class="px-4 py-2 bg-blue-600 text-white rounded-lg">发送</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { sendChat, getHistory } from '../api/chat'

const msgs = ref<any[]>([])
const txt = ref('')
const rec = ref(false)
const sid = ref(localStorage.getItem('sid') || crypto.randomUUID())
const container = ref<HTMLElement>()
let recorder: MediaRecorder | null = null
let chunks: Blob[] = []
let audioContext: AudioContext | null = null
let mediaStream: MediaStream | null = null

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  loadHistory()
})

const toggleRec = async () => {
  if (!rec.value) {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm'
    recorder = new MediaRecorder(mediaStream, { mimeType })
    recorder.ondataavailable = e => chunks.push(e.data)
    recorder.onstop = async () => { 
      const b = new Blob(chunks, { type: 'audio/webm' }); 
      chunks = []; 
      mediaStream?.getTracks().forEach(t => t.stop())
      const wavBlob = await convertToWav(b)
      submitAudio(wavBlob)
    }
    recorder.start(); rec.value = true
  } else { recorder?.stop(); rec.value = false }
}

const convertToWav = async (blob: Blob): Promise<Blob> => {
  const arrayBuffer = await blob.arrayBuffer()
  audioContext = new AudioContext()
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
  const wavBuffer = audioBufferToWav(audioBuffer)
  return new Blob([wavBuffer], { type: 'audio/wav' })
}

const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
  const numChannels = 1
  const sampleRate = 16000
  const format = 1
  const bitDepth = 16
  const bytesPerSample = bitDepth / 8
  const blockAlign = numChannels * bytesPerSample
  const byteRate = sampleRate * blockAlign
  const dataSize = buffer.length * bytesPerSample
  const headerSize = 44
  const totalSize = headerSize + dataSize
  
  const arrayBuffer = new ArrayBuffer(totalSize)
  const view = new DataView(arrayBuffer)
  
  const writeString = (offset: number, str: string) => { for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i)) }
  writeString(0, 'RIFF'); view.setUint32(4, totalSize - 8, true)
  writeString(8, 'WAVE'); writeString(12, 'fmt ')
  view.setUint32(16, 16, true); view.setUint16(20, format, true)
  view.setUint16(22, numChannels, true); view.setUint32(24, sampleRate, true)
  view.setUint32(28, byteRate, true); view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitDepth, true); writeString(36, 'data')
  view.setUint32(40, dataSize, true)
  
  const channelData = buffer.getChannelData(0)
  let offset = 44
  for (let i = 0; i < channelData.length; i++) {
    const sample = Math.max(-1, Math.min(1, channelData[i]))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true)
    offset += 2
  }
  return arrayBuffer
}

const sendTxt = () => { if(!txt.value) return; submitText(txt.value); txt.value=''; }
const submitAudio = async (b: Blob) => { const f=new FormData(); f.append('audio', b, 'rec.wav'); f.append('session_id', sid.value); await send(f); }
const submitText = async (t: string) => { const f=new FormData(); f.append('text', t); f.append('session_id', sid.value); await send(f); }

const send = async (f: FormData) => {
  const { data } = await sendChat(f)
  const isAudio = f.get('audio') !== null
  msgs.value.push({ role:'user', content: isAudio ? '🎤 语音' : String(f.get('text')), user_text: data.user_text || '', emotion_label: data.emotion.label, emotion_conf: data.emotion.confidence })
  msgs.value.push({ role:'assistant', content: data.text, tts_audio_url: data.tts_audio_url })
  scrollToBottom()
}

const loadHistory = async () => {
  const { data } = await getHistory(sid.value)
  msgs.value = data.reverse()
  scrollToBottom()
}

const scrollToBottom = async () => { await nextTick(); container.value?.scrollTo({ top: container.value.scrollHeight, behavior:'smooth' }); }
</script>