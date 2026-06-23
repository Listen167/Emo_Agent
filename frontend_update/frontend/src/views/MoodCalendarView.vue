<template>
  <div class="mood-journal">
    <header v-develop class="mood-header">
      <div>
        <span class="kodak-chip">Exposure Log</span>
        <h1 class="script-title">拍摄记录</h1>
        <p>查看曝光曲线，重温拍摄那一刻的 Sunny 26°C。</p>
      </div>
      <div class="meter-dial">
        <span class="meter-needle" aria-hidden="true"></span>
        <span>ISO</span>
        <strong>400</strong>
      </div>
    </header>

    <main class="mood-layout">
      <section v-develop="80" class="calendar-card">
        <span class="washi-tape"></span>
        <div class="calendar-toolbar">
          <div>
            <h2>{{ selectedYear }} 年 {{ selectedMonth }} 月</h2>
            <p>每个方块代表一天，颜色表示当天主要情绪，深浅表示记录次数。</p>
          </div>

          <div class="select-row">
            <select v-model.number="selectedYear" class="select" @change="load">
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }} 年</option>
            </select>
            <select v-model.number="selectedMonth" class="select" @change="load">
              <option v-for="month in 12" :key="month" :value="month">{{ month }} 月</option>
            </select>
            <button @click="goCurrentMonth">本月</button>
          </div>
        </div>

        <div class="week-row">
          <div v-for="week in weekLabels" :key="week">{{ week }}</div>
        </div>

        <div class="calendar-grid">
          <div
            v-for="cell in calendarCells"
            :key="cell.key"
            :title="tooltip(cell)"
            :class="['calendar-cell', cell.inMonth ? colorClass(cell) : 'empty-cell']"
          >
            <span :class="cell.mood ? 'marked-day' : 'quiet-day'">
              {{ cell.day || '' }}
            </span>
          </div>
        </div>

        <div class="legend-row">
          <span v-for="item in legend" :key="item.label">
            <i :class="item.className" />
            {{ item.text }}
          </span>
        </div>
      </section>

      <section class="stats-board">
        <div v-develop="120" class="stat-card count-card">
          <span>SHOT COUNT</span>
          <strong>{{ summary?.total_count || 0 }}</strong>
          <p>当月记录数</p>
        </div>
        <div v-develop="160" class="stat-card distribution-card">
          <span>EMOTION CONTACT SHEET</span>
          <div class="mood-pills">
            <span v-for="item in moodStats" :key="item.label">
              {{ moodText(item.label) }} {{ item.count }}
            </span>
            <em v-if="moodStats.length === 0">暂无记录</em>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getMoodCalendar, type MoodDay, type MoodSummary } from '../api/mood'
import { createClientId } from '../utils/id'

interface CalendarCell {
  key: string
  date?: string
  day?: number
  inMonth: boolean
  mood?: MoodDay
}

const sid = ref(localStorage.getItem('sid') || createClientId())
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
  if (!cell.mood) return 'no-mood'
  const strong = cell.mood.count >= 3
  const map: Record<string, string> = {
    happy: strong ? 'mood-happy strong' : 'mood-happy',
    neutral: strong ? 'mood-neutral strong' : 'mood-neutral',
    anxious: strong ? 'mood-anxious strong' : 'mood-anxious',
    sad: strong ? 'mood-sad strong' : 'mood-sad',
    angry: strong ? 'mood-angry strong' : 'mood-angry',
    surprised: strong ? 'mood-surprised strong' : 'mood-surprised'
  }
  return map[cell.mood.mood_label] || 'no-mood'
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
.mood-journal {
  min-height: 100vh;
  padding: 26px 30px 42px;
}

.mood-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.mood-header h1 {
  margin: 8px 0 0;
  font-size: clamp(44px, 6vw, 72px);
  line-height: 0.9;
}

.mood-header p {
  margin: 8px 0 0;
  color: var(--journal-muted);
  font-size: 14px;
}

.kodak-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.meter-dial {
  position: relative;
  overflow: hidden;
  width: 112px;
  height: 112px;
  align-self: center;
  display: grid;
  place-items: center;
  border-radius: 999px;
  color: #fff8e8;
  background: radial-gradient(circle at center, #3e3228 0 30%, #20150f 31% 100%);
  border: 8px solid #f5e8ce;
  box-shadow: inset 0 0 0 2px rgb(255 255 255 / 18%), 0 12px 26px rgb(62 50 40 / 22%);
}

.meter-dial::before {
  content: "";
  position: absolute;
  inset: 8px;
  border-radius: inherit;
  background:
    repeating-conic-gradient(from 0deg, rgb(255 255 255 / 12%) 0deg 2deg, transparent 2deg 9deg),
    radial-gradient(circle at center, transparent 0 24%, rgb(255 255 255 / 8%) 25% 26%, transparent 27% 100%);
  animation: meterRecordSpin 7.5s linear infinite;
}

.meter-dial::after {
  content: "";
  position: absolute;
  inset: 37px;
  border-radius: 999px;
  background: radial-gradient(circle, #f5e8ce 0 18%, #3e3228 19% 44%, #120c09 45% 100%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 22%),
    0 0 0 1px rgb(255 255 255 / 18%);
}

.meter-dial:hover::before {
  animation-duration: 3.8s;
}

.meter-dial span,
.meter-dial strong {
  position: relative;
  z-index: 2;
  display: block;
  text-align: center;
}

.meter-needle {
  position: absolute !important;
  z-index: 3 !important;
  left: 50%;
  top: 13px;
  width: 2px;
  height: 40px;
  border-radius: 999px;
  background: #f7d66c;
  box-shadow: 0 0 10px rgb(247 214 108 / 56%);
  transform-origin: 50% 42px;
  animation: exposureNeedle 3.8s ease-in-out infinite;
}

.meter-needle::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -7px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #fff8e8;
  transform: translateX(-50%);
}

.meter-dial span {
  align-self: end;
  font-size: 11px;
}

.meter-dial strong {
  align-self: start;
  font-size: 28px;
}

@keyframes meterRecordSpin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes exposureNeedle {
  0%,
  100% {
    transform: translateX(-50%) rotate(-18deg);
  }
  50% {
    transform: translateX(-50%) rotate(20deg);
  }
}

.mood-layout {
  display: grid;
  gap: 22px;
  padding-top: 26px;
}

.calendar-card {
  position: relative;
  padding: 24px;
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 18px 42px rgb(62 50 40 / 16%);
  clip-path: polygon(0 1%, 99% 0, 100% 98%, 1% 100%);
}

.washi-tape {
  position: absolute;
  top: -12px;
  left: 44px;
  width: 128px;
  height: 28px;
  rotate: -3deg;
  background: rgb(232 195 108 / 58%);
  border: 1px solid rgb(62 50 40 / 10%);
}

.calendar-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 16px;
}

.calendar-toolbar h2 {
  margin: 0;
  color: var(--journal-ink);
  font-size: 24px;
}

.calendar-toolbar p {
  margin: 6px 0 0;
  color: var(--journal-muted);
  font-size: 13px;
}

.select-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.select {
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.5rem 0.75rem;
  background: rgb(253 251 247 / 82%);
  color: var(--journal-ink);
  font-size: 0.875rem;
}

.select-row button {
  border-radius: 10px;
  padding: 0.5rem 0.9rem;
  color: #fff8e8;
  font-size: 0.875rem;
  font-weight: 700;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.week-row,
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(36px, 1fr));
  gap: 8px;
}

.week-row {
  margin-top: 22px;
  color: var(--journal-muted);
  text-align: center;
  font-size: 12px;
}

.calendar-grid {
  margin-top: 10px;
}

.calendar-cell {
  position: relative;
  overflow: hidden;
  min-height: 42px;
  display: grid;
  place-items: center;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.calendar-cell::after {
  content: "";
  position: absolute;
  inset: -35%;
  background: radial-gradient(circle, rgb(255 248 232 / 82%) 0 18%, transparent 48%);
  opacity: 0;
  transform: scale(0.72);
  transition: opacity 0.22s ease, transform 0.22s ease;
  pointer-events: none;
}

.calendar-cell:hover {
  transform: translateY(-2px);
  filter: saturate(1.08);
  box-shadow: 0 8px 18px rgb(62 50 40 / 14%), inset 0 0 0 2px rgb(255 248 232 / 58%);
}

.calendar-cell:hover::after {
  opacity: 0.72;
  transform: scale(1);
}

.calendar-cell span {
  position: relative;
  z-index: 1;
}

.empty-cell {
  opacity: 0;
}

.marked-day {
  color: #fff8e8;
  font-weight: 700;
  text-shadow: 0 1px 2px rgb(62 50 40 / 36%);
}

.quiet-day {
  color: rgb(62 50 40 / 46%);
}

.no-mood {
  background: rgb(253 251 247 / 72%);
}

.mood-happy { background: #e8c36c; }
.mood-neutral { background: #87a777; }
.mood-anxious { background: #d9894d; }
.mood-sad { background: #6f91a8; }
.mood-angry { background: #c85a54; }
.mood-surprised { background: #9a7aa8; }
.strong { box-shadow: inset 0 0 0 3px rgb(62 50 40 / 18%); }

.legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
  color: var(--journal-muted);
  font-size: 12px;
}

.legend-row span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-row i {
  width: 12px;
  height: 12px;
  display: inline-block;
  border-radius: 3px;
}

.legend-row .bg-amber-400 { background: #e8c36c; }
.legend-row .bg-emerald-300 { background: #87a777; }
.legend-row .bg-orange-400 { background: #d9894d; }
.legend-row .bg-blue-400 { background: #6f91a8; }
.legend-row .bg-red-500 { background: #c85a54; }
.legend-row .bg-violet-400 { background: #9a7aa8; }
.legend-row .bg-slate-100 { background: #fdfbf7; border: 1px solid rgb(62 50 40 / 14%); }

.stats-board {
  display: grid;
  grid-template-columns: minmax(190px, 260px) minmax(0, 1fr);
  gap: 18px;
}

.stat-card {
  padding: 22px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 78%);
  box-shadow: 0 14px 30px rgb(62 50 40 / 12%);
}

.stat-card > span {
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.count-card strong {
  display: block;
  margin-top: 8px;
  color: var(--journal-ink);
  font-size: 58px;
  line-height: 1;
}

.count-card p {
  margin: 8px 0 0;
  color: var(--journal-muted);
}

.mood-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.mood-pills span,
.mood-pills em {
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  padding: 0.42rem 0.78rem;
  background: rgb(253 251 247 / 74%);
  color: var(--journal-muted);
  font-style: normal;
  font-size: 14px;
}

@media (max-width: 760px) {
  .mood-journal {
    padding: 16px 14px 26px;
  }

  .meter-dial {
    display: none;
  }

  .calendar-card {
    padding: 20px 14px;
  }

  .week-row,
  .calendar-grid {
    grid-template-columns: repeat(7, minmax(32px, 1fr));
    gap: 5px;
  }

  .calendar-cell {
    min-height: 34px;
  }

  .stats-board {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .meter-dial::before,
  .meter-needle {
    animation: none !important;
  }
}
</style>

