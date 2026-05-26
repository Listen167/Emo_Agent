<template>
  <div class="min-h-screen bg-emerald-50">
    <header class="bg-white border-b p-4">
      <h1 class="text-xl font-bold text-emerald-900">心情日历</h1>
      <p class="text-xs text-emerald-700 mt-1">按年月查看自己的心情贡献图。</p>
    </header>

    <main class="max-w-6xl mx-auto p-4 space-y-4">
      <section class="bg-white rounded-2xl shadow-sm p-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="font-semibold text-slate-800">{{ selectedYear }} 年 {{ selectedMonth }} 月</h2>
            <p class="text-xs text-slate-500 mt-1">每个方块代表一天，颜色表示当天主要情绪，深浅表示记录次数。</p>
          </div>

          <div class="flex gap-2">
            <select v-model.number="selectedYear" class="select" @change="load">
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }} 年</option>
            </select>
            <select v-model.number="selectedMonth" class="select" @change="load">
              <option v-for="month in 12" :key="month" :value="month">{{ month }} 月</option>
            </select>
            <button class="rounded-lg bg-emerald-700 px-3 py-2 text-sm text-white" @click="goCurrentMonth">本月</button>
          </div>
        </div>

        <div class="mt-5 grid grid-cols-7 gap-2 text-center text-xs text-slate-500">
          <div v-for="week in weekLabels" :key="week">{{ week }}</div>
        </div>

        <div class="mt-2 grid grid-cols-7 gap-1 w-fit">
          <div
            v-for="cell in calendarCells"
            :key="cell.key"
            :title="tooltip(cell)"
            :class="[
              'h-7 w-7 rounded-md border flex items-center justify-center text-[10px] transition',
              cell.inMonth ? colorClass(cell) : 'bg-transparent border-transparent text-transparent'
            ]"
          >
            <span :class="cell.mood ? 'text-white font-semibold drop-shadow-sm' : 'text-slate-400'">
              {{ cell.day || '' }}
            </span>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap gap-3 text-xs text-slate-600">
          <span v-for="item in legend" :key="item.label" class="flex items-center gap-1">
            <i :class="['h-3 w-3 rounded-sm inline-block', item.className]" />
            {{ item.text }}
          </span>
        </div>
      </section>

      <section class="grid gap-3 md:grid-cols-3">
        <div class="bg-white rounded-2xl p-4 shadow-sm">
          <p class="text-xs text-slate-500">当月记录数</p>
          <p class="text-3xl font-bold text-slate-900 mt-2">{{ summary?.total_count || 0 }}</p>
        </div>
        <div class="bg-white rounded-2xl p-4 shadow-sm md:col-span-2">
          <p class="text-xs text-slate-500 mb-3">当月情绪分布</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="item in moodStats" :key="item.label" class="rounded-full bg-slate-100 px-3 py-1 text-sm">
              {{ moodText(item.label) }} {{ item.count }}
            </span>
            <span v-if="moodStats.length === 0" class="text-sm text-slate-400">暂无记录</span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getMoodCalendar, type MoodDay, type MoodSummary } from '../api/mood'

interface CalendarCell {
  key: string
  date?: string
  day?: number
  inMonth: boolean
  mood?: MoodDay
}

const sid = ref(localStorage.getItem('sid') || crypto.randomUUID())
const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1)
const summary = ref<MoodSummary | null>(null)

const weekLabels = ['一', '二', '三', '四', '五', '六', '日']
const yearOptions = computed(() => {
  const current = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, index) => current - index)
})

const legend = [
  { label: 'happy', text: '开心', className: 'bg-amber-400' },
  { label: 'neutral', text: '平静', className: 'bg-emerald-300' },
  { label: 'anxious', text: '焦虑', className: 'bg-orange-400' },
  { label: 'sad', text: '悲伤', className: 'bg-blue-400' },
  { label: 'angry', text: '生气', className: 'bg-red-500' },
  { label: 'surprised', text: '惊讶', className: 'bg-violet-400' },
  { label: 'empty', text: '无记录', className: 'bg-slate-100' }
]

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  void load()
})

const load = async () => {
  const { data } = await getMoodCalendar(sid.value, selectedYear.value, selectedMonth.value)
  summary.value = data
}

const goCurrentMonth = async () => {
  const current = new Date()
  selectedYear.value = current.getFullYear()
  selectedMonth.value = current.getMonth() + 1
  await load()
}

const calendarCells = computed<CalendarCell[]>(() => {
  const moodMap = new Map((summary.value?.days || []).map(day => [day.date, day]))
  const firstDay = new Date(selectedYear.value, selectedMonth.value - 1, 1)
  const lastDate = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
  const mondayBasedOffset = (firstDay.getDay() + 6) % 7
  const cells: CalendarCell[] = []

  for (let i = 0; i < mondayBasedOffset; i += 1) {
    cells.push({ key: `empty-start-${i}`, inMonth: false })
  }

  for (let day = 1; day <= lastDate; day += 1) {
    const date = `${selectedYear.value}-${`${selectedMonth.value}`.padStart(2, '0')}-${`${day}`.padStart(2, '0')}`
    cells.push({ key: date, date, day, inMonth: true, mood: moodMap.get(date) })
  }

  while (cells.length % 7 !== 0) {
    cells.push({ key: `empty-end-${cells.length}`, inMonth: false })
  }

  return cells
})

const moodStats = computed(() =>
  Object.entries(summary.value?.mood_count || {})
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
)

const moodText = (mood: string) => {
  const map: Record<string, string> = {
    happy: '开心',
    neutral: '平静',
    anxious: '焦虑',
    sad: '悲伤',
    angry: '生气',
    surprised: '惊讶'
  }
  return map[mood] || mood
}

const colorClass = (cell: CalendarCell) => {
  if (!cell.mood) return 'bg-slate-100 border-slate-200'
  const strong = cell.mood.count >= 3
  const map: Record<string, string> = {
    happy: strong ? 'bg-amber-500 border-amber-500' : 'bg-amber-300 border-amber-300',
    neutral: strong ? 'bg-emerald-500 border-emerald-500' : 'bg-emerald-300 border-emerald-300',
    anxious: strong ? 'bg-orange-500 border-orange-500' : 'bg-orange-300 border-orange-300',
    sad: strong ? 'bg-blue-500 border-blue-500' : 'bg-blue-300 border-blue-300',
    angry: strong ? 'bg-red-600 border-red-600' : 'bg-red-400 border-red-400',
    surprised: strong ? 'bg-violet-500 border-violet-500' : 'bg-violet-300 border-violet-300'
  }
  return map[cell.mood.mood_label] || 'bg-slate-300 border-slate-300'
}

const tooltip = (cell: CalendarCell) => {
  if (!cell.inMonth || !cell.date) return ''
  if (!cell.mood) return `${cell.date} 无记录`
  const sources = Object.entries(cell.mood.source_count)
    .map(([source, count]) => `${source}:${count}`)
    .join(', ')
  return `${cell.date} ${moodText(cell.mood.mood_label)}，${cell.mood.count} 条，${sources}`
}
</script>

<style scoped>
.select {
  border: 1px solid rgb(209 213 219);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: white;
  font-size: 0.875rem;
}
</style>
