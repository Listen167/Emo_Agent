<template>
  <div class="chat-journal">
    <header class="journal-header">
      <div>
        <span class="kodak-chip">Kodak Portra 400</span>
        <h1 class="script-title">Film Journal</h1>
        <p>阳光正好，海风温柔。和小曦记录今天这一次快门的心跳。</p>
      </div>
      <div class="xiaoxi-status" :aria-label="`小曦当前表情：${currentXiaoxiAvatar.label}`">
        <img :src="currentXiaoxiAvatar.src" :alt="currentXiaoxiAvatar.alt" />
        <div>
          <span>XIAO XI</span>
          <strong>{{ currentXiaoxiAvatar.label }}</strong>
          <small>{{ currentXiaoxiAvatar.note }}</small>
        </div>
      </div>
      <div class="session-stamp">
        <span>SESSION</span>
        <strong>{{ sid.slice(0, 8) }}</strong>
      </div>
    </header>

    <div ref="container" class="message-board">
      <div
        v-for="message in msgs"
        :key="message.id"
        :class="['message-row', message.role === 'user' ? 'user-row' : 'assistant-row']"
      >
        <div v-if="message.role === 'assistant'" class="xiaoxi-avatar-wrap">
          <img
            class="xiaoxi-avatar"
            :src="getXiaoxiAvatar(message.avatarEmotion).src"
            :alt="getXiaoxiAvatar(message.avatarEmotion).alt"
          />
        </div>
        <div
          :class="[
            'message-card',
            message.role === 'user'
              ? 'user-card'
              : message.contentType === 'error'
                ? 'error-card'
                : 'assistant-card',
          ]"
        >
          <span class="message-tape"></span>
          <div class="message-meta">
            <span>{{ message.role === 'user' ? 'My Shot' : 'Xiao Xi' }}</span>
            <time>{{ formatMessageTime(message.createdAt) }}</time>
          </div>
          <p class="message-content" v-text="message.content" />
          <a
            v-if="message.contentType === 'text' && isUrl(message.content)"
            :href="message.content"
            target="_blank"
            class="message-link"
          >
            {{ message.content }}
          </a>

          <div v-if="message.role === 'assistant' && message.ttsAudioUrl" class="audio-strip">
            <audio :src="resolveAssetUrl(message.ttsAudioUrl)" controls preload="none"></audio>
          </div>

          <span v-if="message.role === 'user' && message.emotionLabel" class="emotion-stamp">
            情绪 {{ message.emotionLabel }}
            <template v-if="typeof message.emotionConf === 'number'">
              · {{ formatEmotionConfidence(message.emotionConf) }}
            </template>
          </span>
        </div>
      </div>
      <div v-if="msgs.length === 0" class="empty-note">
        <img class="empty-xiaoxi" :src="currentXiaoxiAvatar.src" :alt="currentXiaoxiAvatar.alt" />
        <span class="stamp-outline">NEW ROLL</span>
        <h2>今天想记录什么？</h2>
        <p>输入文字或按下语音，把这一刻贴进你的胶片日记。</p>
      </div>
    </div>

    <footer class="composer-wrap">
      <div class="composer">
        <textarea
          v-model="text"
          class="composer-input"
          rows="2"
          placeholder="说点什么..."
          @keydown.enter.exact.prevent="send"
        />
        <button
          :disabled="sending || !text.trim()"
          class="send-btn"
          @click="send"
        >
          {{ sending ? '发送中...' : '发送' }}
        </button>
        <button
          :class="['record-btn', { recording: rec }]"
          @click="toggleRec"
        >
          {{ rec ? '停止' : '语音' }}
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'

import { getHistory, sendChat } from '../api/chat'
import { resolveAssetUrl } from '../api/client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  contentType: 'text' | 'error'
  emotionLabel?: string | null
  emotionConf?: number | null
  ttsAudioUrl?: string | null
  avatarEmotion?: XiaoxiAvatarKey | null
  createdAt: string
}

const xiaoxiAvatars = {
  usual: {
    src: '/xiaoxi/usual.png',
    label: '日常陪伴',
    note: '安静听你说',
    alt: '小曦日常表情',
  },
  happy: {
    src: '/xiaoxi/happy.png',
    label: '开心回应',
    note: '一起接住好心情',
    alt: '小曦开心表情',
  },
  comfort: {
    src: '/xiaoxi/comfort.png',
    label: '温柔安慰',
    note: '慢慢来，我在',
    alt: '小曦安慰表情',
  },
  angry: {
    src: '/xiaoxi/angry.png',
    label: '认真站队',
    note: '先把问题说清楚',
    alt: '小曦生气表情',
  },
  shy: {
    src: '/xiaoxi/shy.png',
    label: '害羞惊喜',
    note: '有点意外呢',
    alt: '小曦害羞表情',
  },
  think: {
    src: '/xiaoxi/think.png',
    label: '认真思考',
    note: '正在整理回答',
    alt: '小曦思考表情',
  },
  naughty: {
    src: '/xiaoxi/naughty.png',
    label: '俏皮互动',
    note: '给今天加点灵感',
    alt: '小曦俏皮表情',
  },
} as const

type XiaoxiAvatarKey = keyof typeof xiaoxiAvatars

const TARGET_SAMPLE_RATE = 16000
const sid = ref(localStorage.getItem('sid') || crypto.randomUUID())
const msgs = ref<Message[]>([])
const text = ref('')
const container = ref<HTMLElement>()
const sending = ref(false)
const rec = ref(false)
const currentAvatarKey = ref<XiaoxiAvatarKey>('usual')
let mediaStream: MediaStream | null = null
let recorder: MediaRecorder | null = null
let currentAudio: HTMLAudioElement | null = null

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  loadHistory()
})

const isUrl = (str: string) => /^https?:\/\//.test(str)
const currentXiaoxiAvatar = computed(() => xiaoxiAvatars[currentAvatarKey.value])

const getXiaoxiAvatar = (key?: XiaoxiAvatarKey | null) => xiaoxiAvatars[key ?? 'usual']

const getAvatarKeyByEmotion = (label?: string | null): XiaoxiAvatarKey => {
  const normalized = (label || '').toLowerCase()
  if (normalized.includes('happy') || normalized.includes('开心') || normalized.includes('高兴')) return 'happy'
  if (normalized.includes('sad') || normalized.includes('难过') || normalized.includes('悲伤')) return 'comfort'
  if (normalized.includes('anxious') || normalized.includes('焦虑') || normalized.includes('紧张')) return 'comfort'
  if (normalized.includes('angry') || normalized.includes('生气') || normalized.includes('愤怒')) return 'angry'
  if (normalized.includes('surprised') || normalized.includes('惊讶') || normalized.includes('意外')) return 'shy'
  if (normalized.includes('neutral') || normalized.includes('平静')) return 'usual'
  return 'usual'
}

const formatEmotionConfidence = (value: number) => `${Math.round(value * 100)}%`
const formatMessageTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(date)
}

const send = async () => {
  const msg = text.value.trim()
  if (!msg) return

  msgs.value.push({
    id: crypto.randomUUID(),
    role: 'user',
    content: msg,
    contentType: 'text',
    createdAt: new Date().toISOString()
  })
  text.value = ''
  sending.value = true
  currentAvatarKey.value = 'think'
  await scrollToBottom()

  try {
    const form = new FormData()
    form.append('text', msg)
    form.append('session_id', sid.value)
    const { data } = await sendChat(form)
    handleResponse(data)
  } catch {
    currentAvatarKey.value = 'comfort'
    msgs.value.push({
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '发送失败，请重试',
      contentType: 'error',
      avatarEmotion: 'comfort',
      createdAt: new Date().toISOString()
    })
  } finally {
    sending.value = false
  }
}

const toggleRec = async () => {
  if (rec.value) {
    recorder?.stop()
    rec.value = false
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const chunks: Blob[] = []
    recorder = new MediaRecorder(mediaStream)
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data) }
    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/webm' })
      chunks.length = 0
      mediaStream?.getTracks().forEach(track => track.stop())
      const wavBlob = await convertToWav(blob)
      await submitAudio(wavBlob)
    }
    recorder.start()
    rec.value = true
  } catch {
    rec.value = false
  }
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
    audioContext.close()
  }
}

const mixToMono = (buffer: AudioBuffer): Float32Array => {
  const length = buffer.length
  const result = new Float32Array(length)
  for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
    const data = buffer.getChannelData(ch)
    for (let i = 0; i < length; i++) result[i] += data[i]
  }
  for (let i = 0; i < length; i++) result[i] /= buffer.numberOfChannels
  return result
}

const resampleAudio = (data: Float32Array, fromRate: number, toRate: number): Float32Array => {
  if (fromRate === toRate) return data
  const ratio = fromRate / toRate
  const newLength = Math.round(data.length / ratio)
  const result = new Float32Array(newLength)
  for (let i = 0; i < newLength; i++) {
    const srcIdx = i * ratio
    const srcIdxFloor = Math.floor(srcIdx)
    const srcIdxCeil = Math.min(srcIdxFloor + 1, data.length - 1)
    const t = srcIdx - srcIdxFloor
    result[i] = data[srcIdxFloor] * (1 - t) + data[srcIdxCeil] * t
  }
  return result
}

const encodeWav = (samples: Float32Array, sampleRate: number): ArrayBuffer => {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
  }
  writeString(0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, samples.length * 2, true)
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
  }
  return buffer
}

const submitAudio = async (wavBlob: Blob) => {
  const form = new FormData()
  form.append('audio', wavBlob, 'recording.wav')
  form.append('session_id', sid.value)
  currentAvatarKey.value = 'think'
  try {
    const { data } = await sendChat(form)
    handleResponse(data)
  } catch {
    currentAvatarKey.value = 'comfort'
    msgs.value.push({
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '语音发送失败',
      contentType: 'error',
      avatarEmotion: 'comfort',
      createdAt: new Date().toISOString()
    })
  }
}

const handleResponse = (data: any) => {
  const emotionLabel = syncUserMessage(data)
  const avatarEmotion = getAvatarKeyByEmotion(emotionLabel)
  currentAvatarKey.value = avatarEmotion
  msgs.value.push({
    id: crypto.randomUUID(),
    role: 'assistant',
    content: data.text,
    contentType: 'text',
    avatarEmotion,
    ttsAudioUrl: data.tts_audio_url,
    createdAt: data.assistant_created_at
  })
  scrollToBottom()
  playAssistantAudio(data.tts_audio_url)
}

const syncUserMessage = (data: any): string | null => {
  const emotion = data?.emotion || {}
  const label = typeof emotion.label === 'string' ? emotion.label : null
  const confidence = typeof emotion.confidence === 'number' ? emotion.confidence : null
  const userText = typeof data?.user_text === 'string' ? data.user_text.trim() : ''

  for (let index = msgs.value.length - 1; index >= 0; index -= 1) {
    const message = msgs.value[index]
    if (message.role !== 'user') continue
    if (message.emotionLabel == null && message.emotionConf == null) {
      message.emotionLabel = label
      message.emotionConf = confidence
    }
    if (!message.content.trim() && userText) {
      message.content = userText
    }
    return label
  }

  if (userText) {
    msgs.value.push({
      id: crypto.randomUUID(),
      role: 'user',
      content: userText,
      contentType: 'text',
      emotionLabel: label,
      emotionConf: confidence,
      createdAt: data?.user_created_at || new Date().toISOString(),
    })
  }
  return label
}

const loadHistory = async () => {
  try {
    const { data } = await getHistory(sid.value)
    let lastUserEmotion: string | null = null
    const loaded = (data || []).map((item: any) => {
      const role = item.role === 'assistant' ? 'assistant' : 'user'
      const message: Message = {
        id: crypto.randomUUID(),
        role,
        content: item.content,
        contentType: item.content_type,
        emotionLabel: item.emotion_label,
        emotionConf: item.emotion_conf,
        ttsAudioUrl: item.tts_audio_url,
        avatarEmotion: role === 'assistant' ? getAvatarKeyByEmotion(lastUserEmotion) : null,
        createdAt: item.created_at
      }
      if (role === 'user') {
        lastUserEmotion = typeof item.emotion_label === 'string' ? item.emotion_label : null
      }
      return message
    })
    msgs.value = loaded
    const latestAssistant = [...loaded].reverse().find(message => message.role === 'assistant' && message.avatarEmotion)
    currentAvatarKey.value = latestAssistant?.avatarEmotion || 'usual'
  } catch { /* ignore */ }
  await scrollToBottom()
}

const playAssistantAudio = async (url?: string | null) => {
  if (!url) return
  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
  }
  try {
    currentAudio = new Audio(resolveAssetUrl(url))
    await currentAudio.play()
  } catch {
    currentAudio = null
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (container.value) {
    container.value.scrollTop = container.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-journal {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 26px 30px 22px;
  overflow: hidden;
}

.journal-header {
  position: relative;
  flex: 0 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px 22px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.journal-header::after {
  content: "";
  position: absolute;
  right: 42px;
  top: -14px;
  width: 124px;
  height: 28px;
  rotate: 5deg;
  background: rgb(232 195 108 / 56%);
  border: 1px solid rgb(62 50 40 / 10%);
}

.kodak-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.journal-header h1 {
  margin: 8px 0 0;
  font-size: clamp(44px, 6vw, 76px);
  line-height: 0.95;
}

.journal-header p {
  margin: 8px 0 0;
  max-width: 640px;
  color: var(--journal-muted);
  font-size: 14px;
}

.session-stamp {
  align-self: center;
  min-width: 124px;
  padding: 14px;
  border: 2px solid var(--journal-stamp);
  border-radius: 999px;
  color: var(--journal-stamp);
  text-align: center;
  rotate: -5deg;
}

.session-stamp span,
.session-stamp strong {
  display: block;
}

.session-stamp span {
  font-size: 11px;
}

.xiaoxi-status {
  align-self: center;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 230px;
  padding: 10px 14px 10px 10px;
  border: 1px solid rgb(62 50 40 / 15%);
  background:
    linear-gradient(135deg, rgb(255 255 255 / 78%), rgb(255 241 205 / 40%));
  box-shadow: 0 14px 30px rgb(62 50 40 / 12%);
}

.xiaoxi-status img {
  width: 76px;
  height: 76px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: drop-shadow(0 8px 10px rgb(62 50 40 / 18%));
}

.xiaoxi-status span,
.xiaoxi-status strong,
.xiaoxi-status small {
  display: block;
}

.xiaoxi-status span {
  color: var(--journal-stamp);
  font-size: 11px;
  font-weight: 700;
}

.xiaoxi-status strong {
  margin-top: 4px;
  color: var(--journal-ink);
  font-size: 16px;
}

.xiaoxi-status small {
  margin-top: 3px;
  color: var(--journal-muted);
  font-size: 11px;
}

.message-board {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 28px 8px 24px;
}

.message-board::-webkit-scrollbar {
  width: 8px;
}

.message-board::-webkit-scrollbar-thumb {
  background: rgb(62 50 40 / 22%);
  border-radius: 999px;
}

.message-row {
  display: flex;
  margin-bottom: 20px;
}

.user-row {
  justify-content: flex-end;
}

.assistant-row {
  align-items: flex-start;
  gap: 12px;
  justify-content: flex-start;
}

.xiaoxi-avatar-wrap {
  position: relative;
  flex: 0 0 72px;
  width: 72px;
  height: 72px;
  display: grid;
  place-items: center;
  margin-top: 2px;
  border: 1px solid rgb(62 50 40 / 13%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 12px 24px rgb(62 50 40 / 13%);
  rotate: -2deg;
}

.xiaoxi-avatar-wrap::after {
  content: "";
  position: absolute;
  top: -7px;
  left: 18px;
  width: 34px;
  height: 13px;
  rotate: -5deg;
  background: rgb(232 195 108 / 54%);
  border: 1px solid rgb(62 50 40 / 8%);
}

.xiaoxi-avatar {
  width: 70px;
  height: 70px;
  object-fit: contain;
  filter: drop-shadow(0 5px 8px rgb(62 50 40 / 16%));
}

.message-card {
  position: relative;
  max-width: min(720px, 82%);
  padding: 18px 20px 16px;
  border: 1px solid rgb(62 50 40 / 16%);
  box-shadow: 0 14px 30px rgb(62 50 40 / 13%);
  clip-path: polygon(0 2%, 98% 0, 100% 96%, 2% 100%);
}

.assistant-card {
  background: #fff8e8;
}

.user-card {
  background:
    linear-gradient(135deg, rgb(232 195 108 / 58%), rgb(255 248 232 / 92%));
}

.error-card {
  background: rgb(255 231 224);
  color: #8f2f2a;
}

.message-tape {
  position: absolute;
  top: -11px;
  left: 26px;
  width: 92px;
  height: 22px;
  rotate: -3deg;
  background: rgb(232 195 108 / 52%);
  border: 1px solid rgb(62 50 40 / 9%);
}

.user-card .message-tape {
  left: auto;
  right: 26px;
  rotate: 4deg;
  background: rgb(255 255 255 / 44%);
}

.message-meta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.message-content {
  margin: 0;
  white-space: pre-wrap;
  color: var(--journal-ink);
  font-size: 15px;
  line-height: 1.8;
}

.message-link {
  display: inline-block;
  margin-top: 8px;
  color: var(--journal-stamp);
  font-size: 12px;
  text-decoration: underline;
}

.audio-strip {
  margin-top: 14px;
  padding: 8px;
  border-radius: 8px;
  background: #211711;
}

.audio-strip audio {
  width: 100%;
  height: 36px;
}

.emotion-stamp {
  display: inline-flex;
  margin-top: 12px;
  padding: 5px 9px;
  border: 1px solid var(--journal-stamp);
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
  rotate: -2deg;
}

.empty-note {
  width: min(520px, 92%);
  margin: 60px auto 0;
  padding: 32px;
  text-align: center;
  border: 1px dashed rgb(62 50 40 / 28%);
  background: rgb(255 248 232 / 62%);
}

.empty-xiaoxi {
  display: block;
  width: 136px;
  height: 136px;
  margin: -8px auto 14px;
  object-fit: contain;
  filter: drop-shadow(0 12px 18px rgb(62 50 40 / 16%));
}

.stamp-outline {
  display: inline-block;
  padding: 8px 12px;
  border: 2px solid var(--journal-stamp);
  border-radius: 999px;
  color: var(--journal-stamp);
  font-weight: 700;
  rotate: -5deg;
}

.empty-note h2 {
  margin: 18px 0 8px;
  font-size: 24px;
}

.empty-note p {
  margin: 0;
  color: var(--journal-muted);
}

.composer-wrap {
  flex: 0 0 auto;
  padding-top: 12px;
}

.composer {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  padding: 12px;
  border-radius: 22px;
  border: 1px solid rgb(255 255 255 / 62%);
  background:
    linear-gradient(135deg, rgb(255 255 255 / 74%), rgb(255 241 205 / 30%));
  backdrop-filter: blur(18px) saturate(145%);
  -webkit-backdrop-filter: blur(18px) saturate(145%);
  box-shadow: 0 18px 40px rgb(62 50 40 / 16%);
}

.composer-input {
  flex: 1;
  min-height: 52px;
  max-height: 150px;
  resize: vertical;
  outline: none;
  border: 1px solid rgb(62 50 40 / 16%);
  border-radius: 14px;
  padding: 12px 14px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 74%);
}

.composer-input:focus {
  border-color: rgb(200 90 84 / 46%);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
}

.send-btn,
.record-btn {
  min-height: 52px;
  border-radius: 14px;
  padding: 0 20px;
  color: #fff8e8;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 18%);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.record-btn {
  color: var(--journal-ink);
  background: var(--journal-kodak);
}

.record-btn.recording {
  color: #fff8e8;
  background: var(--journal-stamp);
}

@media (max-width: 720px) {
  .chat-journal {
    padding: 16px 14px 18px;
  }

  .journal-header {
    display: block;
    padding: 20px;
  }

  .session-stamp {
    display: none;
  }

  .xiaoxi-status {
    min-width: 0;
    margin-top: 16px;
  }

  .xiaoxi-status img {
    width: 64px;
    height: 64px;
  }

  .assistant-row {
    gap: 8px;
  }

  .xiaoxi-avatar-wrap {
    flex-basis: 54px;
    width: 54px;
    height: 54px;
  }

  .xiaoxi-avatar {
    width: 52px;
    height: 52px;
  }

  .message-card {
    max-width: calc(100% - 62px);
  }

  .composer {
    display: grid;
    grid-template-columns: 1fr 82px 72px;
  }
}
</style>
