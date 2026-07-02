<template>
  <section class="profile-card">
    <button class="profile-summary" type="button" @click="openEditor">
      <span class="profile-avatar">
        <img v-if="profile?.avatar_url" :src="resolveAssetUrl(profile.avatar_url)" alt="用户头像" />
        <span v-else>{{ avatarInitial }}</span>
      </span>
      <span class="profile-copy">
        <strong>{{ displayName }}</strong>
        <small>{{ profile?.motto || '记录每一次快门的心跳' }}</small>
      </span>
    </button>

    <div class="profile-tags">
      <span>{{ genderText }}</span>
      <span v-if="profile?.ebti_type">{{ profile.ebti_type }} · {{ profile.ebti_name || 'EBTI' }}</span>
      <span v-else>EBTI 未测试</span>
    </div>

    <Teleport to="body">
      <Transition name="profile-modal-motion">
        <div v-if="editing" class="profile-modal-mask" @click.self="closeEditor">
          <section class="profile-modal" role="dialog" aria-modal="true" aria-label="编辑个人资料">
            <span v-if="savedStampVisible" class="saved-stamp">PROFILE<br>SAVED</span>

            <header class="profile-modal-header">
              <div>
                <span>PROFILE</span>
                <h2>个人资料</h2>
              </div>
              <button class="close-button" type="button" @click="closeEditor">关闭</button>
            </header>

            <div class="profile-modal-grid">
              <div class="profile-left-column">
                <div :class="['avatar-editor', { 'avatar-editor-flash': avatarChanged }]">
                  <span class="large-avatar">
                    <img v-if="draftAvatarUrl" :src="draftAvatarUrl" alt="用户头像预览" />
                    <span v-else>{{ avatarInitial }}</span>
                  </span>
                  <label class="avatar-upload">
                    更换头像
                    <input type="file" accept="image/*" @change="onAvatarChange" />
                  </label>
                </div>

                <div class="profile-form">
                  <label>
                    <span>昵称</span>
                    <input v-model="draft.nickname" maxlength="40" placeholder="给自己取个名字" />
                  </label>
                  <label>
                    <span>座右铭</span>
                    <textarea v-model="draft.motto" maxlength="160" placeholder="写一句给自己的话" />
                  </label>
                  <label>
                    <span>性别</span>
                    <select v-model="draft.gender">
                      <option value="">不设置</option>
                      <option value="female">女</option>
                      <option value="male">男</option>
                      <option value="nonbinary">非二元</option>
                      <option value="secret">保密</option>
                    </select>
                  </label>
                </div>

                <div class="ebti-panel">
                  <span>首次 EBTI</span>
                  <strong v-if="profile?.ebti_type">{{ profile.ebti_type }} · {{ profile.ebti_name || '已记录' }}</strong>
                  <strong v-else>还没有同步测试结果</strong>
                  <small>完成 EBTI 测试后，这里会自动记录你的首次测试结果。</small>
                </div>

                <footer class="profile-modal-actions">
                  <button class="ghost-button" type="button" @click="closeEditor">取消</button>
                  <button class="save-button" type="button" :disabled="saving" @click="saveProfile">
                    <span class="button-shutter"></span>
                    {{ saving ? '保存中...' : '保存资料' }}
                  </button>
                </footer>
              </div>

              <div class="profile-right-column">
                <section class="mini-mood-panel" aria-label="本月心情日历">
                  <div class="growth-record-head">
                    <div>
                      <span>Mood Calendar</span>
                      <h3>心情日历</h3>
                      <small>{{ moodYear }} 年 {{ moodMonth }} 月</small>
                    </div>
                    <strong class="mood-count-chip">{{ moodSummary?.total_count || 0 }} 条</strong>
                  </div>

                  <div class="mini-mood-toolbar">
                    <select v-model.number="moodYear" @change="loadMoodSnapshot()">
                      <option v-for="year in moodYearOptions" :key="year" :value="year">{{ year }} 年</option>
                    </select>
                    <select v-model.number="moodMonth" @change="loadMoodSnapshot()">
                      <option v-for="month in 12" :key="month" :value="month">{{ month }} 月</option>
                    </select>
                    <button type="button" @click="goCurrentMoodMonth()">本月</button>
                  </div>

                  <div class="mini-mood-stats">
                    <div>
                      <span>当月记录数</span>
                      <strong>{{ moodSummary?.total_count || 0 }}</strong>
                    </div>
                    <div>
                      <span>主要情绪</span>
                      <strong>{{ dominantMoodText }}</strong>
                    </div>
                  </div>

                  <div class="mini-mood-distribution">
                    <span v-for="item in moodStats" :key="item.label">
                      {{ moodText(item.label) }} {{ item.count }}
                    </span>
                    <em v-if="moodStats.length === 0">暂无记录</em>
                  </div>

                  <div class="mini-week-row">
                    <span v-for="week in weekLabels" :key="week">{{ week }}</span>
                  </div>
                  <div class="mini-calendar-grid">
                    <button
                      v-for="cell in miniCalendarCells"
                      :key="cell.key"
                      type="button"
                      :title="moodTooltip(cell)"
                      :class="[
                        'mini-calendar-cell',
                        cell.inMonth ? miniMoodClass(cell) : 'outside-month',
                        { today: cell.date === todayKey, selected: cell.date === selectedMoodDate },
                      ]"
                      :disabled="!cell.inMonth"
                      @click="selectMoodDay(cell)"
                    >
                      <b>{{ cell.day || '' }}</b>
                      <i v-if="cell.mood"></i>
                    </button>
                  </div>

                  <div class="selected-mood-card">
                    <span>{{ selectedMoodCell?.date || '选择一天查看' }}</span>
                    <strong>{{ selectedMoodCell?.mood ? moodText(selectedMoodCell.mood.mood_label) : '暂无心情记录' }}</strong>
                    <small>
                      {{ selectedMoodCell?.mood
                        ? `${selectedMoodCell.mood.count} 条记录 · ${moodSourceText(selectedMoodCell.mood)}`
                        : '当天还没有来自聊天、动态或生活记录的情绪数据。' }}
                    </small>
                  </div>

                  <div class="mini-mood-legend">
                    <span v-for="item in miniMoodLegend" :key="item.label">
                      <i :class="item.className"></i>
                      {{ item.text }}
                    </span>
                  </div>
                </section>

                <section class="growth-record-panel" aria-label="我的成长记录">
                  <div class="growth-record-head">
                    <div>
                      <span>GROWTH RECORD</span>
                      <h3>我的成长记录</h3>
                    </div>
                    <button class="mini-refresh-button" type="button" :disabled="recordsLoading" @click="loadGrowthRecords">
                      {{ recordsLoading ? '同步中' : '同步' }}
                    </button>
                  </div>

                  <div class="growth-stat-grid">
                    <div>
                      <strong>{{ publicRecords.length }}</strong>
                      <span>公开动态</span>
                    </div>
                    <div>
                      <strong>{{ privateRecords.length }}</strong>
                      <span>私密记录</span>
                    </div>
                    <div>
                      <strong>{{ memories.length }}</strong>
                      <span>长期记忆</span>
                    </div>
                  </div>

                  <div class="growth-summary-card">
                    <span>成长中心</span>
                    <strong>{{ weeklyTheme }}</strong>
                    <small>{{ weeklyGoalText }}</small>
                  </div>

                  <div class="record-preview-list">
                    <article v-for="record in previewRecords" :key="record.id" class="record-preview-item">
                      <span :class="['record-visibility-dot', record.visibility === 'public' ? 'public' : 'private']"></span>
                      <div>
                        <strong>{{ record.title || record.content || '未命名记录' }}</strong>
                        <small>
                          {{ record.visibility === 'public' ? '公开' : '私密' }}
                          <template v-if="record.mood_label"> · {{ moodText(record.mood_label) }}</template>
                          · {{ formatRecordTime(record.created_at) }}
                        </small>
                      </div>
                    </article>
                    <p v-if="recordsLoading" class="empty-growth-record">
                      正在同步成长记录...
                    </p>
                    <p v-else-if="previewRecords.length === 0" class="empty-growth-record">
                      还没有动态记录。可以在聊天广场发布公开或私密动态。
                    </p>
                  </div>
                </section>
              </div>
            </div>
          </section>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { getProfile, updateProfile, uploadProfileAvatar, type UserProfile } from '../api/profile'
import { getLifeRecords, type LifeRecordItem } from '../api/life'
import { getMoodCalendar, type MoodDay, type MoodSummary } from '../api/mood'
import { resolveAssetUrl } from '../api/client'

const props = defineProps<{
  sessionId: string
  refreshKey?: number
}>()

const profile = ref<UserProfile | null>(null)
const editing = ref(false)
const saving = ref(false)
const avatarFile = ref<File | null>(null)
const draftAvatarUrl = ref('')
const avatarChanged = ref(false)
const savedStampVisible = ref(false)
const draft = reactive({
  nickname: '',
  motto: '',
  gender: '',
})
const records = ref<LifeRecordItem[]>([])
const recordsLoading = ref(false)
const memories = ref<MemoryItem[]>([])
const setup = ref<SetupData>({})
const moodSummary = ref<MoodSummary | null>(null)
const moodNow = new Date()
const moodYear = ref(moodNow.getFullYear())
const moodMonth = ref(moodNow.getMonth() + 1)
const todayKey = `${moodNow.getFullYear()}-${`${moodNow.getMonth() + 1}`.padStart(2, '0')}-${`${moodNow.getDate()}`.padStart(2, '0')}`
const selectedMoodDate = ref(todayKey)

interface SetupData {
  nickname?: string
  currentState?: string
  focus?: string
  weeklyGoal?: string
}

interface MemoryItem {
  id: string
  category: string
  content: string
  createdAt: string
}

interface MiniCalendarCell {
  key: string
  date?: string
  day?: number
  inMonth: boolean
  mood?: MoodDay
}

const displayName = computed(() => profile.value?.nickname || '胶片旅人')
const avatarInitial = computed(() => displayName.value.slice(0, 1).toUpperCase())
const genderText = computed(() => {
  const map: Record<string, string> = {
    female: '女',
    male: '男',
    nonbinary: '非二元',
    secret: '保密',
  }
  return profile.value?.gender ? map[profile.value.gender] || profile.value.gender : '未设置性别'
})
const publicRecords = computed(() => records.value.filter(record => record.visibility === 'public'))
const privateRecords = computed(() => records.value.filter(record => record.visibility === 'private'))
const previewRecords = computed(() => records.value.slice(0, 4))
const weeklyTheme = computed(() => setup.value.focus ? `${setup.value.focus} · ${weekRangeText()}` : `学生成长 · ${weekRangeText()}`)
const weeklyGoalText = computed(() => setup.value.weeklyGoal || '每天留下一次真实记录')
const weekLabels = ['一', '二', '三', '四', '五', '六', '日']
const miniMoodLegend = [
  { label: 'happy', text: '开心', className: 'mood-dot-happy' },
  { label: 'neutral', text: '平静', className: 'mood-dot-neutral' },
  { label: 'anxious', text: '焦虑', className: 'mood-dot-anxious' },
  { label: 'sad', text: '难过', className: 'mood-dot-sad' },
  { label: 'angry', text: '生气', className: 'mood-dot-angry' },
] as const
const moodYearOptions = computed(() => {
  const current = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, index) => current - index)
})
const moodStats = computed(() =>
  Object.entries(moodSummary.value?.mood_count || {})
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
)
const dominantMoodText = computed(() => {
  const first = moodStats.value[0]
  return first ? `${moodText(first.label)} ${first.count}` : '暂无'
})
const miniCalendarCells = computed<MiniCalendarCell[]>(() => {
  const moodMap = new Map((moodSummary.value?.days || []).map(day => [day.date, day]))
  const firstDay = new Date(moodYear.value, moodMonth.value - 1, 1)
  const lastDate = new Date(moodYear.value, moodMonth.value, 0).getDate()
  const mondayBasedOffset = (firstDay.getDay() + 6) % 7
  const cells: MiniCalendarCell[] = []

  for (let i = 0; i < mondayBasedOffset; i += 1) {
    cells.push({ key: `empty-start-${i}`, inMonth: false })
  }

  for (let day = 1; day <= lastDate; day += 1) {
    const date = `${moodYear.value}-${`${moodMonth.value}`.padStart(2, '0')}-${`${day}`.padStart(2, '0')}`
    cells.push({ key: date, date, day, inMonth: true, mood: moodMap.get(date) })
  }

  while (cells.length % 7 !== 0) {
    cells.push({ key: `empty-end-${cells.length}`, inMonth: false })
  }

  return cells
})
const selectedMoodCell = computed(() =>
  miniCalendarCells.value.find(cell => cell.date === selectedMoodDate.value) ||
  miniCalendarCells.value.find(cell => cell.inMonth) ||
  null
)

onMounted(() => {
  void loadProfile()
})

watch(
  () => props.sessionId,
  () => {
    void loadProfile()
  }
)

watch(
  () => props.refreshKey,
  () => {
    void loadProfile()
  }
)

const loadProfile = async () => {
  if (!props.sessionId) return
  try {
    const { data } = await getProfile(props.sessionId)
    profile.value = data
    syncDraft(data)
  } catch {
    profile.value = profile.value || null
  }
}

const syncDraft = (value: UserProfile | null) => {
  draft.nickname = value?.nickname || ''
  draft.motto = value?.motto || ''
  draft.gender = value?.gender || ''
  draftAvatarUrl.value = value?.avatar_url ? resolveAssetUrl(value.avatar_url) : ''
  avatarFile.value = null
  avatarChanged.value = false
}

const openEditor = () => {
  syncDraft(profile.value)
  loadGrowthSnapshot()
  void loadGrowthRecords()
  goCurrentMoodMonth(false)
  void loadMoodSnapshot()
  editing.value = true
}

const closeEditor = () => {
  editing.value = false
  syncDraft(profile.value)
  savedStampVisible.value = false
}

const onAvatarChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] || null
  avatarFile.value = file
  if (file) {
    draftAvatarUrl.value = URL.createObjectURL(file)
    avatarChanged.value = true
    window.setTimeout(() => {
      avatarChanged.value = false
    }, 520)
  }
  input.value = ''
}

const saveProfile = async () => {
  saving.value = true
  try {
    const { data } = await updateProfile({
      session_id: props.sessionId,
      nickname: draft.nickname.trim() || null,
      motto: draft.motto.trim() || null,
      gender: draft.gender || null,
    })
    profile.value = data

    if (avatarFile.value) {
      const form = new FormData()
      form.append('session_id', props.sessionId)
      form.append('avatar', avatarFile.value)
      const avatarResp = await uploadProfileAvatar(form)
      profile.value = avatarResp.data
    }

    syncDraft(profile.value)
    savedStampVisible.value = true
    window.setTimeout(() => {
      editing.value = false
      savedStampVisible.value = false
    }, 620)
  } finally {
    saving.value = false
  }
}

const loadGrowthRecords = async () => {
  if (!props.sessionId) return
  recordsLoading.value = true
  try {
    const { data } = await getLifeRecords(props.sessionId)
    records.value = data
    loadGrowthSnapshot()
  } catch {
    records.value = records.value || []
  } finally {
    recordsLoading.value = false
  }
}

const loadMoodSnapshot = async () => {
  if (!props.sessionId) return
  try {
    const { data } = await getMoodCalendar(props.sessionId, moodYear.value, moodMonth.value)
    moodSummary.value = data
    if (!selectedMoodDate.value.startsWith(`${moodYear.value}-${`${moodMonth.value}`.padStart(2, '0')}`)) {
      selectedMoodDate.value = `${moodYear.value}-${`${moodMonth.value}`.padStart(2, '0')}-01`
    }
  } catch {
    moodSummary.value = null
  }
}

const goCurrentMoodMonth = (load = true) => {
  const current = new Date()
  moodYear.value = current.getFullYear()
  moodMonth.value = current.getMonth() + 1
  selectedMoodDate.value = todayKey
  if (load) void loadMoodSnapshot()
}

const loadGrowthSnapshot = () => {
  setup.value = loadJson<SetupData>('u-life-user-setup-v1', {})
  memories.value = loadJson<MemoryItem[]>('u-life-long-memory-v1', [])
}

const loadJson = <T,>(key: string, fallback: T): T => {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) as T : fallback
  } catch {
    return fallback
  }
}

const weekRangeText = () => {
  const now = new Date()
  const day = (now.getDay() + 6) % 7
  const start = new Date(now)
  start.setDate(now.getDate() - day)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  const format = (date: Date) => `${date.getMonth() + 1}.${date.getDate()}`
  return `${format(start)}-${format(end)}`
}

const formatRecordTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)
}

const moodText = (mood: string) => {
  const map: Record<string, string> = {
    happy: '开心',
    neutral: '平静',
    anxious: '焦虑',
    sad: '难过',
    angry: '生气',
    surprised: '惊讶',
  }
  return map[mood] || mood
}

const miniMoodClass = (cell: MiniCalendarCell) => {
  if (!cell.mood) return 'no-mood'
  const strong = cell.mood.count >= 3
  const map: Record<string, string> = {
    happy: strong ? 'mood-happy strong' : 'mood-happy',
    neutral: strong ? 'mood-neutral strong' : 'mood-neutral',
    anxious: strong ? 'mood-anxious strong' : 'mood-anxious',
    sad: strong ? 'mood-sad strong' : 'mood-sad',
    angry: strong ? 'mood-angry strong' : 'mood-angry',
    surprised: strong ? 'mood-surprised strong' : 'mood-surprised',
  }
  return map[cell.mood.mood_label] || 'no-mood'
}

const selectMoodDay = (cell: MiniCalendarCell) => {
  if (!cell.inMonth || !cell.date) return
  selectedMoodDate.value = cell.date
}

const moodSourceText = (day: MoodDay) => {
  const sourceName: Record<string, string> = {
    chat: '聊天',
    life: '动态',
    plaza: '广场',
    mood: '手动',
  }
  const sources = Object.entries(day.source_count || {})
    .filter(([, count]) => count > 0)
    .map(([source, count]) => `${sourceName[source] || source}${count}`)
  return sources.length ? sources.join('、') : '来源待同步'
}

const moodTooltip = (cell: MiniCalendarCell) => {
  if (!cell.inMonth || !cell.date) return ''
  if (!cell.mood) return `${cell.date} 暂无心情记录`
  return `${cell.date} ${moodText(cell.mood.mood_label)} · ${cell.mood.count} 条 · ${moodSourceText(cell.mood)}`
}
</script>

<style scoped>
.profile-card {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 64%);
  box-shadow: 0 12px 24px rgb(62 50 40 / 10%);
}

.profile-summary {
  display: flex;
  align-items: center;
  gap: 11px;
  width: 100%;
  padding: 0;
  color: var(--journal-ink);
  text-align: left;
  background: transparent;
  cursor: pointer;
}

.profile-avatar,
.large-avatar {
  display: grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  color: #fff8e8;
  background:
    linear-gradient(145deg, rgb(200 90 84 / 88%), rgb(62 50 40));
  font-weight: 700;
}

.profile-avatar {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  font-size: 20px;
}

.profile-avatar img,
.large-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-copy {
  min-width: 0;
}

.profile-copy strong,
.profile-copy small {
  display: block;
}

.profile-copy strong {
  overflow: hidden;
  color: var(--journal-ink);
  font-size: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-copy small {
  display: -webkit-box;
  margin-top: 3px;
  overflow: hidden;
  color: var(--journal-muted);
  font-size: 11px;
  line-height: 1.35;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.profile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.profile-tags span {
  padding: 4px 8px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 66%);
  font-size: 11px;
}

.profile-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgb(28 19 14 / 42%);
}

.profile-modal {
  position: relative;
  display: flex;
  flex-direction: column;
  width: min(1080px, calc(100vw - 40px));
  height: min(760px, calc(100vh - 36px));
  overflow: hidden;
  padding: clamp(18px, 2vw, 24px);
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 28px 80px rgb(28 19 14 / 32%);
}

.profile-modal-motion-enter-active,
.profile-modal-motion-leave-active {
  transition: opacity 0.28s ease;
}

.profile-modal-motion-enter-active .profile-modal,
.profile-modal-motion-leave-active .profile-modal {
  transition:
    transform 0.34s cubic-bezier(0.2, 0.9, 0.2, 1),
    filter 0.34s ease,
    opacity 0.34s ease;
}

.profile-modal-motion-enter-from,
.profile-modal-motion-leave-to {
  opacity: 0;
}

.profile-modal-motion-enter-from .profile-modal {
  opacity: 0;
  transform: translateY(28px) scale(0.94) rotate(-1.4deg);
  filter: blur(12px) sepia(0.35);
}

.profile-modal-motion-leave-to .profile-modal {
  opacity: 0;
  transform: translateY(12px) scale(0.98) rotate(1deg);
  filter: blur(8px);
}

.saved-stamp {
  position: absolute;
  right: 30px;
  top: 86px;
  z-index: 4;
  display: grid;
  place-items: center;
  width: 118px;
  height: 78px;
  border: 3px solid var(--journal-stamp);
  border-radius: 999px;
  color: var(--journal-stamp);
  font-size: 15px;
  font-weight: 700;
  line-height: 1.05;
  text-align: center;
  rotate: -12deg;
  background: rgb(255 248 232 / 64%);
  mix-blend-mode: multiply;
  animation: stampDrop 0.54s cubic-bezier(0.18, 1.6, 0.42, 1) both;
}

.profile-modal-header {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.profile-modal-header span {
  color: var(--journal-stamp);
  font-size: 11px;
  font-weight: 700;
}

.profile-modal-header h2 {
  margin: 4px 0 0;
  font-size: 24px;
}

.profile-modal-grid {
  display: grid;
  grid-template-columns: minmax(260px, 300px) minmax(0, 1fr);
  gap: clamp(14px, 1.6vw, 18px);
  flex: 1 1 auto;
  margin-top: 16px;
  min-height: 0;
}

.profile-left-column,
.profile-right-column {
  min-width: 0;
  min-height: 0;
}

.profile-left-column {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-right: 2px;
}

.profile-right-column {
  display: grid;
  align-content: start;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
  padding-right: 4px;
}

.close-button,
.ghost-button {
  min-height: 38px;
  border-radius: 10px;
  padding: 0 14px;
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 70%);
  cursor: pointer;
}

.avatar-editor {
  position: relative;
  display: flex;
  align-items: center;
  gap: 18px;
}

.avatar-editor::after {
  content: "";
  position: absolute;
  left: -8px;
  top: -8px;
  width: 112px;
  height: 112px;
  border-radius: 28px;
  background: radial-gradient(circle, rgb(255 255 255 / 72%), transparent 62%);
  opacity: 0;
  pointer-events: none;
}

.avatar-editor-flash::after {
  animation: avatarFlash 0.52s ease-out both;
}

.large-avatar {
  width: 88px;
  height: 88px;
  border-radius: 20px;
  font-size: 32px;
}

.avatar-upload {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.avatar-upload input {
  display: none;
}

.profile-form {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.profile-form label {
  display: grid;
  gap: 6px;
}

.profile-form span,
.ebti-panel span {
  color: var(--journal-muted);
  font-size: 12px;
  font-weight: 700;
}

.profile-form input,
.profile-form textarea,
.profile-form select {
  width: 100%;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.72rem 0.8rem;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
}

.profile-form textarea {
  min-height: 78px;
  resize: vertical;
}

.profile-form input:focus,
.profile-form textarea:focus,
.profile-form select:focus {
  border-color: rgb(200 90 84 / 48%);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
}

.ebti-panel {
  display: grid;
  gap: 5px;
  margin-top: 14px;
  padding: 12px;
  border: 1px dashed rgb(62 50 40 / 24%);
  background: rgb(253 251 247 / 62%);
}

.ebti-panel strong {
  color: var(--journal-stamp);
  font-size: 16px;
}

.ebti-panel small {
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.5;
}

.growth-record-panel {
  display: grid;
  gap: 10px;
  padding: 13px;
  border: 1px solid rgb(62 50 40 / 14%);
  background:
    linear-gradient(115deg, rgb(253 251 247 / 72%), rgb(255 248 232 / 58%)),
    rgb(253 251 247 / 66%);
}

.growth-record-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.growth-record-head span,
.growth-summary-card span {
  color: var(--journal-stamp);
  font-size: 11px;
  font-weight: 800;
}

.growth-record-head h3 {
  margin: 3px 0 0;
  color: var(--journal-ink);
  font-size: 18px;
}

.growth-record-head small {
  display: block;
  margin-top: 3px;
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.35;
}

.mini-refresh-button {
  min-height: 32px;
  border-radius: 9px;
  padding: 0 12px;
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 72%);
  cursor: pointer;
  font-weight: 700;
}

.mini-refresh-button:disabled {
  opacity: 0.55;
  cursor: default;
}

.growth-stat-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 7px;
}

.growth-stat-grid div {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid rgb(62 50 40 / 12%);
  background: rgb(255 248 232 / 58%);
}

.growth-stat-grid strong {
  color: var(--journal-stamp);
  font-size: 18px;
}

.growth-stat-grid span {
  overflow: hidden;
  color: var(--journal-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.growth-summary-card {
  display: grid;
  gap: 4px;
  padding: 10px;
  border-left: 4px solid var(--journal-stamp);
  background: rgb(255 248 232 / 64%);
}

.growth-summary-card strong {
  color: var(--journal-ink);
  font-size: 14px;
}

.growth-summary-card small {
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.45;
}

.record-preview-list {
  display: grid;
  gap: 6px;
}

.record-preview-item {
  display: grid;
  grid-template-columns: 10px minmax(0, 1fr);
  gap: 9px;
  align-items: start;
  padding: 7px 0;
  border-top: 1px dashed rgb(62 50 40 / 14%);
}

.record-visibility-dot {
  width: 9px;
  height: 9px;
  margin-top: 6px;
  border-radius: 999px;
  background: var(--journal-muted);
}

.record-visibility-dot.public {
  background: var(--journal-stamp);
}

.record-visibility-dot.private {
  background: #6b7d74;
}

.record-preview-item strong,
.record-preview-item small {
  display: block;
  min-width: 0;
}

.record-preview-item strong {
  overflow: hidden;
  color: var(--journal-ink);
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-preview-item small,
.empty-growth-record {
  margin: 3px 0 0;
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.45;
}

.mini-mood-panel {
  display: grid;
  gap: 10px;
  padding: 13px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(253 251 247 / 62%);
}

.mood-count-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border-radius: 999px;
  padding: 0 11px;
  color: #fff8e8;
  background: var(--journal-stamp);
  font-size: 12px;
}

.mini-mood-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.mini-mood-toolbar select,
.mini-mood-toolbar button {
  min-height: 32px;
  border: 1px solid rgb(62 50 40 / 16%);
  border-radius: 9px;
  padding: 0 10px;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
  font-size: 12px;
  font-weight: 700;
}

.mini-mood-toolbar button {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.mini-mood-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.mini-mood-stats div {
  display: grid;
  gap: 3px;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid rgb(62 50 40 / 12%);
  background: rgb(255 248 232 / 58%);
}

.mini-mood-stats span {
  color: var(--journal-muted);
  font-size: 11px;
  font-weight: 800;
}

.mini-mood-stats strong {
  overflow: hidden;
  color: var(--journal-stamp);
  font-size: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-mood-distribution {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.mini-mood-distribution span,
.mini-mood-distribution em {
  border: 1px solid rgb(62 50 40 / 12%);
  border-radius: 999px;
  padding: 4px 8px;
  color: var(--journal-muted);
  background: rgb(255 248 232 / 58%);
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
}

.mini-week-row,
.mini-calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 40px);
  justify-content: start;
  gap: 5px;
}

.mini-week-row span {
  color: var(--journal-muted);
  font-size: 11px;
  font-weight: 800;
  text-align: center;
}

.mini-calendar-cell {
  position: relative;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  min-width: 0;
  border: 1px solid rgb(62 50 40 / 10%);
  border-radius: 7px;
  color: var(--journal-muted);
  background: rgb(255 248 232 / 60%);
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
}

.mini-calendar-cell:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: saturate(1.08);
  box-shadow: 0 7px 13px rgb(62 50 40 / 12%);
}

.mini-calendar-cell:disabled {
  cursor: default;
}

.mini-calendar-cell b {
  position: relative;
  z-index: 2;
  font-size: 11px;
}

.mini-calendar-cell i {
  position: absolute;
  right: 5px;
  bottom: 5px;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: currentColor;
}

.mini-calendar-cell.today {
  border-color: rgb(62 50 40 / 34%);
  box-shadow: inset 0 0 0 2px rgb(255 248 232 / 86%);
}

.mini-calendar-cell.selected {
  outline: 2px solid var(--journal-stamp);
  outline-offset: 2px;
}

.mini-calendar-cell.today::after {
  content: "";
  position: absolute;
  top: 5px;
  right: 5px;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: var(--journal-stamp);
}

.mini-calendar-cell.outside-month {
  visibility: hidden;
}

.mini-calendar-cell.no-mood {
  background: rgb(253 251 247 / 52%);
}

.mini-calendar-cell.mood-happy {
  color: #6b4b0c;
  background: rgb(232 195 108 / 48%);
}

.mini-calendar-cell.mood-neutral {
  color: #31564a;
  background: rgb(98 142 123 / 34%);
}

.mini-calendar-cell.mood-anxious {
  color: #8c4a12;
  background: rgb(217 132 58 / 34%);
}

.mini-calendar-cell.mood-sad {
  color: #2f587a;
  background: rgb(86 133 174 / 34%);
}

.mini-calendar-cell.mood-angry {
  color: #7d2c28;
  background: rgb(200 90 84 / 36%);
}

.mini-calendar-cell.mood-surprised {
  color: #5d4470;
  background: rgb(154 122 168 / 36%);
}

.mini-calendar-cell.strong {
  box-shadow:
    inset 0 0 0 1px currentColor,
    0 8px 14px rgb(62 50 40 / 10%);
}

.selected-mood-card {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px dashed rgb(62 50 40 / 18%);
  background: rgb(255 248 232 / 58%);
}

.selected-mood-card span {
  color: var(--journal-muted);
  font-size: 11px;
  font-weight: 800;
}

.selected-mood-card strong {
  color: var(--journal-ink);
  font-size: 15px;
}

.selected-mood-card small {
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.45;
}

.mini-mood-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 7px 10px;
}

.mini-mood-legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--journal-muted);
  font-size: 11px;
  font-weight: 700;
}

.mini-mood-legend i {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.mood-dot-happy {
  background: rgb(232 195 108);
}

.mood-dot-neutral {
  background: rgb(98 142 123);
}

.mood-dot-anxious {
  background: rgb(217 132 58);
}

.mood-dot-sad {
  background: rgb(86 133 174);
}

.mood-dot-angry {
  background: rgb(200 90 84);
}

.profile-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: auto;
  padding-top: 16px;
}

.save-button {
  position: relative;
  overflow: hidden;
  min-height: 40px;
  border-radius: 10px;
  padding: 0 16px;
  color: #fff8e8;
  font-weight: 700;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.button-shutter {
  position: absolute;
  inset: -40%;
  border-radius: 999px;
  background:
    conic-gradient(from 0deg, transparent 0 12%, rgb(255 248 232 / 36%) 13% 23%, transparent 24% 38%, rgb(255 248 232 / 28%) 39% 48%, transparent 49% 100%);
  opacity: 0;
  pointer-events: none;
}

.save-button:disabled .button-shutter {
  opacity: 1;
  animation: profileButtonShutter 0.82s ease-in-out infinite;
}

.save-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@keyframes stampDrop {
  0% {
    opacity: 0;
    transform: translateY(-28px) scale(1.5) rotate(10deg);
    filter: blur(5px);
  }
  58% {
    opacity: 1;
    transform: translateY(3px) scale(0.9) rotate(0);
    filter: blur(0);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1) rotate(0);
  }
}

@keyframes avatarFlash {
  0% {
    opacity: 0;
    transform: scale(0.7);
  }
  35% {
    opacity: 0.92;
  }
  100% {
    opacity: 0;
    transform: scale(1.35);
  }
}

@keyframes profileButtonShutter {
  0% {
    transform: scale(1.26) rotate(0deg);
    opacity: 0.18;
  }
  50% {
    transform: scale(0.78) rotate(55deg);
    opacity: 0.82;
  }
  100% {
    transform: scale(1.26) rotate(110deg);
    opacity: 0.18;
  }
}

@media (max-width: 820px) {
  .profile-modal {
    overflow-y: auto;
    padding: 18px;
  }

  .profile-modal-grid {
    grid-template-columns: 1fr;
  }

  .profile-right-column {
    max-height: none;
    overflow: visible;
    padding-right: 0;
  }

  .profile-modal-actions {
    margin-top: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .profile-modal-motion-enter-active,
  .profile-modal-motion-leave-active,
  .profile-modal-motion-enter-active .profile-modal,
  .profile-modal-motion-leave-active .profile-modal {
    transition: none !important;
  }

  .saved-stamp,
  .avatar-editor-flash::after,
  .save-button:disabled .button-shutter {
    animation: none !important;
  }
}
</style>
