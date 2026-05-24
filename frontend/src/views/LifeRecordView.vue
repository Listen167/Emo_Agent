<template>
  <div class="min-h-screen bg-stone-100">
    <header class="bg-white border-b p-4">
      <h1 class="text-xl font-bold text-stone-800">生活记录</h1>
      <p class="text-xs text-stone-500 mt-1">记录日常片段，图片和文字默认只保存在本地开发数据目录。</p>
    </header>

    <main class="max-w-5xl mx-auto p-4 grid gap-4 md:grid-cols-[360px_1fr]">
      <section class="bg-white rounded-2xl shadow-sm p-4 h-fit">
        <h2 class="font-semibold text-stone-800 mb-3">新增记录</h2>

        <div class="space-y-3">
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
          <input type="file" accept="image/*" class="block w-full text-sm" @change="onFileChange" />

          <button class="w-full rounded-xl bg-stone-800 text-white py-2 disabled:opacity-50" :disabled="saving" @click="save">
            {{ saving ? '保存中...' : '保存记录' }}
          </button>
        </div>
      </section>

      <section class="space-y-3">
        <div v-if="records.length === 0" class="bg-white rounded-2xl p-8 text-center text-stone-500">
          暂时还没有生活记录。
        </div>

        <article v-for="record in records" :key="record.id" class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <img v-if="record.media_url" :src="record.media_url" class="w-full max-h-96 object-cover" />
          <div class="p-4">
            <div class="flex justify-between gap-3">
              <div>
                <h3 class="font-semibold text-stone-900">{{ record.title || '未命名记录' }}</h3>
                <p class="text-xs text-stone-400 mt-1">{{ formatTime(record.created_at) }}</p>
              </div>
              <button class="text-xs text-red-500 hover:text-red-700" @click="remove(record.id)">删除</button>
            </div>

            <p class="text-sm leading-6 whitespace-pre-wrap mt-3 text-stone-700">{{ record.content }}</p>

            <div class="flex flex-wrap gap-2 mt-3 text-xs">
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
.input {
  width: 100%;
  border: 1px solid rgb(214 211 209);
  border-radius: 0.75rem;
  padding: 0.625rem 0.75rem;
  outline: none;
}

.input:focus {
  border-color: rgb(120 113 108);
  box-shadow: 0 0 0 3px rgb(231 229 228);
}

.pill {
  border-radius: 999px;
  background: rgb(245 245 244);
  color: rgb(87 83 78);
  padding: 0.25rem 0.625rem;
}
</style>
