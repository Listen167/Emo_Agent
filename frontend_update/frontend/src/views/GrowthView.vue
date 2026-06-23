<template>
  <div class="growth-center">
    <header v-develop class="growth-header">
      <div>
        <span class="kodak-chip">Growth Lab</span>
        <h1 class="script-title">成长中心</h1>
        <p>把情绪陪伴、长期记忆、周报和隐私控制收束成一个可商业化的用户价值闭环。</p>
      </div>
      <div class="growth-score">
        <span>TRUST</span>
        <strong>{{ trustScore }}</strong>
        <small>隐私与连续使用指数</small>
      </div>
    </header>

    <main class="growth-layout">
      <section class="growth-main">
        <article v-develop="80" class="weekly-card">
          <span class="report-cover-strip" aria-hidden="true"></span>
          <div class="section-title-row">
            <div>
              <span class="eyebrow">WEEKLY FILM REPORT</span>
              <h2>本周胶片报告</h2>
            </div>
            <button class="print-button" type="button" @click="downloadReport">导出报告</button>
          </div>

          <div class="report-grid">
            <div>
              <span>本周主线</span>
              <strong>{{ weeklyTheme }}</strong>
              <p>{{ setup.weeklyGoal || '每天留下一次真实记录' }}</p>
            </div>
            <div>
              <span>陪伴策略</span>
              <strong>{{ personalityLabel }}</strong>
              <p>{{ personalityNote }}</p>
            </div>
            <div>
              <span>成长线索</span>
              <strong>{{ memories.length }}</strong>
              <p>已沉淀长期记忆，用于后续个性化回应。</p>
            </div>
          </div>

          <div class="insight-list">
            <p v-for="item in weeklyInsights" :key="item">{{ item }}</p>
          </div>
        </article>

        <article v-develop="120" class="memory-card">
          <div class="section-title-row">
            <div>
              <span class="eyebrow">LONG MEMORY</span>
              <h2>小曦长期记忆</h2>
            </div>
            <button class="ghost-button" type="button" @click="addMemory">保存记忆</button>
          </div>

          <div class="memory-form">
            <select v-model="memoryDraft.category">
              <option value="目标">目标</option>
              <option value="压力源">压力源</option>
              <option value="偏好">偏好</option>
              <option value="重要事件">重要事件</option>
            </select>
            <input v-model="memoryDraft.content" placeholder="例如：最近在准备前端实习，希望被提醒复盘项目。" @keydown.enter.prevent="addMemory" />
          </div>

          <div class="memory-list">
            <article
              v-for="memory in memories"
              :key="memory.id"
              :class="['memory-item', { 'memory-item-new': memory.id === lastAddedMemoryId }]"
            >
              <span>{{ memory.category }}</span>
              <p>{{ memory.content }}</p>
              <button type="button" @click="removeMemory(memory.id)">删除</button>
            </article>
            <div v-if="memories.length === 0" class="empty-box">还没有长期记忆。先保存一个目标或偏好。</div>
          </div>
        </article>

        <article v-develop="160" class="privacy-card">
          <div class="section-title-row">
            <div>
              <span class="eyebrow">PRIVACY BY DESIGN</span>
              <h2>隐私、安全与数据控制</h2>
            </div>
            <button class="print-button danger" type="button" @click="clearLocalData">清除本地数据</button>
          </div>

          <div class="privacy-grid">
            <label class="toggle-row">
              <input v-model="privacy.privateMode" type="checkbox" @change="savePrivacy" />
              <span>
                <strong>隐私模式</strong>
                <small>默认减少公开分享，适合情绪记录和求职材料。</small>
              </span>
            </label>
            <label class="toggle-row">
              <input v-model="privacy.anonymousDefault" type="checkbox" @change="savePrivacy" />
              <span>
                <strong>广场默认匿名</strong>
                <small>用于公开社区时保护身份，后端可继续接匿名发布字段。</small>
              </span>
            </label>
            <label class="toggle-row">
              <input v-model="privacy.crisisGuard" type="checkbox" @change="savePrivacy" />
              <span>
                <strong>危机表达安全提示</strong>
                <small>出现高风险表达时，引导用户联系可信赖的人或专业资源。</small>
              </span>
            </label>
          </div>

          <div class="data-actions">
            <button class="ghost-button" type="button" @click="exportUserData">导出我的数据</button>
            <button class="ghost-button" type="button" @click="seedDemo">生成演示数据</button>
          </div>
        </article>
      </section>

      <aside class="growth-side">
        <section v-develop="100" class="persona-panel">
          <span class="eyebrow">XIAO XI MODE</span>
          <h2>小曦人格</h2>
          <div class="persona-options">
            <button
              v-for="item in personalityOptions"
              :key="item.key"
              :class="{ active: personality === item.key }"
              type="button"
              @click="setPersonality(item.key)"
            >
              <strong>{{ item.label }}</strong>
              <small>{{ item.note }}</small>
            </button>
          </div>
        </section>

        <section v-develop="140" class="setup-panel">
          <span class="eyebrow">USER PROFILE</span>
          <h2>首次档案</h2>
          <dl>
            <div>
              <dt>昵称</dt>
              <dd>{{ setup.nickname || '胶片旅人' }}</dd>
            </div>
            <div>
              <dt>当前状态</dt>
              <dd>{{ setup.currentState || '等待记录' }}</dd>
            </div>
            <div>
              <dt>核心场景</dt>
              <dd>{{ setup.focus || '情绪陪伴' }}</dd>
            </div>
          </dl>
        </section>

        <section v-develop="180" class="safety-panel">
          <span class="eyebrow">COMMERCIAL READY</span>
          <h2>落地能力</h2>
          <ul>
            <li>首次引导：降低冷启动流失</li>
            <li>周报：建立每周回访理由</li>
            <li>长期记忆：提升陪伴粘性</li>
            <li>数据控制：增强用户信任</li>
          </ul>
        </section>
      </aside>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import {
  clearGrowthState,
  createGrowthMemory,
  deleteGrowthMemory,
  getGrowthState,
  updateGrowthProfile,
  type GrowthMemoryItem,
  type GrowthProfileUpdate,
  type GrowthStateItem,
} from '../api/growth'
import { createClientId } from '../utils/id'

interface SetupData {
  nickname?: string
  currentState?: string
  focus?: string
  personality?: string
  weeklyGoal?: string
  completed?: boolean
  createdAt?: string
}

interface MemoryItem {
  id: number | string
  category: string
  content: string
  createdAt: string
}

const sid = ref(localStorage.getItem('sid') || createClientId())
const setup = reactive<SetupData>(loadJson('u-life-user-setup-v1', {}))
const memories = ref<MemoryItem[]>(loadJson('u-life-long-memory-v1', []))
const personality = ref(localStorage.getItem('u-life-xiaoxi-personality-v1') || setup.personality || 'warm')
const memoryDraft = reactive({ category: '目标', content: '' })
const lastAddedMemoryId = ref<number | string | null>(null)
let memoryAnimationTimer: number | undefined
const privacy = reactive({
  privateMode: localStorage.getItem('u-life-privacy-mode-v1') !== 'false',
  anonymousDefault: localStorage.getItem('u-life-plaza-anonymous-v1') === 'true',
  crisisGuard: localStorage.getItem('u-life-crisis-guard-v1') !== 'false',
})

onMounted(async () => {
  localStorage.setItem('sid', sid.value)
  await loadGrowthState()
})

const personalityOptions = [
  { key: 'warm', label: '温柔陪伴型', note: '优先共情、安抚和稳定情绪。' },
  { key: 'coach', label: '成长教练型', note: '更常给计划、复盘和行动建议。' },
  { key: 'rational', label: '理性分析型', note: '帮你拆解问题、权衡取舍。' },
  { key: 'bright', label: '元气鼓励型', note: '语气更轻快，适合日常打卡。' },
] as const

const personalityLabel = computed(() => personalityOptions.find(item => item.key === personality.value)?.label || '温柔陪伴型')
const personalityNote = computed(() => personalityOptions.find(item => item.key === personality.value)?.note || '优先共情、安抚和稳定情绪。')
const weeklyTheme = computed(() => setup.focus ? `${setup.focus} · ${weekRangeText()}` : `情绪陪伴 · ${weekRangeText()}`)
const trustScore = computed(() => Math.min(99, 62 + memories.value.length * 6 + Number(privacy.privateMode) * 8 + Number(privacy.crisisGuard) * 7))
const weeklyInsights = computed(() => [
  `${setup.nickname || '你'}这周的核心目标是：${setup.weeklyGoal || '每天留下一次真实记录'}。`,
  `小曦将以“${personalityLabel.value}”回应，优先匹配你的当前状态：${setup.currentState || '等待记录'}。`,
  memories.value.length
    ? `已经沉淀 ${memories.value.length} 条长期记忆，可以支撑更连续的陪伴。`
    : '还没有长期记忆，建议先记录一个目标、压力源或偏好。',
])

onBeforeUnmount(() => {
  if (memoryAnimationTimer) window.clearTimeout(memoryAnimationTimer)
})

function loadJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) as T : fallback
  } catch {
    return fallback
  }
}

function weekRangeText() {
  const now = new Date()
  const day = (now.getDay() + 6) % 7
  const start = new Date(now)
  start.setDate(now.getDate() - day)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  const format = (date: Date) => `${date.getMonth() + 1}.${date.getDate()}`
  return `${format(start)}-${format(end)}`
}

function persistMemories() {
  localStorage.setItem('u-life-long-memory-v1', JSON.stringify(memories.value))
  window.dispatchEvent(new CustomEvent('u-life-settings-changed'))
}

function cacheSetup() {
  localStorage.setItem('u-life-user-setup-v1', JSON.stringify(setup))
}

function applyGrowthState(data: GrowthStateItem) {
  setup.nickname = data.profile.nickname || '胶片旅人'
  setup.currentState = data.profile.current_state || ''
  setup.focus = data.profile.focus || ''
  setup.personality = data.profile.personality || 'warm'
  setup.weeklyGoal = data.profile.weekly_goal || '每天留下一次真实记录'
  setup.completed = data.profile.setup_completed
  setup.createdAt = data.profile.created_at
  personality.value = data.profile.personality || 'warm'
  privacy.privateMode = data.profile.private_mode
  privacy.anonymousDefault = data.profile.anonymous_default
  privacy.crisisGuard = data.profile.crisis_guard
  memories.value = data.memories.map(mapMemory)
  cacheSetup()
  localStorage.setItem('u-life-xiaoxi-personality-v1', personality.value)
  savePrivacyLocal()
  persistMemories()
}

function mapMemory(memory: GrowthMemoryItem): MemoryItem {
  return {
    id: memory.id,
    category: memory.category,
    content: memory.content,
    createdAt: memory.created_at,
  }
}

async function loadGrowthState() {
  try {
    const { data } = await getGrowthState(sid.value)
    applyGrowthState(data)
  } catch {
    // 离线或后端未启动时保留本地缓存，避免成长中心不可用。
  }
}

async function persistProfileToServer(extra: Partial<GrowthProfileUpdate> = {}) {
  try {
    const { data } = await updateGrowthProfile({
      session_id: sid.value,
      nickname: setup.nickname || '胶片旅人',
      current_state: setup.currentState || null,
      focus: setup.focus || null,
      personality: personality.value,
      weekly_goal: setup.weeklyGoal || '每天留下一次真实记录',
      setup_completed: Boolean(setup.completed),
      private_mode: privacy.privateMode,
      anonymous_default: privacy.anonymousDefault,
      crisis_guard: privacy.crisisGuard,
      ...extra,
    })
    applyGrowthState(data)
  } catch {
    cacheSetup()
  }
}

async function addMemory() {
  const content = memoryDraft.content.trim()
  if (!content) return
  const localId = createClientId()
  const optimisticMemory = {
    id: localId,
    category: memoryDraft.category,
    content,
    createdAt: new Date().toISOString(),
  }
  memories.value = [
    optimisticMemory,
    ...memories.value,
  ]
  lastAddedMemoryId.value = localId
  if (memoryAnimationTimer) window.clearTimeout(memoryAnimationTimer)
  memoryAnimationTimer = window.setTimeout(() => {
    lastAddedMemoryId.value = null
  }, 1100)
  memoryDraft.content = ''
  persistMemories()
  try {
    const { data } = await createGrowthMemory(sid.value, optimisticMemory.category, optimisticMemory.content)
    memories.value = memories.value.map(item => item.id === localId ? mapMemory(data) : item)
    lastAddedMemoryId.value = data.id
    persistMemories()
  } catch {
    // 本地缓存已保存，后端恢复后可重新录入或导出数据。
  }
}

async function removeMemory(id: number | string) {
  memories.value = memories.value.filter(item => item.id !== id)
  persistMemories()
  if (typeof id === 'number') {
    try {
      await deleteGrowthMemory(id, sid.value)
    } catch {
      // 删除失败时保持本地结果，不阻塞界面操作。
    }
  }
}

async function setPersonality(value: string) {
  personality.value = value
  localStorage.setItem('u-life-xiaoxi-personality-v1', value)
  window.dispatchEvent(new CustomEvent('u-life-settings-changed'))
  await persistProfileToServer({ personality: value })
}

function savePrivacyLocal() {
  localStorage.setItem('u-life-privacy-mode-v1', String(privacy.privateMode))
  localStorage.setItem('u-life-plaza-anonymous-v1', String(privacy.anonymousDefault))
  localStorage.setItem('u-life-crisis-guard-v1', String(privacy.crisisGuard))
}

async function savePrivacy() {
  savePrivacyLocal()
  window.dispatchEvent(new CustomEvent('u-life-settings-changed'))
  await persistProfileToServer()
}

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

function exportUserData() {
  const keys = [
    'sid',
    'u-life-user-setup-v1',
    'u-life-xiaoxi-personality-v1',
    'u-life-long-memory-v1',
    'u-life-privacy-mode-v1',
    'u-life-plaza-anonymous-v1',
    'u-life-crisis-guard-v1',
    'emo-agent-resume-v1',
  ]
  const data = Object.fromEntries(keys.map(key => [key, localStorage.getItem(key)]))
  downloadJson('u-life-user-data.json', data)
}

function downloadReport() {
  downloadJson('u-life-weekly-film-report.json', {
    theme: weeklyTheme.value,
    goal: setup.weeklyGoal,
    personality: personalityLabel.value,
    memories: memories.value,
    insights: weeklyInsights.value,
    generatedAt: new Date().toISOString(),
  })
}

function seedDemo() {
  if (!setup.nickname) setup.nickname = '胶片旅人'
  setup.focus = setup.focus || '自我理解'
  setup.currentState = setup.currentState || '准备求职，需要成长建议'
  setup.weeklyGoal = setup.weeklyGoal || '整理一次情绪波动，并完成简历项目经历复盘'
  cacheSetup()
  if (memories.value.length === 0) {
    memories.value = [
      { id: createClientId(), category: '目标', content: '希望在就业季前完成一份可投递的前端简历。', createdAt: new Date().toISOString() },
      { id: createClientId(), category: '压力源', content: '容易因为比较同学进度而焦虑，需要被提醒回到自己的节奏。', createdAt: new Date().toISOString() },
    ]
    persistMemories()
  }
  void persistProfileToServer()
}

async function clearLocalData() {
  const ok = window.confirm('确认清除本地成长档案、长期记忆和隐私设置？简历草稿也会被清除。')
  if (!ok) return
  ;[
    'u-life-user-setup-v1',
    'u-life-xiaoxi-personality-v1',
    'u-life-long-memory-v1',
    'u-life-privacy-mode-v1',
    'u-life-plaza-anonymous-v1',
    'u-life-crisis-guard-v1',
    'emo-agent-resume-v1',
  ].forEach(key => localStorage.removeItem(key))
  try {
    await clearGrowthState(sid.value)
  } catch {
    // 后端不可用时只清本地数据。
  }
  window.location.reload()
}
</script>

<style scoped>
.growth-center {
  min-height: 100vh;
  padding: 26px 30px 42px;
}

.growth-header,
.weekly-card,
.memory-card,
.privacy-card,
.persona-panel,
.setup-panel,
.safety-panel {
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 78%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.growth-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px;
}

.kodak-chip,
.eyebrow {
  display: inline-block;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.kodak-chip {
  padding: 5px 12px;
  color: var(--journal-ink);
  background: var(--journal-kodak);
}

.growth-header h1 {
  margin: 8px 0 0;
  font-size: clamp(44px, 6vw, 72px);
  line-height: 0.9;
}

.growth-header p {
  max-width: 720px;
  margin: 8px 0 0;
  color: var(--journal-muted);
  font-size: 14px;
}

.growth-score {
  align-self: center;
  min-width: 150px;
  padding: 16px;
  border: 2px solid var(--journal-stamp);
  color: var(--journal-stamp);
  text-align: center;
  rotate: 5deg;
}

.growth-score span,
.growth-score strong,
.growth-score small {
  display: block;
}

.growth-score strong {
  font-size: 48px;
  line-height: 1;
}

.growth-score small {
  color: var(--journal-muted);
  font-size: 11px;
}

.growth-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  padding-top: 26px;
}

.growth-main {
  display: grid;
  gap: 20px;
}

.weekly-card,
.memory-card,
.privacy-card,
.persona-panel,
.setup-panel,
.safety-panel {
  padding: 22px;
}

.weekly-card {
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
}

.weekly-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 12px;
  background:
    linear-gradient(180deg, var(--journal-stamp), #3e3228),
    repeating-linear-gradient(180deg, transparent 0 12px, rgb(255 248 232 / 32%) 12px 18px);
  opacity: 0.9;
}

.weekly-card::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, transparent 0 49%, rgb(62 50 40 / 16%) 50%, rgb(255 248 232 / 92%) 52% 100%);
  transform-origin: 100% 0;
  transition: transform 0.26s ease;
  pointer-events: none;
}

.weekly-card:hover::after {
  transform: rotate(-10deg);
}

.report-cover-strip {
  position: absolute;
  right: 92px;
  top: 20px;
  width: 88px;
  height: 18px;
  border: 1px solid rgb(62 50 40 / 12%);
  background: rgb(232 195 108 / 56%);
  rotate: 4deg;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

h2 {
  margin: 4px 0 0;
  color: var(--journal-ink);
  font-size: 22px;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.report-grid > div {
  padding: 14px;
  border: 1px dashed rgb(62 50 40 / 18%);
  background: rgb(253 251 247 / 58%);
}

.report-grid span,
.report-grid strong {
  display: block;
}

.report-grid span {
  color: var(--journal-muted);
  font-size: 12px;
  font-weight: 700;
}

.report-grid strong {
  margin-top: 5px;
  color: var(--journal-ink);
  font-size: 19px;
}

.report-grid p,
.insight-list p,
.memory-item p,
.toggle-row small,
.safety-panel li,
dd {
  color: var(--journal-muted);
  font-size: 13px;
  line-height: 1.6;
}

.insight-list {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.insight-list p {
  margin: 0;
  padding: 11px 13px;
  border-left: 4px solid var(--journal-stamp);
  background: rgb(253 251 247 / 64%);
}

.memory-form {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 10px;
  margin-top: 16px;
}

select,
input {
  width: 100%;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.72rem 0.8rem;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
}

.memory-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.memory-item {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  background:
    linear-gradient(90deg, rgb(253 251 247 / 84%), rgb(255 248 232 / 58%));
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 68%);
}

.memory-item span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  border-radius: 999px;
  background: rgb(232 195 108 / 42%);
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.memory-item p {
  margin: 0;
}

.memory-item button {
  color: var(--journal-stamp);
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.memory-item-new {
  animation: memoryCapsuleStore 0.78s cubic-bezier(0.2, 0.9, 0.2, 1) both;
}

.empty-box {
  padding: 28px;
  border: 1px dashed rgb(62 50 40 / 24%);
  color: var(--journal-muted);
  text-align: center;
}

.privacy-grid {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.toggle-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  border: 1px dashed rgb(62 50 40 / 18%);
  background: rgb(253 251 247 / 52%);
}

.toggle-row input {
  width: 18px;
  height: 18px;
  margin-top: 2px;
}

.toggle-row strong,
.toggle-row small {
  display: block;
}

.data-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.ghost-button,
.print-button {
  min-height: 38px;
  border-radius: 10px;
  padding: 0 14px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.ghost-button {
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 70%);
}

.print-button {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 16%);
}

.print-button.danger {
  background: var(--journal-stamp);
}

.growth-side {
  position: sticky;
  top: 24px;
  display: grid;
  gap: 16px;
  height: fit-content;
}

.persona-options {
  display: grid;
  gap: 9px;
  margin-top: 14px;
}

.persona-options button {
  padding: 12px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 12px;
  color: var(--journal-ink);
  text-align: left;
  background: rgb(253 251 247 / 66%);
  cursor: pointer;
}

.persona-options button.active {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
}

.persona-options strong,
.persona-options small {
  display: block;
}

.persona-options small {
  margin-top: 4px;
  color: inherit;
  opacity: 0.72;
  font-size: 12px;
  line-height: 1.5;
}

dl {
  display: grid;
  gap: 11px;
  margin: 14px 0 0;
}

dt {
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

dd {
  margin: 4px 0 0;
}

.safety-panel ul {
  display: grid;
  gap: 8px;
  margin: 14px 0 0;
  padding-left: 18px;
}

@keyframes memoryCapsuleStore {
  0% {
    opacity: 0;
    transform: translateY(-14px) scale(0.94);
    filter: blur(6px);
  }
  62% {
    opacity: 1;
    transform: translateY(3px) scale(1.02);
    filter: blur(0);
  }
  100% {
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 980px) {
  .growth-center {
    padding: 16px 14px 26px;
  }

  .growth-layout {
    display: block;
  }

  .growth-side {
    position: relative;
    top: auto;
    margin-top: 18px;
  }

  .report-grid {
    grid-template-columns: 1fr;
  }

}

@media (max-width: 680px) {
  .growth-header {
    display: block;
    padding: 20px;
  }

  .growth-score {
    margin-top: 16px;
  }

  .section-title-row,
  .memory-form,
  .memory-item {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>

