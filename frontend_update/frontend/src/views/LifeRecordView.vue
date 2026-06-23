<template>
  <div class="life-journal">
    <header v-develop class="life-header">
      <div>
        <span class="kodak-chip">Rolls Library</span>
        <h1 class="script-title">胶卷库</h1>
        <p>上传你的胶卷，还原冲洗过程。把日常片段贴进这本旧日记。</p>
      </div>
      <div class="develop-stamp">DEVELOPED<br>BY U-LIFE</div>
    </header>

    <main class="life-layout">
      <section v-develop="80" class="record-form-card">
        <span class="washi-tape"></span>
        <h2>新增记录</h2>

        <div class="form-stack">
          <input v-model="title" class="input" placeholder="标题，例如：晚上的校园散步" />
          <textarea v-model="content" class="input min-h-32 resize-y" placeholder="写下今天发生了什么..." />
          <input v-model="location" class="input" placeholder="地点，例如：图书馆 / 操场" />
          <input v-model="tags" class="input" placeholder="标签，用逗号分隔，例如：学习,朋友,运动" />
          <select v-model="moodLabel" class="input">
            <option value="">关联情绪（可选）</option>
            <option value="happy">开心</option>
            <option value="neutral">平静</option>
            <option value="anxious">焦虑</option>
            <option value="sad">难过</option>
            <option value="angry">生气</option>
            <option value="surprised">惊讶</option>
          </select>
          <div class="visibility-switch" aria-label="记录可见性">
            <button
              :class="{ active: visibility === 'private' }"
              type="button"
              @click="visibility = 'private'"
            >
              仅自己可见
            </button>
            <button
              :class="{ active: visibility === 'public' }"
              type="button"
              @click="visibility = 'public'"
            >
              发布到广场
            </button>
          </div>
          <label class="file-picker">
            <span>{{ image ? image.name : '选择一张照片 / Image' }}</span>
            <input type="file" accept="image/*" @change="onFileChange" />
          </label>
          <Transition name="developing-wash">
            <div v-if="developing" class="upload-developing" aria-live="polite">
              <span class="developing-window"></span>
              <div>
                <strong>PHOTO LAB</strong>
                <small>正在冲洗显影这一张照片</small>
              </div>
            </div>
          </Transition>

          <button class="save-button" :disabled="saving || !canSave" @click="save">
            {{ saving ? '保存中...' : '保存记录' }}
          </button>
        </div>
      </section>

      <section class="records-board">
        <div v-if="records.length === 0" class="empty-records">
          <span>NO FILM</span>
          <p>暂时还没有生活记录。</p>
        </div>

        <article
          v-for="(record, index) in records"
          :key="record.id"
          v-develop="120"
          class="record-card"
          :style="{ '--develop-progress': `${developProgress(record, index)}%` }"
        >
          <span class="card-tape"></span>
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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { createLifeRecord, deleteLifeRecord, getLifeRecords, type LifeRecordItem } from '../api/life'
import { resolveAssetUrl } from '../api/client'
import { createClientId } from '../utils/id'

const sid = ref(localStorage.getItem('sid') || createClientId())
const records = ref<LifeRecordItem[]>([])
const title = ref('')
const content = ref('')
const location = ref('')
const tags = ref('')
const moodLabel = ref('')
const visibility = ref<'private' | 'public'>('private')
const image = ref<File | null>(null)
const saving = ref(false)
const developing = ref(false)
let developingTimer: number | undefined
const canSave = computed(() => Boolean(content.value.trim() || image.value))

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  void load()
})

onBeforeUnmount(() => {
  if (developingTimer) window.clearTimeout(developingTimer)
})

const load = async () => {
  const { data } = await getLifeRecords(sid.value)
  records.value = data
}

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  image.value = input.files?.[0] || null
  if (image.value) showDeveloping()
}

const save = async () => {
  const cleanContent = content.value.trim()
  if (!cleanContent && !image.value) return

  saving.value = true
  if (image.value) showDeveloping()
  try {
    const form = new FormData()
    form.append('session_id', sid.value)
    form.append('content', cleanContent || '分享了一张生活胶片')
    if (title.value.trim()) form.append('title', title.value.trim())
    if (location.value.trim()) form.append('location', location.value.trim())
    if (tags.value.trim()) form.append('tags', tags.value.trim())
    if (moodLabel.value) form.append('mood_label', moodLabel.value)
    form.append('visibility', visibility.value)
    if (image.value) form.append('image', image.value)

    const { data } = await createLifeRecord(form)
    records.value = [data, ...records.value]
    title.value = ''
    content.value = ''
    location.value = ''
    tags.value = ''
    moodLabel.value = ''
    visibility.value = 'private'
    image.value = null
  } finally {
    saving.value = false
  }
}

const showDeveloping = () => {
  developing.value = true
  if (developingTimer) window.clearTimeout(developingTimer)
  developingTimer = window.setTimeout(() => {
    developing.value = false
  }, 1400)
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

const remove = async (id: number) => {
  await deleteLifeRecord(id, sid.value)
  records.value = records.value.filter(record => record.id !== id)
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

.kodak-chip,
.kodak-label {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.develop-stamp {
  align-self: center;
  padding: 12px 16px;
  border: 2px solid var(--journal-stamp);
  border-radius: 999px;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
  text-align: center;
  rotate: 7deg;
}

.life-layout {
  display: grid;
  grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
  gap: 24px;
  padding-top: 26px;
}

.record-form-card {
  position: sticky;
  top: 24px;
  height: fit-content;
  padding: 24px;
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 18px 42px rgb(62 50 40 / 16%);
  clip-path: polygon(0 2%, 98% 0, 100% 97%, 2% 100%);
}

.washi-tape,
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

.record-form-card h2 {
  margin: 0 0 16px;
  color: var(--journal-ink);
  font-size: 22px;
}

.form-stack {
  display: grid;
  gap: 12px;
}

.input {
  width: 100%;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.72rem 0.8rem;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
}

.input:focus {
  border-color: rgb(200 90 84 / 48%);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
}

.file-picker {
  display: flex;
  align-items: center;
  min-height: 44px;
  padding: 0 12px;
  border: 1px dashed rgb(62 50 40 / 34%);
  border-radius: 10px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 58%);
  cursor: pointer;
}

.visibility-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 5px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 12px;
  background: rgb(253 251 247 / 58%);
}

.visibility-switch button {
  min-height: 36px;
  border-radius: 9px;
  color: var(--journal-muted);
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.visibility-switch button.active {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 8px 16px rgb(62 50 40 / 14%);
}

.file-picker input {
  display: none;
}

.upload-developing {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  padding: 10px;
  border: 1px dashed rgb(62 50 40 / 20%);
  border-radius: 12px;
  background: rgb(253 251 247 / 68%);
  overflow: hidden;
}

.developing-window {
  position: relative;
  height: 46px;
  border-radius: 8px;
  border: 1px solid rgb(62 50 40 / 16%);
  background:
    linear-gradient(90deg, transparent 0 10%, rgb(62 50 40 / 22%) 10% 14%, transparent 14% 28%, rgb(62 50 40 / 20%) 28% 32%, transparent 32% 100%),
    linear-gradient(135deg, #30251d, #e8c36c 54%, #fff8e8);
  box-shadow: inset 0 0 0 5px rgb(32 21 15 / 82%);
}

.developing-window::after {
  content: "";
  position: absolute;
  inset: 6px;
  background: linear-gradient(90deg, transparent, rgb(255 248 232 / 76%), transparent);
  transform: translateX(-120%);
  animation: developingSweep 1.15s ease-in-out infinite;
}

.upload-developing strong,
.upload-developing small {
  display: block;
}

.upload-developing strong {
  color: var(--journal-stamp);
  font-size: 12px;
}

.upload-developing small {
  margin-top: 4px;
  color: var(--journal-muted);
  font-size: 12px;
}

.developing-wash-enter-active,
.developing-wash-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease, filter 0.28s ease;
}

.developing-wash-enter-from,
.developing-wash-leave-to {
  opacity: 0;
  transform: translateY(8px);
  filter: blur(5px);
}

.save-button {
  width: 100%;
  min-height: 46px;
  border-radius: 12px;
  color: #fff8e8;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 18%);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.records-board {
  columns: 2 300px;
  column-gap: 22px;
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

.record-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
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

@keyframes developingSweep {
  to {
    transform: translateX(120%);
  }
}

@keyframes developGrow {
  from {
    width: 18%;
  }
}

@media (max-width: 920px) {
  .life-journal {
    padding: 16px 14px 26px;
  }

  .life-layout {
    display: block;
  }

  .record-form-card {
    position: relative;
    top: auto;
    margin-bottom: 24px;
  }

  .develop-stamp {
    display: none;
  }
}
</style>

