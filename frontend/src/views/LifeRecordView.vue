<template>
  <div class="life-journal">
    <header v-develop class="life-header">
      <div class="life-header-copy">
        <span class="kodak-chip">Rolls Library</span>
        <h1 class="script-title">胶卷库</h1>
        <p>上传你的胶卷，还原冲洗过程。把日常片段贴进这本旧日记。</p>
      </div>
      <div class="film-desk" aria-label="胶片状态条">
        <span class="film-desk-rail film-desk-rail-top" aria-hidden="true"></span>
        <span class="film-desk-rail film-desk-rail-bottom" aria-hidden="true"></span>
        <div class="film-desk-meta">
          <span class="film-desk-badge">
            <small>已存胶片</small>
            <strong>{{ records.length }}</strong>
          </span>
          <span class="film-desk-badge">
            <small>公开帧</small>
            <strong>{{ publicRecords.length }}</strong>
          </span>
        </div>

        <div class="film-desk-main">
          <button
            class="latest-frame-widget"
            type="button"
            :disabled="!latestRecord"
            @click="latestRecord && focusRecord(latestRecord.id)"
          >
            <span>最近一帧</span>
            <div class="latest-frame-preview">
              <img v-if="latestRecord?.media_url" :src="resolveAssetUrl(latestRecord.media_url)" alt="最近生活记录图片" />
              <b v-else>{{ latestRecordTitle }}</b>
            </div>
          </button>

          <div class="xiaoxi-desk-note">
            <span>小曦便签</span>
            <p>{{ xiaoxiNote }}</p>
          </div>

          <div class="week-progress-widget">
            <span>本周胶片</span>
            <div class="week-progress-copy">
              <strong>{{ weeklyRecords.length }}</strong>
              <small>{{ weekProgressText }}</small>
            </div>
            <div class="week-dots" aria-hidden="true">
              <i v-for="day in weekDots" :key="day.key" :class="{ active: day.active }"></i>
            </div>
          </div>

          <button class="random-frame-button" type="button" :disabled="records.length === 0" @click="pickRandomRecord">
            随机回看一帧
          </button>
        </div>

        <span class="film-desk-hint">{{ filmDeskHint }}</span>
      </div>
    </header>

    <main class="life-layout">
      <RecordComposer
        v-develop="80"
        :session-id="sid"
        variant="life"
        default-visibility="private"
        title="新增记录"
        :avatar-src="currentXiaoxiAvatar.src"
        private-hint="私密记录只保存在成长记忆里。"
        public-hint="公开记录会进入聊天广场，也会保留在成长记忆里。"
        private-submit-label="保存记录"
        public-submit-label="发布到广场"
        @created="handleRecordCreated"
      />

      <section class="records-board">
        <div class="drying-line" aria-hidden="true">
          <span class="line-rope"></span>
          <i class="photo-clip clip-one"></i>
          <i class="photo-clip clip-two"></i>
          <i class="photo-clip clip-three"></i>
          <span class="hanging-photo photo-one"></span>
          <span class="hanging-photo photo-two"></span>
          <span class="hanging-photo photo-three"></span>
        </div>
        <div v-if="records.length === 0" class="empty-records">
          <span>NO FILM</span>
          <p>暂时还没有生活记录。</p>
        </div>

        <article
          v-for="(record, index) in records"
          :key="record.id"
          :ref="el => setRecordElement(record.id, el)"
          v-develop="120"
          :class="['record-card', { 'record-card-highlight': highlightedRecordId === record.id }]"
          :style="{ '--develop-progress': `${developProgress(record, index)}%` }"
        >
          <span class="card-tape"></span>
          <span class="scrapbook-sticker" aria-hidden="true">{{ cardSticker(record, index) }}</span>
          <div class="record-card-head">
            <div class="kodak-label">Kodak Portra 400</div>
            <span class="film-number">{{ recordNumber(index) }}</span>
          </div>
          <div class="photo-frame">
            <img v-if="record.media_url" :src="resolveAssetUrl(record.media_url)" />
            <div v-else class="photo-placeholder">
              <span>SHOT ON FILM</span>
            </div>
          </div>
          <div class="develop-meter" aria-hidden="true">
            <span></span>
            <em>DEVELOP {{ developProgress(record, index) }}%</em>
          </div>
          <div class="record-body">
            <div class="record-title-row">
              <div>
                <h3>{{ record.title || '未命名记录' }}</h3>
                <p>{{ formatTime(record.created_at) }}</p>
              </div>
              <button class="delete-btn" @click="remove(record.id)">删除</button>
            </div>

            <p class="record-content">{{ record.content }}</p>

            <div class="record-tags">
              <span v-if="record.mood_label" class="sticker-label">{{ stickerText(record.mood_label) }}</span>
              <span :class="['pill', record.visibility === 'public' ? 'public-pill' : 'private-pill']">
                {{ record.visibility === 'public' ? '广场公开' : '仅自己可见' }}
              </span>
              <span v-if="record.location" class="pill">地点：{{ record.location }}</span>
              <span v-if="record.mood_label" class="pill">情绪：{{ moodText(record.mood_label) }}</span>
              <span v-for="tag in record.tags" :key="tag" class="pill">#{{ tag }}</span>
            </div>
            <div v-if="record.visibility === 'public'" class="social-stats">
              <span>{{ record.like_count }} 喜欢</span>
              <span>{{ record.comment_count }} 评论</span>
              <span>{{ record.repost_count }} 转发</span>
            </div>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, type ComponentPublicInstance } from 'vue'

import RecordComposer from '../components/RecordComposer.vue'
import { deleteLifeRecord, getLifeRecords, type LifeRecordItem } from '../api/life'
import { resolveAssetUrl } from '../api/client'
import { createClientId } from '../utils/id'

const xiaoxiAvatars = {
  usual: { src: '/xiaoxi/usual.png' },
  happy: { src: '/xiaoxi/happy.png' },
  comfort: { src: '/xiaoxi/comfort.png' },
  angry: { src: '/xiaoxi/angry.png' },
  shy: { src: '/xiaoxi/shy.png' },
  think: { src: '/xiaoxi/think.png' },
  naughty: { src: '/xiaoxi/naughty.png' },
} as const

type XiaoxiAvatarKey = keyof typeof xiaoxiAvatars

const sid = ref(localStorage.getItem('sid') || createClientId())
const records = ref<LifeRecordItem[]>([])
const storedAvatarKey = localStorage.getItem('u-life-xiaoxi-avatar-key-v1')
const currentAvatarKey = ref<XiaoxiAvatarKey>(isXiaoxiAvatarKey(storedAvatarKey) ? storedAvatarKey : 'usual')
const highlightedRecordId = ref<number | null>(null)
const recordElements = new Map<number, Element>()
let highlightTimer: number | undefined
const currentXiaoxiAvatar = computed(() => xiaoxiAvatars[currentAvatarKey.value])
const latestRecord = computed(() => records.value[0] || null)
const latestRecordTitle = computed(() => latestRecord.value?.title || latestRecord.value?.content || '还没有胶片')
const publicRecords = computed(() => records.value.filter(record => record.visibility === 'public'))
const xiaoxiNotes = [
  '今天可以只保存一个瞬间。',
  '不用把每一天都过得很完整。',
  '这卷胶片慢慢拍。',
  '只写一句话，也算给今天留了光。',
  '看到旧照片时，记得先对自己温柔一点。',
]
const xiaoxiNote = computed(() => {
  const daySeed = Math.floor(Date.now() / 86400000)
  return xiaoxiNotes[daySeed % xiaoxiNotes.length]
})
const weekStart = computed(() => {
  const date = new Date()
  const day = (date.getDay() + 6) % 7
  date.setHours(0, 0, 0, 0)
  date.setDate(date.getDate() - day)
  return date
})
const weeklyRecords = computed(() =>
  records.value.filter(record => {
    const date = new Date(record.created_at)
    return !Number.isNaN(date.getTime()) && date >= weekStart.value
  })
)
const filmDeskHint = computed(() => {
  if (records.value.length === 0) return '先留下一帧，胶片夹会慢慢亮起来'
  if (weeklyRecords.value.length === 0) return '这一周还很安静，可以从一句话开始'
  if (publicRecords.value.length === 0) return '都在私密胶卷里，安心保存也很好'
  return '状态条会帮你快速回到最近和随机的一帧'
})
const weekProgressText = computed(() => {
  if (weeklyRecords.value.length === 0) return '还没开拍，也没关系'
  if (weeklyRecords.value.length < 3) return '轻轻留下了几帧'
  if (weeklyRecords.value.length < 6) return '这一周有在好好记录'
  return '这一卷很充实'
})
const weekDots = computed(() =>
  Array.from({ length: 7 }, (_, index) => {
    const date = new Date(weekStart.value)
    date.setDate(date.getDate() + index)
    const key = date.toISOString().slice(0, 10)
    return {
      key,
      active: records.value.some(record => {
        const recordDate = new Date(record.created_at)
        return !Number.isNaN(recordDate.getTime()) && recordDate.toISOString().slice(0, 10) === key
      }),
    }
  })
)

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  window.addEventListener('u-life-xiaoxi-avatar-changed', syncCurrentAvatar)
  void load()
})

onBeforeUnmount(() => {
  if (highlightTimer) window.clearTimeout(highlightTimer)
  window.removeEventListener('u-life-xiaoxi-avatar-changed', syncCurrentAvatar)
})

function isXiaoxiAvatarKey(value: string | null): value is XiaoxiAvatarKey {
  return Boolean(value && value in xiaoxiAvatars)
}

function syncCurrentAvatar() {
  const value = localStorage.getItem('u-life-xiaoxi-avatar-key-v1')
  currentAvatarKey.value = isXiaoxiAvatarKey(value) ? value : 'usual'
}

const load = async () => {
  const { data } = await getLifeRecords(sid.value)
  records.value = data
}

const handleRecordCreated = (record: LifeRecordItem) => {
  records.value = [record, ...records.value]
}

const recordNumber = (index: number) => `ROLL ${String(records.value.length - index).padStart(3, '0')}`

const developProgress = (record: LifeRecordItem, index: number) => {
  const seed = Number(record.id || index + 1)
  return 72 + (seed % 24)
}

const stickerText = (mood: string) => {
  const map: Record<string, string> = {
    happy: 'SUNNY FRAME',
    neutral: 'SOFT LIGHT',
    anxious: 'FAST SHOT',
    sad: 'BLUE HOUR',
    angry: 'RED FILTER',
    surprised: 'FLASH CUT',
  }
  return map[mood] || 'DAILY SHOT'
}

const cardSticker = (record: LifeRecordItem, index: number) => {
  if (record.visibility === 'public') return 'PUBLIC ROLL'
  if (record.media_url) return 'PHOTO LAB'
  if (record.mood_label) return stickerText(record.mood_label)
  const stickers = ['KEEP THIS', 'DAILY SHOT', 'SOFT MEMORY', 'U-LIFE']
  return stickers[index % stickers.length]
}

const remove = async (id: number) => {
  await deleteLifeRecord(id, sid.value)
  records.value = records.value.filter(record => record.id !== id)
  recordElements.delete(id)
}

const setRecordElement = (id: number, el: Element | ComponentPublicInstance | null) => {
  if (el instanceof Element) {
    recordElements.set(id, el)
  } else {
    recordElements.delete(id)
  }
}

const focusRecord = async (id: number) => {
  highlightedRecordId.value = id
  await nextTick()
  recordElements.get(id)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  if (highlightTimer) window.clearTimeout(highlightTimer)
  highlightTimer = window.setTimeout(() => {
    highlightedRecordId.value = null
  }, 1800)
}

const pickRandomRecord = () => {
  if (records.value.length === 0) return
  const next = records.value[Math.floor(Math.random() * records.value.length)]
  void focusRecord(next.id)
}

const formatTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(date)
}

const moodText = (mood: string) => {
  const map: Record<string, string> = {
    happy: '开心',
    neutral: '平静',
    anxious: '焦虑',
    sad: '难过',
    angry: '生气',
    surprised: '惊讶'
  }
  return map[mood] || mood
}
</script>

<style scoped>
.life-journal {
  min-height: 100vh;
  padding: 26px 30px 42px;
}

.life-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.life-header-copy {
  min-width: 220px;
  max-width: 460px;
}

.life-header h1 {
  margin: 8px 0 0;
  font-size: clamp(44px, 6vw, 72px);
  line-height: 0.9;
}

.life-header p {
  margin: 8px 0 0;
  color: var(--journal-muted);
  font-size: 14px;
}

.film-desk {
  position: relative;
  flex: 1 1 620px;
  max-width: 760px;
  min-width: 520px;
  align-self: center;
  display: grid;
  gap: 8px;
  padding: 22px 10px 28px;
  border: 1px solid rgb(62 50 40 / 12%);
  border-radius: 18px;
  background:
    linear-gradient(115deg, transparent 0 42%, rgb(255 248 232 / 58%) 48%, transparent 54%),
    linear-gradient(90deg, rgb(62 50 40 / 7%) 0 1px, transparent 1px 18px),
    rgb(253 251 247 / 54%);
  background-size: 260% 100%, 18px 18px, auto;
  box-shadow:
    inset 0 1px 0 rgb(255 248 232 / 70%),
    inset 0 0 0 1px rgb(255 248 232 / 34%),
    0 14px 28px rgb(62 50 40 / 10%);
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease, background-position 0.6s ease;
}

.film-desk:hover,
.film-desk:focus-within {
  transform: translateY(-1px);
  background-position: 100% 0, 0 0, 0 0;
  box-shadow:
    inset 0 1px 0 rgb(255 248 232 / 72%),
    inset 0 0 0 1px rgb(255 248 232 / 38%),
    0 18px 34px rgb(62 50 40 / 14%);
}

.film-desk-meta {
  position: absolute;
  left: 22px;
  right: 22px;
  top: 8px;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
  pointer-events: none;
}

.film-desk-rail {
  position: absolute;
  left: 14px;
  right: 14px;
  height: 9px;
  border-radius: 999px;
  background:
    radial-gradient(circle, rgb(253 251 247 / 95%) 42%, transparent 46%) left center / 18px 9px repeat-x,
    linear-gradient(90deg, rgb(62 50 40 / 34%), rgb(62 50 40 / 20%));
  opacity: 0.78;
  pointer-events: none;
}

.film-desk-rail-top {
  top: 7px;
  animation: filmDeskRailDrift 9s linear infinite;
}

.film-desk-rail-bottom {
  bottom: 7px;
  animation: filmDeskRailDrift 9s linear infinite reverse;
}

.film-desk-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 48%;
  min-width: 0;
  min-height: 20px;
  padding: 0 8px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 94%);
  box-shadow: 0 8px 16px rgb(62 50 40 / 10%);
}

.film-desk-badge small {
  overflow: hidden;
  color: var(--journal-muted);
  font-size: 9px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.film-desk-badge strong {
  color: var(--journal-stamp);
  font-size: 13px;
  line-height: 1;
}

.film-desk-hint {
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 7px;
  z-index: 2;
  overflow: hidden;
  color: var(--journal-muted);
  font-size: 10px;
  font-weight: 800;
  text-align: center;
  text-overflow: ellipsis;
  white-space: nowrap;
  pointer-events: none;
}

.film-desk-main {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(168px, 1.05fr) minmax(160px, 1fr) minmax(172px, 1fr) auto;
  gap: 8px;
  align-items: stretch;
  min-width: 0;
}

.xiaoxi-desk-note,
.latest-frame-widget,
.week-progress-widget,
.random-frame-button {
  position: relative;
  z-index: 1;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(253 251 247 / 80%);
}

.xiaoxi-desk-note {
  min-width: 0;
  padding: 10px 12px;
  border-radius: 12px;
}

.xiaoxi-desk-note span,
.latest-frame-widget span,
.week-progress-widget span {
  display: block;
  color: var(--journal-stamp);
  font-size: 10px;
  font-weight: 900;
}

.xiaoxi-desk-note p {
  margin: 6px 0 0;
  color: var(--journal-ink);
  font-size: 12px;
  line-height: 1.45;
}

.latest-frame-widget {
  display: grid;
  grid-template-columns: 1fr 64px;
  gap: 8px;
  align-items: center;
  min-width: 0;
  padding: 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.latest-frame-widget::after {
  content: "";
  position: absolute;
  inset: 8px;
  border-radius: 10px;
  border: 1px dashed rgb(62 50 40 / 12%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease;
}

.latest-frame-widget:disabled,
.random-frame-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.latest-frame-widget:not(:disabled):hover,
.random-frame-button:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 28px rgb(62 50 40 / 16%);
}

.latest-frame-widget:not(:disabled):hover::after,
.latest-frame-widget:not(:disabled):focus-visible::after {
  opacity: 1;
}

.latest-frame-preview {
  width: 64px;
  min-width: 0;
}

.latest-frame-preview img,
.latest-frame-preview b {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 9px;
  color: var(--journal-muted);
  background:
    linear-gradient(145deg, rgb(232 195 108 / 72%), rgb(200 90 84 / 34%)),
    #fff8e8;
  object-fit: cover;
  font-size: 11px;
  line-height: 1.35;
  box-shadow: inset 0 0 0 4px rgb(253 251 247 / 58%);
}

.latest-frame-preview b {
  padding: 6px;
  font-weight: 800;
}

.week-progress-widget {
  min-width: 0;
  padding: 10px 12px;
  border-radius: 12px;
}

.week-progress-copy {
  display: flex;
  align-items: baseline;
  gap: 7px;
  margin-top: 2px;
}

.week-progress-widget strong {
  color: var(--journal-ink);
  font-size: 26px;
  line-height: 1;
}

.week-progress-widget small {
  color: var(--journal-muted);
  font-size: 11px;
  font-weight: 700;
}

.week-dots {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
  margin-top: 8px;
}

.week-dots i {
  height: 7px;
  border-radius: 999px;
  background: rgb(62 50 40 / 12%);
}

.week-dots i.active {
  background: var(--journal-stamp);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
  animation: weekDotGlow 2.8s ease-in-out infinite;
}

.random-frame-button {
  min-width: 118px;
  min-height: 100%;
  border-radius: 12px;
  padding: 0 12px;
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
  font-size: 12px;
  font-weight: 900;
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
}

.random-frame-button::before {
  content: "";
  position: absolute;
  inset: 7px;
  border: 1px solid rgb(255 248 232 / 16%);
  border-radius: 9px;
  pointer-events: none;
}

.random-frame-button:not(:disabled):active {
  transform: translateY(0) scale(0.98);
}

.kodak-chip,
.kodak-label {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.life-layout {
  display: grid;
  grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
  gap: 24px;
  padding-top: 26px;
}

.card-tape {
  position: absolute;
  top: -12px;
  left: 34px;
  width: 112px;
  height: 28px;
  rotate: -4deg;
  background: rgb(232 195 108 / 58%);
  border: 1px solid rgb(62 50 40 / 10%);
}

.records-board {
  columns: 2 300px;
  column-gap: 22px;
}

.drying-line {
  position: relative;
  break-inside: avoid;
  height: 108px;
  margin: 0 0 18px;
  overflow: visible;
}

.line-rope {
  position: absolute;
  left: 4px;
  right: 4px;
  top: 22px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgb(62 50 40 / 36%), transparent);
}

.photo-clip {
  position: absolute;
  z-index: 2;
  top: 13px;
  width: 8px;
  height: 18px;
  border-radius: 3px;
  background: #3e3228;
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 18%);
}

.clip-one { left: 12%; rotate: -3deg; }
.clip-two { left: 46%; rotate: 2deg; }
.clip-three { right: 15%; rotate: -2deg; }

.hanging-photo {
  position: absolute;
  top: 24px;
  width: 72px;
  height: 68px;
  padding: 7px 7px 16px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: #fdfbf7;
  box-shadow: 0 10px 20px rgb(62 50 40 / 12%);
  transform-origin: 50% 0;
  animation: hangingPhotoSway 4.6s ease-in-out infinite;
}

.hanging-photo::after {
  content: "";
  display: block;
  width: 100%;
  height: 100%;
  background:
    linear-gradient(135deg, rgb(232 195 108 / 84%), rgb(200 90 84 / 52)),
    linear-gradient(160deg, #6f91a8, #fff8e8);
}

.photo-one {
  left: 6%;
  rotate: -4deg;
}

.photo-two {
  left: 38%;
  rotate: 3deg;
  animation-delay: 0.35s;
}

.photo-two::after {
  background:
    linear-gradient(145deg, rgb(58 82 78 / 72%), rgb(232 195 108 / 62%)),
    #fff8e8;
}

.photo-three {
  right: 8%;
  rotate: -2deg;
  animation-delay: 0.7s;
}

.photo-three::after {
  background:
    linear-gradient(145deg, rgb(154 122 168 / 68%), rgb(255 248 232 / 84%)),
    #fff8e8;
}

.empty-records {
  padding: 42px;
  text-align: center;
  border: 1px dashed rgb(62 50 40 / 26%);
  background: rgb(255 248 232 / 62%);
}

.empty-records span {
  color: var(--journal-stamp);
  font-weight: 700;
}

.empty-records p {
  margin: 10px 0 0;
  color: var(--journal-muted);
}

.record-card {
  position: relative;
  break-inside: avoid;
  margin: 0 0 22px;
  padding: 18px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: #fff8e8;
  box-shadow: 0 16px 34px rgb(62 50 40 / 16%);
  clip-path: polygon(0 1%, 99% 0, 100% 98%, 2% 100%);
}

.scrapbook-sticker {
  position: absolute;
  z-index: 2;
  right: 20px;
  top: 18px;
  max-width: 112px;
  padding: 5px 8px;
  border: 1px solid rgb(62 50 40 / 13%);
  border-radius: 5px;
  color: var(--journal-ink);
  background: rgb(232 195 108 / 78%);
  box-shadow: 0 6px 12px rgb(62 50 40 / 10%);
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
  rotate: 5deg;
  pointer-events: none;
}

.record-card:nth-child(2n) .scrapbook-sticker {
  rotate: -4deg;
  background: rgb(253 251 247 / 90%);
  color: var(--journal-stamp);
}

.record-card:nth-child(3n) .scrapbook-sticker {
  rotate: 3deg;
  background: rgb(200 90 84 / 88%);
  color: #fff8e8;
}

.record-card::before {
  content: "";
  position: absolute;
  right: 18px;
  top: 54px;
  width: 54px;
  height: 54px;
  border: 2px solid rgb(200 90 84 / 72%);
  border-radius: 999px;
  opacity: 0.18;
  transform: rotate(-12deg);
  pointer-events: none;
}

.record-card:nth-child(2n) {
  rotate: -0.6deg;
}

.record-card:nth-child(3n) {
  rotate: 0.7deg;
}

.record-card-highlight {
  animation: recordSpotlight 1.8s ease-out both;
}

.record-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
  padding-right: 112px;
}

.record-card .kodak-label {
  rotate: -2deg;
}

.film-number {
  padding: 4px 8px;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 999px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 72%);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
}

.photo-frame {
  padding: 10px;
  background: #fdfbf7;
  border: 1px solid rgb(62 50 40 / 14%);
  box-shadow: inset 0 0 0 1px rgb(255 255 255 / 68%);
}

.photo-frame img,
.photo-placeholder {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: grid;
  place-items: center;
}

.photo-placeholder {
  color: rgb(255 248 232 / 86%);
  background:
    linear-gradient(160deg, rgb(58 82 78), rgb(232 195 108) 58%, rgb(62 50 40));
  font-weight: 700;
}

.develop-meter {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
  margin-top: 10px;
  color: var(--journal-muted);
  font-size: 10px;
  font-weight: 800;
}

.develop-meter span {
  position: relative;
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: rgb(62 50 40 / 10%);
}

.develop-meter span::after {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: var(--develop-progress);
  border-radius: inherit;
  background: linear-gradient(90deg, var(--journal-stamp), var(--journal-kodak));
  animation: developGrow 0.75s ease-out both;
}

.sticker-label {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 9px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 4px;
  color: var(--journal-ink);
  background: rgb(232 195 108 / 72%);
  box-shadow: 0 4px 8px rgb(62 50 40 / 9%);
  font-size: 11px;
  font-weight: 900;
  rotate: -2deg;
}

.record-body {
  padding: 14px 4px 2px;
}

.record-title-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.record-title-row h3 {
  margin: 0;
  color: var(--journal-ink);
  font-size: 18px;
}

.record-title-row p {
  margin: 4px 0 0;
  color: var(--journal-muted);
  font-size: 12px;
}

.delete-btn {
  align-self: start;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
  background: transparent;
  cursor: pointer;
}

.record-content {
  margin: 12px 0 0;
  color: var(--journal-ink);
  font-size: 14px;
  line-height: 1.75;
  white-space: pre-wrap;
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.pill {
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  background: rgb(253 251 247 / 72%);
  color: var(--journal-muted);
  padding: 0.28rem 0.62rem;
  font-size: 12px;
}

.public-pill {
  color: #fff8e8;
  background: var(--journal-stamp);
}

.private-pill {
  color: var(--journal-ink);
  background: rgb(232 195 108 / 34%);
}

.social-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
  color: var(--journal-muted);
  font-size: 12px;
}

@keyframes developGrow {
  from {
    width: 18%;
  }
}

@keyframes filmDeskRailDrift {
  to {
    background-position: 18px center, 0 0;
  }
}

@keyframes weekDotGlow {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.68;
  }
}

@keyframes hangingPhotoSway {
  0%,
  100% {
    transform: rotate(-1deg);
  }
  50% {
    transform: rotate(1.8deg);
  }
}

@keyframes recordSpotlight {
  0% {
    box-shadow:
      0 16px 34px rgb(62 50 40 / 16%),
      0 0 0 0 rgb(200 90 84 / 0%);
    transform: scale(1);
  }
  28% {
    box-shadow:
      0 22px 42px rgb(62 50 40 / 20%),
      0 0 0 8px rgb(200 90 84 / 14%);
    transform: scale(1.012);
  }
  100% {
    box-shadow:
      0 16px 34px rgb(62 50 40 / 16%),
      0 0 0 0 rgb(200 90 84 / 0%);
    transform: scale(1);
  }
}

@media (max-width: 920px) {
  .life-journal {
    padding: 16px 14px 26px;
  }

  .life-header {
    display: grid;
  }

  .life-header-copy {
    max-width: none;
  }

  .life-layout {
    display: block;
  }

  .film-desk {
    width: 100%;
    max-width: none;
    min-width: 0;
    min-height: auto;
  }

  .film-desk-main {
    grid-template-columns: minmax(180px, 1fr) minmax(160px, 0.9fr);
  }

  .random-frame-button {
    min-height: 52px;
  }

  .drying-line {
    height: 96px;
  }
}

@media (max-width: 640px) {
  .life-header {
    padding: 20px;
  }

  .film-desk {
    gap: 8px;
    padding-bottom: 32px;
  }

  .film-desk-meta {
    left: 14px;
    right: 14px;
  }

  .film-desk-main {
    grid-template-columns: 1fr;
  }

  .film-desk-badge {
    max-width: 49%;
    padding: 0 7px;
  }

  .film-desk-badge small {
    font-size: 8px;
  }

  .latest-frame-widget {
    min-height: auto;
  }

  .latest-frame-preview {
    width: 72px;
  }
}
</style>
