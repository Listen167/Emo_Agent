<template>
  <div class="chat-journal" @wheel="handleChatWheel">
    <header class="journal-header">
      <div class="journal-copy">
        <span class="kodak-chip">Kodak Portra 400</span>
        <h1 class="script-title">Film Journal</h1>
        <p>阳光正好，海风温柔。和小曦记录今天这一次快门的心跳。</p>
      </div>
      <div class="today-film-folder" aria-label="今日胶片夹">
        <span class="folder-tab">今日胶片夹</span>
        <div class="folder-grid">
          <div>
            <strong>{{ todayRecordCount }}</strong>
            <small>今日记录</small>
          </div>
          <div>
            <strong>{{ latestEmotionText }}</strong>
            <small>最近情绪</small>
          </div>
          <div>
            <strong>{{ unreadSuggestionCount }}</strong>
            <small>未读建议</small>
          </div>
        </div>
      </div>
      <div
        :class="['xiaoxi-status', `xiaoxi-status-${displayAvatarKey}`]"
        :aria-label="`小曦当前表情：${currentXiaoxiAvatar.label}`"
      >
        <div class="xiaoxi-avatar-stage">
          <img :src="currentXiaoxiAvatar.src" :alt="currentXiaoxiAvatar.alt" />
          <span class="xiaoxi-blink" aria-hidden="true"></span>
          <span class="xiaoxi-status-light" aria-hidden="true"></span>
        </div>
        <div>
          <span>XIAO XI</span>
          <strong>{{ currentXiaoxiAvatar.label }}</strong>
          <small>{{ currentXiaoxiAvatar.note }}</small>
          <div class="xiaoxi-memory-line">
            <em>{{ xiaoxiModeText }}</em>
            <em>{{ longMemoryCount }} 条记忆</em>
          </div>
          <button class="avatar-picker-trigger" type="button" @click="avatarPickerOpen = true">
            {{ manualAvatarKey ? '更换小曦形象' : '选择小曦形象' }}
          </button>
        </div>
      </div>
      <div class="session-stamp">
        <span>SESSION</span>
        <strong>{{ sid.slice(0, 8) }}</strong>
      </div>
    </header>

    <Transition name="avatar-dialog">
      <div
        v-if="avatarPickerOpen"
        class="avatar-picker-backdrop"
        @click.self="avatarPickerOpen = false"
      >
        <section
          class="avatar-picker-panel"
          role="dialog"
          aria-modal="true"
          aria-labelledby="avatar-picker-title"
        >
          <div class="avatar-picker-head">
            <div>
              <span class="kodak-chip">Xiao Xi Contact Sheet</span>
              <h2 id="avatar-picker-title">选择今天陪你记录的小曦</h2>
              <p>可以固定一个表情头像，也可以交给小曦根据对话情绪自动切换。</p>
            </div>
            <button class="avatar-picker-close" type="button" @click="avatarPickerOpen = false">
              关闭
            </button>
          </div>

          <button
            :class="['avatar-auto-card', { active: !manualAvatarKey }]"
            type="button"
            @click="selectAvatar(null)"
          >
            <span class="auto-lens"></span>
            <div>
              <strong>跟随情绪自动切换</strong>
              <small>聊天、空状态和顶部状态会随小曦回应自然变化。</small>
            </div>
          </button>

          <div class="avatar-option-grid">
            <button
              v-for="item in avatarOptions"
              :key="item.key"
              :class="[
                'avatar-option-card',
                `avatar-option-${item.key}`,
                { active: manualAvatarKey === item.key },
              ]"
              type="button"
              @click="selectAvatar(item.key)"
            >
              <span class="avatar-thumb-stage">
                <img :src="item.src" :alt="item.alt" />
                <i aria-hidden="true"></i>
              </span>
              <span class="avatar-option-copy">
                <strong>{{ item.label }}</strong>
                <small>{{ item.note }}</small>
                <em>{{ avatarMotionText(item.key) }}</em>
              </span>
            </button>
          </div>
        </section>
      </div>
    </Transition>

    <div ref="container" class="message-board">
      <TransitionGroup name="message-develop" tag="div" class="message-stack">
        <div
          v-for="message in msgs"
          :key="message.id"
          :class="['message-row', message.role === 'user' ? 'user-row' : 'assistant-row']"
        >
          <div
            v-if="message.role === 'assistant'"
            :class="['xiaoxi-avatar-wrap', `xiaoxi-avatar-${getMessageAvatarKey(message.avatarEmotion)}`]"
          >
            <img
              class="xiaoxi-avatar"
              :src="getXiaoxiAvatar(getMessageAvatarKey(message.avatarEmotion)).src"
              :alt="getXiaoxiAvatar(getMessageAvatarKey(message.avatarEmotion)).alt"
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
      </TransitionGroup>
      <div v-if="sending" class="thinking-strip" aria-live="polite">
        <span class="thinking-dot"></span>
        <span class="thinking-dot"></span>
        <span class="thinking-dot"></span>
        <small>小曦正在显影这一帧</small>
      </div>
      <div v-if="msgs.length === 0" class="empty-note">
        <img
          :class="['empty-xiaoxi', `empty-xiaoxi-${displayAvatarKey}`]"
          :src="currentXiaoxiAvatar.src"
          :alt="currentXiaoxiAvatar.alt"
        />
        <span class="stamp-outline">NEW ROLL</span>
        <h2>今天想记录什么？</h2>
        <p>输入文字或按下语音，把这一刻贴进你的胶片日记。</p>
        <button class="empty-avatar-switch" type="button" @click="avatarPickerOpen = true">
          当前小曦：{{ currentXiaoxiAvatar.label }} · 更换
        </button>
      </div>
    </div>

    <footer class="composer-wrap">
      <div :class="['composer', { 'composer-recording': rec, 'composer-sending': sending }]">
        <textarea
          v-model="text"
          class="composer-input"
          rows="2"
          placeholder="说点什么..."
          @keydown.enter.exact.prevent="send"
        />
        <button
          :disabled="sending || !text.trim()"
          :class="['send-btn', { loading: sending }]"
          @click="send"
        >
          <span class="button-shutter"></span>
          {{ sending ? '发送中...' : '发送' }}
        </button>
        <button
          :class="['record-btn', { recording: rec }]"
          @click="toggleRec"
        >
          <span class="record-wave" aria-hidden="true">
            <i></i>
            <i></i>
            <i></i>
            <i></i>
          </span>
          {{ rec ? '停止' : '语音' }}
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import { getChatStreamUrl, getHistory, sendChat } from '../api/chat'
import { resolveAssetUrl } from '../api/client'
import { createClientId } from '../utils/id'

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
const sid = ref(localStorage.getItem('sid') || createClientId())
const msgs = ref<Message[]>([])
const text = ref('')
const container = ref<HTMLElement>()
const sending = ref(false)
const rec = ref(false)
const currentAvatarKey = ref<XiaoxiAvatarKey>('usual')
const storedAvatarKey = localStorage.getItem('u-life-xiaoxi-avatar-key-v1')
const manualAvatarKey = ref<XiaoxiAvatarKey | null>(
  isXiaoxiAvatarKey(storedAvatarKey) ? storedAvatarKey : null
)
const avatarPickerOpen = ref(false)
const xiaoxiMode = ref(localStorage.getItem('u-life-xiaoxi-personality-v1') || 'warm')
const longMemoryCount = ref(getLongMemoryCount())
let mediaStream: MediaStream | null = null
let recorder: MediaRecorder | null = null
let currentAudio: HTMLAudioElement | null = null
let streamAudio: HTMLAudioElement | null = null
let mediaSource: MediaSource | null = null
let sourceBuffer: SourceBuffer | null = null
let pendingAudioChunks: Uint8Array[] = []
let mediaSourceReady = false

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  loadHistory()
  window.addEventListener('u-life-settings-changed', syncGrowthSettings)
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('u-life-settings-changed', syncGrowthSettings)
  window.removeEventListener('keydown', handleGlobalKeydown)
  resetStreamAudio()
})

const isUrl = (str: string) => /^https?:\/\//.test(str)
const avatarOptions = computed(() =>
  (Object.keys(xiaoxiAvatars) as XiaoxiAvatarKey[]).map(key => ({
    key,
    ...xiaoxiAvatars[key],
  }))
)
const displayAvatarKey = computed(() => manualAvatarKey.value || currentAvatarKey.value)
const currentXiaoxiAvatar = computed(() => xiaoxiAvatars[displayAvatarKey.value])
const xiaoxiModeText = computed(() => {
  const map: Record<string, string> = {
    warm: '温柔陪伴型',
    coach: '成长教练型',
    rational: '理性分析型',
    bright: '元气鼓励型',
  }
  return map[xiaoxiMode.value] || '温柔陪伴型'
})
const shanghaiDayFormatter = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Shanghai',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})
const isTodayMessage = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return false
  return shanghaiDayFormatter.format(date) === shanghaiDayFormatter.format(new Date())
}
const todayUserMessages = computed(() =>
  msgs.value.filter(message => message.role === 'user' && isTodayMessage(message.createdAt))
)
const todayRecordCount = computed(() => todayUserMessages.value.length)
const latestEmotionText = computed(() => {
  const latest = [...msgs.value]
    .reverse()
    .find(message => message.role === 'user' && message.emotionLabel)
  return moodLabelText(latest?.emotionLabel) || '等待记录'
})
const unreadSuggestionCount = computed(() =>
  msgs.value.filter(message =>
    message.role === 'assistant' &&
    message.contentType === 'text' &&
    isTodayMessage(message.createdAt)
  ).length
)

const getXiaoxiAvatar = (key?: XiaoxiAvatarKey | null) => xiaoxiAvatars[key ?? 'usual']
const getMessageAvatarKey = (key?: XiaoxiAvatarKey | null) => manualAvatarKey.value || key || 'usual'

function isXiaoxiAvatarKey(value: string | null): value is XiaoxiAvatarKey {
  return Boolean(value && value in xiaoxiAvatars)
}

const selectAvatar = (key: XiaoxiAvatarKey | null) => {
  manualAvatarKey.value = key
  if (key) {
    localStorage.setItem('u-life-xiaoxi-avatar-key-v1', key)
    currentAvatarKey.value = key
  } else {
    localStorage.removeItem('u-life-xiaoxi-avatar-key-v1')
  }
  avatarPickerOpen.value = false
}

const avatarMotionText = (key: XiaoxiAvatarKey) => {
  const map: Record<XiaoxiAvatarKey, string> = {
    usual: '轻呼吸',
    happy: '轻跳跃',
    comfort: '柔和漂浮',
    angry: '快速抖动',
    shy: '侧身轻晃',
    think: '思考点头',
    naughty: '俏皮摆动',
  }
  return map[key]
}

const moodLabelText = (mood?: string | null) => {
  const map: Record<string, string> = {
    happy: '开心',
    neutral: '平静',
    anxious: '焦虑',
    sad: '难过',
    angry: '生气',
    surprised: '惊讶',
  }
  return mood ? (map[mood] || mood) : ''
}

function getLongMemoryCount() {
  try {
    const raw = localStorage.getItem('u-life-long-memory-v1')
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed.length : 0
  } catch {
    return 0
  }
}

const syncGrowthSettings = () => {
  xiaoxiMode.value = localStorage.getItem('u-life-xiaoxi-personality-v1') || 'warm'
  longMemoryCount.value = getLongMemoryCount()
}

const handleGlobalKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && avatarPickerOpen.value) {
    avatarPickerOpen.value = false
  }
}

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
    id: createClientId(),
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
    await sendTextStream(msg)
  } catch {
    currentAvatarKey.value = 'comfort'
    msgs.value.push({
      id: createClientId(),
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
      id: createClientId(),
      role: 'assistant',
      content: '语音发送失败',
      contentType: 'error',
      avatarEmotion: 'comfort',
      createdAt: new Date().toISOString()
    })
  }
}

const sendTextStream = (msg: string) => new Promise<void>((resolve, reject) => {
  const socket = new WebSocket(getChatStreamUrl())
  const assistantId = createClientId()
  let assistantCreated = false
  let streamedText = ''
  let emotionLabel: string | null = null
  const assistantMessage: Message = {
    id: assistantId,
    role: 'assistant',
    content: '',
    contentType: 'text',
    avatarEmotion: 'think',
    createdAt: new Date().toISOString()
  }

  socket.onopen = () => {
    resetStreamAudio()
    socket.send(JSON.stringify({ text: msg, session_id: sid.value }))
  }

  socket.onmessage = async (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'start') {
      emotionLabel = syncUserMessage(data)
      const avatarEmotion = getAvatarKeyByEmotion(emotionLabel)
      assistantMessage.avatarEmotion = avatarEmotion
      currentAvatarKey.value = avatarEmotion
      return
    }

    if (data.type === 'text_delta') {
      if (!assistantCreated) {
        msgs.value.push(assistantMessage)
        assistantCreated = true
      }
      streamedText += data.delta || ''
      assistantMessage.content = streamedText
      await scrollToBottom()
      return
    }

    if (data.type === 'audio_delta') {
      appendStreamAudio(base64ToBytes(data.data || ''), data.codec || 'mp3')
      return
    }

    if (data.type === 'done') {
      if (!assistantCreated) {
        msgs.value.push(assistantMessage)
        assistantCreated = true
      }
      assistantMessage.content = data.text || streamedText
      assistantMessage.ttsAudioUrl = data.tts_audio_url
      assistantMessage.createdAt = data.assistant_created_at || assistantMessage.createdAt
      currentAvatarKey.value = getAvatarKeyByEmotion(emotionLabel)
      finishStreamAudio()
      if (!mediaSource && data.tts_audio_url) playAssistantAudio(data.tts_audio_url)
      socket.close()
      resolve()
      return
    }

    if (data.type === 'error' || data.type === 'tts_error') {
      if (data.type === 'error') {
        socket.close()
        reject(new Error(data.message || '流式对话失败'))
      }
    }
  }

  socket.onerror = () => {
    reject(new Error('流式连接失败'))
  }
})

const handleResponse = (data: any) => {
  const emotionLabel = syncUserMessage(data)
  const avatarEmotion = getAvatarKeyByEmotion(emotionLabel)
  currentAvatarKey.value = avatarEmotion
  msgs.value.push({
    id: createClientId(),
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
      id: createClientId(),
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
        id: createClientId(),
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

const resetStreamAudio = () => {
  if (streamAudio) {
    streamAudio.pause()
    streamAudio = null
  }
  mediaSource = null
  sourceBuffer = null
  pendingAudioChunks = []
  mediaSourceReady = false
}

const base64ToBytes = (value: string) => {
  const binary = atob(value)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return bytes
}

const appendStreamAudio = (chunk: Uint8Array, codec: string) => {
  if (!chunk.byteLength || codec !== 'mp3' || !('MediaSource' in window)) return
  if (!mediaSource) {
    mediaSource = new MediaSource()
    streamAudio = new Audio(URL.createObjectURL(mediaSource))
    mediaSource.addEventListener('sourceopen', () => {
      if (!mediaSource) return
      try {
        sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg')
        sourceBuffer.addEventListener('updateend', flushStreamAudio)
        mediaSourceReady = true
        flushStreamAudio()
        void streamAudio?.play()
      } catch {
        resetStreamAudio()
      }
    }, { once: true })
  }
  pendingAudioChunks.push(chunk)
  flushStreamAudio()
}

const flushStreamAudio = () => {
  if (!mediaSourceReady || !sourceBuffer || sourceBuffer.updating || pendingAudioChunks.length === 0) return
  const chunk = pendingAudioChunks.shift()
  if (!chunk) return
  try {
    sourceBuffer.appendBuffer(chunk)
  } catch {
    pendingAudioChunks.unshift(chunk)
  }
}

const finishStreamAudio = () => {
  if (!mediaSource || mediaSource.readyState !== 'open') return
  const tryEnd = () => {
    if (!mediaSource || mediaSource.readyState !== 'open') return
    if (sourceBuffer?.updating || pendingAudioChunks.length > 0) {
      window.setTimeout(tryEnd, 120)
      return
    }
    try {
      mediaSource.endOfStream()
    } catch { /* ignore */ }
  }
  tryEnd()
}

const scrollToBottom = async () => {
  await nextTick()
  if (container.value) {
    container.value.scrollTop = container.value.scrollHeight
  }
}

const handleChatWheel = (event: WheelEvent) => {
  const board = container.value
  if (!board) return

  const target = event.target instanceof Element ? event.target : null
  if (target?.closest('.message-board, textarea, input, button, select, audio')) return

  event.preventDefault()
  board.scrollTop += event.deltaY
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
  flex-wrap: wrap;
  align-items: center;
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

.journal-copy {
  flex: 1 1 320px;
  min-width: 260px;
}

.today-film-folder {
  position: relative;
  align-self: center;
  min-width: 250px;
  padding: 18px 16px 14px;
  border: 1px solid rgb(62 50 40 / 15%);
  border-radius: 4px 12px 12px 12px;
  background:
    linear-gradient(180deg, rgb(255 252 242 / 86%), rgb(245 232 206 / 78%));
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 72%), 0 14px 28px rgb(62 50 40 / 10%);
}

.today-film-folder::after {
  content: "";
  position: absolute;
  inset: 7px;
  pointer-events: none;
  border: 1px dashed rgb(62 50 40 / 13%);
  border-radius: 8px;
}

.folder-tab {
  position: absolute;
  top: -14px;
  left: -1px;
  padding: 5px 12px 6px;
  border: 1px solid rgb(62 50 40 / 15%);
  border-bottom: 0;
  border-radius: 8px 8px 0 0;
  color: var(--journal-ink);
  background: #f2d98a;
  font-size: 11px;
  font-weight: 800;
}

.folder-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 0.8fr 1.2fr 0.8fr;
  gap: 8px;
}

.folder-grid div {
  min-width: 0;
  padding: 9px 7px;
  border-radius: 8px;
  background: rgb(253 251 247 / 64%);
  text-align: center;
}

.folder-grid strong,
.folder-grid small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.folder-grid strong {
  color: var(--journal-ink);
  font-size: 17px;
}

.folder-grid small {
  margin-top: 4px;
  color: var(--journal-muted);
  font-size: 10px;
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
  position: relative;
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
  animation: xiaoxiStatusBreathe 4.8s ease-in-out infinite;
}

.xiaoxi-avatar-stage {
  position: relative;
  flex: 0 0 76px;
  width: 76px;
  height: 76px;
  display: grid;
  place-items: center;
}

.xiaoxi-status img {
  width: 76px;
  height: 76px;
  object-fit: contain;
  filter: drop-shadow(0 8px 10px rgb(62 50 40 / 18%));
}

.xiaoxi-blink {
  position: absolute;
  left: 18px;
  top: 28px;
  width: 40px;
  height: 11px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgb(62 50 40 / 0%), rgb(62 50 40 / 26%));
  opacity: 0;
  transform: scaleY(0.15);
  transform-origin: 50% 50%;
  animation: xiaoxiBlink 5.6s ease-in-out infinite;
  pointer-events: none;
}

.xiaoxi-status-light {
  position: absolute;
  right: 4px;
  bottom: 8px;
  width: 11px;
  height: 11px;
  border: 2px solid rgb(255 248 232 / 88%);
  border-radius: 999px;
  background: #87a777;
  box-shadow: 0 0 0 4px rgb(135 167 119 / 18%), 0 0 12px rgb(135 167 119 / 62%);
  animation: xiaoxiStatusLight 2.4s ease-in-out infinite;
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

.xiaoxi-memory-line {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 7px;
}

.xiaoxi-memory-line em {
  padding: 3px 6px;
  border: 1px solid rgb(62 50 40 / 12%);
  border-radius: 999px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 62%);
  font-size: 10px;
  font-style: normal;
}

.avatar-picker-trigger,
.empty-avatar-switch {
  min-height: 30px;
  margin-top: 8px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  padding: 0 10px;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 72%);
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.avatar-picker-trigger:hover,
.empty-avatar-switch:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgb(62 50 40 / 10%);
}

.avatar-picker-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgb(32 21 15 / 28%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.avatar-picker-panel {
  width: min(820px, 96vw);
  max-height: min(720px, 88vh);
  overflow-y: auto;
  padding: 22px;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgb(255 248 232 / 96%), rgb(253 251 247 / 92%));
  box-shadow: 0 28px 80px rgb(32 21 15 / 24%);
}

.avatar-picker-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.avatar-picker-head h2 {
  margin: 8px 0 0;
  color: var(--journal-ink);
  font-size: 24px;
}

.avatar-picker-head p {
  margin: 6px 0 0;
  color: var(--journal-muted);
  font-size: 13px;
}

.avatar-picker-close {
  min-height: 36px;
  border-radius: 999px;
  padding: 0 14px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 72%);
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
}

.avatar-auto-card,
.avatar-option-card {
  border: 1px solid rgb(62 50 40 / 14%);
  color: var(--journal-ink);
  background: rgb(253 251 247 / 68%);
  cursor: pointer;
  text-align: left;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.avatar-auto-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 18px;
  padding: 13px 14px;
  border-radius: 14px;
}

.avatar-auto-card.active,
.avatar-option-card.active {
  border-color: rgb(200 90 84 / 42%);
  box-shadow: 0 12px 26px rgb(200 90 84 / 12%);
  background: rgb(255 248 232 / 92%);
}

.avatar-auto-card:hover,
.avatar-option-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgb(62 50 40 / 12%);
}

.auto-lens {
  position: relative;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border: 6px solid #f5e8ce;
  border-radius: 999px;
  background: radial-gradient(circle, #3e3228 0 32%, #20150f 33% 100%);
}

.auto-lens::after {
  content: "";
  position: absolute;
  inset: 6px;
  border-radius: inherit;
  background: conic-gradient(from 0deg, transparent, rgb(232 195 108 / 72%), transparent 45%);
  animation: avatarLensSpin 2.4s linear infinite;
}

.avatar-auto-card strong,
.avatar-auto-card small,
.avatar-option-copy strong,
.avatar-option-copy small,
.avatar-option-copy em {
  display: block;
}

.avatar-auto-card small,
.avatar-option-copy small {
  margin-top: 4px;
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.5;
}

.avatar-option-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.avatar-option-card {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 10px;
  justify-items: center;
  padding: 14px 10px 12px;
  border-radius: 14px;
}

.avatar-option-card::before {
  content: "";
  position: absolute;
  left: 8px;
  right: 8px;
  top: 7px;
  height: 8px;
  background: repeating-linear-gradient(90deg, rgb(62 50 40 / 24%) 0 6px, transparent 6px 14px);
  opacity: 0.38;
}

.avatar-thumb-stage {
  position: relative;
  width: 92px;
  height: 92px;
  display: grid;
  place-items: center;
  border: 1px solid rgb(62 50 40 / 12%);
  border-radius: 18px;
  background: rgb(255 248 232 / 82%);
  box-shadow: inset 0 0 0 1px rgb(255 255 255 / 62%);
}

.avatar-thumb-stage img {
  width: 84px;
  height: 84px;
  object-fit: contain;
  filter: drop-shadow(0 8px 10px rgb(62 50 40 / 16%));
  transform-origin: 50% 88%;
}

.avatar-thumb-stage i {
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 9px;
  height: 9px;
  border: 2px solid rgb(255 248 232 / 90%);
  border-radius: 999px;
  background: #87a777;
  box-shadow: 0 0 10px rgb(135 167 119 / 56%);
  animation: xiaoxiStatusLight 2.4s ease-in-out infinite;
}

.avatar-option-copy {
  width: 100%;
  text-align: center;
}

.avatar-option-copy strong {
  color: var(--journal-ink);
  font-size: 13px;
}

.avatar-option-copy em {
  margin-top: 6px;
  color: var(--journal-stamp);
  font-size: 11px;
  font-style: normal;
  font-weight: 800;
}

.avatar-option-think .avatar-thumb-stage img {
  animation: xiaoxiThink 1.45s ease-in-out infinite;
}

.avatar-option-happy .avatar-thumb-stage img {
  animation: xiaoxiHappy 1.9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}

.avatar-option-comfort .avatar-thumb-stage img {
  animation: xiaoxiComfort 3.2s ease-in-out infinite;
}

.avatar-option-angry .avatar-thumb-stage img {
  animation: xiaoxiAngry 0.42s ease-in-out infinite;
}

.avatar-option-shy .avatar-thumb-stage img {
  animation: xiaoxiShy 2.2s ease-in-out infinite;
}

.avatar-option-naughty .avatar-thumb-stage img {
  animation: xiaoxiNaughty 2.1s ease-in-out infinite;
}

.avatar-dialog-enter-active,
.avatar-dialog-leave-active {
  transition: opacity 0.24s ease;
}

.avatar-dialog-enter-active .avatar-picker-panel,
.avatar-dialog-leave-active .avatar-picker-panel {
  transition: transform 0.28s cubic-bezier(0.2, 0.9, 0.2, 1), filter 0.28s ease;
}

.avatar-dialog-enter-from,
.avatar-dialog-leave-to {
  opacity: 0;
}

.avatar-dialog-enter-from .avatar-picker-panel,
.avatar-dialog-leave-to .avatar-picker-panel {
  transform: translateY(18px) scale(0.98);
  filter: blur(8px);
}

.message-board {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: auto;
  padding: 28px 8px 24px;
}

.message-board::-webkit-scrollbar {
  width: 8px;
}

.message-board::-webkit-scrollbar-thumb {
  background: rgb(62 50 40 / 22%);
  border-radius: 999px;
}

.message-stack {
  display: contents;
}

.message-row {
  display: flex;
  margin-bottom: 20px;
  will-change: transform, opacity, filter;
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
  animation: xiaoxiFloat 4.4s ease-in-out infinite;
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
  transform-origin: 50% 88%;
}

.xiaoxi-status img {
  animation: xiaoxiBreathe 4.6s ease-in-out infinite;
  transform-origin: 50% 88%;
}

.xiaoxi-status-think img,
.xiaoxi-avatar-think .xiaoxi-avatar {
  animation: xiaoxiThink 1.45s ease-in-out infinite;
}

.xiaoxi-status-happy img,
.xiaoxi-avatar-happy .xiaoxi-avatar {
  animation: xiaoxiHappy 1.9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}

.xiaoxi-status-comfort img,
.xiaoxi-avatar-comfort .xiaoxi-avatar {
  animation: xiaoxiComfort 3.2s ease-in-out infinite;
}

.xiaoxi-status-angry img,
.xiaoxi-avatar-angry .xiaoxi-avatar {
  animation: xiaoxiAngry 0.42s ease-in-out infinite;
}

.xiaoxi-status-shy img,
.xiaoxi-avatar-shy .xiaoxi-avatar {
  animation: xiaoxiShy 2.2s ease-in-out infinite;
}

.xiaoxi-status-naughty img,
.xiaoxi-avatar-naughty .xiaoxi-avatar {
  animation: xiaoxiNaughty 2.1s ease-in-out infinite;
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
  animation: errorShake 0.34s ease-in-out;
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

.thinking-strip {
  width: fit-content;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: -4px 0 18px 84px;
  padding: 9px 13px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  color: var(--journal-muted);
  background: rgb(255 248 232 / 74%);
  box-shadow: 0 10px 22px rgb(62 50 40 / 10%);
}

.thinking-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--journal-stamp);
  animation: thinkingDot 1s ease-in-out infinite;
}

.thinking-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.thinking-dot:nth-child(3) {
  animation-delay: 0.3s;
}

.thinking-strip small {
  color: var(--journal-muted);
  font-size: 12px;
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
  transform-origin: 50% 88%;
  animation: xiaoxiBreathe 4.6s ease-in-out infinite;
}

.empty-xiaoxi-think {
  animation: xiaoxiThink 1.45s ease-in-out infinite;
}

.empty-xiaoxi-happy {
  animation: xiaoxiHappy 1.9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}

.empty-xiaoxi-comfort {
  animation: xiaoxiComfort 3.2s ease-in-out infinite;
}

.empty-xiaoxi-angry {
  animation: xiaoxiAngry 0.42s ease-in-out infinite;
}

.empty-xiaoxi-shy {
  animation: xiaoxiShy 2.2s ease-in-out infinite;
}

.empty-xiaoxi-naughty {
  animation: xiaoxiNaughty 2.1s ease-in-out infinite;
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

.empty-avatar-switch {
  margin-top: 16px;
}

.composer-wrap {
  flex: 0 0 auto;
  padding-top: 12px;
}

.composer {
  position: relative;
  overflow: hidden;
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
  transition:
    border-color 0.25s ease,
    box-shadow 0.25s ease,
    transform 0.25s ease;
}

.composer::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(115deg, transparent 0 34%, rgb(255 255 255 / 42%) 45%, transparent 58%),
    radial-gradient(circle at 8% 50%, rgb(232 195 108 / 18%), transparent 28%);
  opacity: 0;
  transform: translateX(-55%);
  pointer-events: none;
  transition: opacity 0.25s ease;
}

.composer:focus-within {
  border-color: rgb(200 90 84 / 38%);
  box-shadow:
    0 20px 46px rgb(62 50 40 / 18%),
    0 0 0 4px rgb(200 90 84 / 10%);
}

.composer:focus-within::before {
  opacity: 1;
  animation: composerSweep 2.8s ease-in-out infinite;
}

.composer-recording {
  border-color: rgb(200 90 84 / 52%);
  box-shadow:
    0 20px 48px rgb(62 50 40 / 18%),
    0 0 0 5px rgb(200 90 84 / 12%);
}

.composer-sending {
  transform: translateY(-1px);
}

.composer-input {
  position: relative;
  z-index: 1;
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
  position: relative;
  z-index: 1;
  overflow: hidden;
  min-height: 52px;
  border-radius: 14px;
  padding: 0 20px;
  color: #fff8e8;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 18%);
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    background 0.18s ease;
}

.send-btn:active,
.record-btn:active {
  transform: translateY(1px) scale(0.98);
}

.button-shutter {
  position: absolute;
  inset: -32%;
  border-radius: 999px;
  background:
    conic-gradient(from 0deg, transparent 0 12%, rgb(255 248 232 / 36%) 13% 22%, transparent 23% 37%, rgb(255 248 232 / 30%) 38% 48%, transparent 49% 100%);
  opacity: 0;
  transform: scale(1.35) rotate(0deg);
  pointer-events: none;
}

.send-btn.loading .button-shutter {
  opacity: 1;
  animation: buttonShutterSpin 0.82s ease-in-out infinite;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.record-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--journal-ink);
  background: var(--journal-kodak);
}

.record-btn.recording {
  color: #fff8e8;
  background: var(--journal-stamp);
}

.record-wave {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  height: 18px;
}

.record-wave i {
  width: 3px;
  height: 8px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.64;
  transform-origin: 50% 100%;
}

.record-btn.recording .record-wave i {
  animation: recordWave 0.72s ease-in-out infinite;
}

.record-wave i:nth-child(2) {
  animation-delay: 0.1s;
}

.record-wave i:nth-child(3) {
  animation-delay: 0.2s;
}

.record-wave i:nth-child(4) {
  animation-delay: 0.3s;
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

  .today-film-folder {
    min-width: 0;
    margin-top: 18px;
  }

  .avatar-picker-backdrop {
    padding: 14px;
  }

  .avatar-picker-panel {
    padding: 18px 14px;
  }

  .avatar-picker-head {
    display: grid;
  }

  .avatar-picker-close {
    justify-self: start;
  }

  .avatar-option-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .folder-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .xiaoxi-status img {
    width: 64px;
    height: 64px;
  }

  .xiaoxi-avatar-stage {
    flex-basis: 64px;
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

  .thinking-strip {
    margin-left: 62px;
  }
}

@media (max-width: 460px) {
  .avatar-option-grid {
    grid-template-columns: 1fr;
  }
}

@keyframes composerSweep {
  0%,
  20% {
    transform: translateX(-65%);
  }
  70%,
  100% {
    transform: translateX(72%);
  }
}

@keyframes buttonShutterSpin {
  0% {
    transform: scale(1.25) rotate(0deg);
    opacity: 0.2;
  }
  50% {
    transform: scale(0.78) rotate(55deg);
    opacity: 0.88;
  }
  100% {
    transform: scale(1.25) rotate(110deg);
    opacity: 0.2;
  }
}

@keyframes recordWave {
  0%,
  100% {
    transform: scaleY(0.55);
  }
  50% {
    transform: scaleY(1.65);
  }
}

.message-develop-enter-active {
  transition:
    opacity 0.48s ease,
    transform 0.48s cubic-bezier(0.2, 0.9, 0.2, 1),
    filter 0.48s ease;
}

.message-develop-leave-active {
  transition:
    opacity 0.22s ease,
    transform 0.22s ease,
    filter 0.22s ease;
}

.message-develop-enter-from {
  opacity: 0;
  transform: translateY(18px) rotate(-1.5deg) scale(0.985);
  filter: blur(9px) sepia(0.5);
}

.user-row.message-develop-enter-from {
  transform: translateY(18px) rotate(1.5deg) scale(0.985);
}

.message-develop-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.985);
  filter: blur(6px);
}

@keyframes xiaoxiBreathe {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-3px) scale(1.025);
  }
}

@keyframes xiaoxiStatusBreathe {
  0%,
  100% {
    box-shadow: 0 14px 30px rgb(62 50 40 / 12%);
  }
  50% {
    box-shadow: 0 18px 34px rgb(62 50 40 / 16%);
  }
}

@keyframes xiaoxiBlink {
  0%,
  88%,
  100% {
    opacity: 0;
    transform: scaleY(0.08);
  }
  91%,
  94% {
    opacity: 0.42;
    transform: scaleY(1);
  }
}

@keyframes xiaoxiStatusLight {
  0%,
  100% {
    opacity: 0.72;
    transform: scale(0.94);
  }
  50% {
    opacity: 1;
    transform: scale(1.08);
  }
}

@keyframes xiaoxiFloat {
  0%,
  100% {
    transform: translateY(0) rotate(-1deg);
  }
  50% {
    transform: translateY(-4px) rotate(1deg);
  }
}

@keyframes xiaoxiThink {
  0%,
  100% {
    transform: rotate(-2deg) translateY(0);
  }
  50% {
    transform: rotate(3deg) translateY(-3px);
  }
}

@keyframes xiaoxiHappy {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  28% {
    transform: translateY(-7px) scale(1.06);
  }
  48% {
    transform: translateY(1px) scale(0.99);
  }
}

@keyframes xiaoxiComfort {
  0%,
  100% {
    transform: translateY(0) scale(1);
    filter: drop-shadow(0 5px 8px rgb(62 50 40 / 16%));
  }
  50% {
    transform: translateY(-4px) scale(1.03);
    filter: drop-shadow(0 9px 14px rgb(200 90 84 / 20%));
  }
}

@keyframes xiaoxiAngry {
  0%,
  100% {
    transform: translateX(0) rotate(0);
  }
  25% {
    transform: translateX(-2px) rotate(-2deg);
  }
  75% {
    transform: translateX(2px) rotate(2deg);
  }
}

@keyframes xiaoxiShy {
  0%,
  100% {
    transform: rotate(0) scale(1);
  }
  50% {
    transform: rotate(-4deg) scale(1.025);
  }
}

@keyframes xiaoxiNaughty {
  0%,
  100% {
    transform: rotate(0) translateY(0);
  }
  30% {
    transform: rotate(5deg) translateY(-4px);
  }
  58% {
    transform: rotate(-3deg) translateY(1px);
  }
}

@keyframes errorShake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

@keyframes thinkingDot {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.42;
  }
  40% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .message-develop-enter-active,
  .message-develop-leave-active {
    transition: none !important;
  }

  .xiaoxi-status img,
  .xiaoxi-status,
  .xiaoxi-blink,
  .xiaoxi-status-light,
  .xiaoxi-avatar-wrap,
  .xiaoxi-avatar,
  .error-card,
  .thinking-dot {
    animation: none !important;
  }
}
</style>

