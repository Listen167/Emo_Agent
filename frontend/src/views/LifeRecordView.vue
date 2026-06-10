<template>
  <div class="life-journal">
    <header class="life-header">
      <div>
        <span class="kodak-chip">Rolls Library</span>
        <h1 class="script-title">胶卷库</h1>
        <p>上传你的胶卷，还原冲洗过程。把日常片段贴进这本旧日记。</p>
      </div>
      <div class="develop-stamp">DEVELOPED<br>BY U-LIFE</div>
    </header>

    <main class="life-layout">
      <section class="record-form-card">
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
          <label class="file-picker">
            <span>{{ image ? image.name : '选择一张照片 / Image' }}</span>
            <input type="file" accept="image/*" @change="onFileChange" />
          </label>

          <button class="save-button" :disabled="saving" @click="save">
            {{ saving ? '保存中...' : '保存记录' }}
          </button>
        </div>
      </section>

      <section class="records-board">
        <div v-if="records.length === 0" class="empty-records">
          <span>NO FILM</span>
          <p>暂时还没有生活记录。</p>
        </div>

        <article v-for="record in records" :key="record.id" class="record-card">
          <span class="card-tape"></span>
          <div class="kodak-label">Kodak Portra 400</div>
          <div class="photo-frame">
            <img v-if="record.media_url" :src="resolveAssetUrl(record.media_url)" />
            <div v-else class="photo-placeholder">
              <span>SHOT ON FILM</span>
            </div>
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
              <span v-if="record.location" class="pill">地点：{{ record.location }}</span>
              <span v-if="record.mood_label" class="pill">情绪：{{ moodText(record.mood_label) }}</span>
              <span v-for="tag in record.tags" :key="tag" class="pill">#{{ tag }}</span>
            </div>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { createLifeRecord, deleteLifeRecord, getLifeRecords, type LifeRecordItem } from '../api/life'
import { resolveAssetUrl } from '../api/client'

const sid = ref(localStorage.getItem('sid') || crypto.randomUUID())
const records = ref<LifeRecordItem[]>([])
const title = ref('')
const content = ref('')
const location = ref('')
const tags = ref('')
const moodLabel = ref('')
const image = ref<File | null>(null)
const saving = ref(false)

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  void load()
})

const load = async () => {
  const { data } = await getLifeRecords(sid.value)
  records.value = data
}

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  image.value = input.files?.[0] || null
}

const save = async () => {
  const cleanContent = content.value.trim()
  if (!cleanContent) return

  saving.value = true
  try {
    const form = new FormData()
    form.append('session_id', sid.value)
    form.append('content', cleanContent)
    if (title.value.trim()) form.append('title', title.value.trim())
    if (location.value.trim()) form.append('location', location.value.trim())
    if (tags.value.trim()) form.append('tags', tags.value.trim())
    if (moodLabel.value) form.append('mood_label', moodLabel.value)
    if (image.value) form.append('image', image.value)

    const { data } = await createLifeRecord(form)
    records.value = [data, ...records.value]
    title.value = ''
    content.value = ''
    location.value = ''
    tags.value = ''
    moodLabel.value = ''
    image.value = null
  } finally {
    saving.value = false
  }
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

.file-picker input {
  display: none;
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

.record-card:nth-child(2n) {
  rotate: -0.6deg;
}

.record-card:nth-child(3n) {
  rotate: 0.7deg;
}

.record-card .kodak-label {
  margin-bottom: 12px;
  rotate: -2deg;
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
