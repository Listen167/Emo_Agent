<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import OnboardingModal from './components/OnboardingModal.vue'
import ProfileCard from './components/ProfileCard.vue'
import ChatView from './views/ChatView.vue'
import GrowthView from './views/GrowthView.vue'
import LandingView from './views/LandingView.vue'
import LifeRecordView from './views/LifeRecordView.vue'
import MoodCalendarView from './views/MoodCalendarView.vue'
import PlazaView from './views/PlazaView.vue'
import ResumeView from './views/ResumeView.vue'
import { BACKEND_ORIGIN } from './api/client'
import { updateGrowthProfile } from './api/growth'
import { updateProfileEbti } from './api/profile'
import { createClientId } from './utils/id'

type ViewKey = 'chat' | 'life' | 'mood' | 'resume' | 'growth' | 'ebti' | 'plaza'

const showLanding = ref(true)
const showOnboarding = ref(false)
const sessionId = ref(localStorage.getItem('sid') || createClientId())
localStorage.setItem('sid', sessionId.value)
const profileVersion = ref(0)
const activeView = ref<ViewKey>('chat')
const viewHistory = ref<ViewKey[]>([])
const viewForwardStack = ref<ViewKey[]>([])
const sidebarCollapsed = ref(false)
const townUrl = `/ai-town/index.html${BACKEND_ORIGIN ? `?backend=${encodeURIComponent(`${BACKEND_ORIGIN}/api/town`)}` : ''}`
const navItems = [
  { key: 'chat', cn: '首页', en: 'Home', icon: '⌂', note: '和小曦对话' },
  { key: 'life', cn: '胶卷库', en: 'Rolls', icon: '▣', note: '生活记录' },
  { key: 'mood', cn: '拍摄记录', en: 'Log', icon: '◫', note: '心情日历' },
  { key: 'resume', cn: '简历工坊', en: 'Resume', icon: '▤', note: '简历制作' },
  { key: 'ebti', cn: '我的暗房', en: 'Darkroom', icon: '✦', note: 'EBTI 测试' },
  { key: 'plaza', cn: '聊天广场', en: 'Plaza', icon: '◈', note: '公开胶片' },
  { key: 'growth', cn: '成长中心', en: 'Growth', icon: '✺', note: '周报与隐私' },
] as const
const activeLabel = computed(() => navItems.find(item => item.key === activeView.value)?.note || 'Film Journal')
const activeNavIndex = computed(() => Math.max(0, navItems.findIndex(item => item.key === activeView.value)))
const canGoBack = computed(() => viewHistory.value.length > 0)
const canGoForward = computed(() => viewForwardStack.value.length > 0)
const NAV_WHEEL_THRESHOLD = 48
const NAV_WHEEL_COOLDOWN_MS = 155
let navWheelDelta = 0
let navWheelResetTimer: number | undefined
let navWheelCooldownTimer: number | undefined
let navWheelLocked = false

const navigateTo = (view: ViewKey) => {
  if (activeView.value === view) return
  viewHistory.value.push(activeView.value)
  viewForwardStack.value = []
  activeView.value = view
}

const goBack = () => {
  const previousView = viewHistory.value.pop()
  if (!previousView) return
  viewForwardStack.value.push(activeView.value)
  activeView.value = previousView
}

const goForward = () => {
  const nextView = viewForwardStack.value.pop()
  if (!nextView) return
  viewHistory.value.push(activeView.value)
  activeView.value = nextView
}

const normalizeNavIndex = (index: number) => {
  const length = navItems.length
  return ((index % length) + length) % length
}

const navigateNavByIndex = (index: number) => {
  const next = navItems[normalizeNavIndex(index)]
  navigateTo(next.key)
}

const rollNav = (direction: 1 | -1) => {
  navigateNavByIndex(activeNavIndex.value + direction)
}

const handleNavWheel = (event: WheelEvent) => {
  if (event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return

  event.preventDefault()
  if (navWheelLocked) return

  navWheelDelta += event.deltaY
  if (navWheelResetTimer) window.clearTimeout(navWheelResetTimer)
  navWheelResetTimer = window.setTimeout(() => {
    navWheelDelta = 0
  }, 140)

  if (Math.abs(navWheelDelta) < NAV_WHEEL_THRESHOLD) return

  rollNav(navWheelDelta > 0 ? 1 : -1)
  navWheelDelta = 0
  navWheelLocked = true
  navWheelCooldownTimer = window.setTimeout(() => {
    navWheelLocked = false
  }, NAV_WHEEL_COOLDOWN_MS)
}

const handleNavKeydown = (event: KeyboardEvent) => {
  if (event.altKey || event.ctrlKey || event.metaKey) return

  if (['ArrowDown', 'ArrowRight', 'PageDown'].includes(event.key)) {
    event.preventDefault()
    rollNav(1)
  }

  if (['ArrowUp', 'ArrowLeft', 'PageUp'].includes(event.key)) {
    event.preventDefault()
    rollNav(-1)
  }

  if (event.key === 'Home') {
    event.preventDefault()
    navigateNavByIndex(0)
  }

  if (event.key === 'End') {
    event.preventDefault()
    navigateNavByIndex(navItems.length - 1)
  }
}

const handleKeyboardNavigation = (event: KeyboardEvent) => {
  if (!event.altKey) return

  const target = event.target instanceof Element ? event.target : null
  if (target?.closest('input, textarea, select, iframe')) return

  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    goBack()
  }

  if (event.key === 'ArrowRight') {
    event.preventDefault()
    goForward()
  }
}

const handleEbtiMessage = async (event: MessageEvent) => {
  if (event.origin !== window.location.origin) return
  const payload = event.data
  if (!payload || payload.source !== 'ebti-test' || payload.event !== 'ebti-result') return
  if (typeof payload.ebti_type !== 'string' || !payload.ebti_type.trim()) return

  await updateProfileEbti({
    session_id: sessionId.value,
    ebti_type: payload.ebti_type,
    ebti_name: typeof payload.ebti_name === 'string' ? payload.ebti_name : null,
    ebti_avatar: typeof payload.ebti_avatar === 'string' ? payload.ebti_avatar : null,
  })
  profileVersion.value += 1
}

const syncOnboardingToServer = async () => {
  const raw = localStorage.getItem('u-life-user-setup-v1')
  if (!raw) return
  try {
    const setup = JSON.parse(raw)
    await updateGrowthProfile({
      session_id: sessionId.value,
      nickname: setup.nickname || '胶片旅人',
      current_state: setup.currentState || null,
      focus: setup.focus || null,
      personality: setup.personality || localStorage.getItem('u-life-xiaoxi-personality-v1') || 'warm',
      weekly_goal: setup.weeklyGoal || '每天留下一次真实记录',
      setup_completed: Boolean(setup.completed),
    })
  } catch {
    // 本地引导数据损坏时忽略，成长中心仍可重新保存。
  }
}

const handleOnboardingComplete = async () => {
  showOnboarding.value = false
  await syncOnboardingToServer()
  profileVersion.value += 1
}

onMounted(() => {
  showOnboarding.value = !localStorage.getItem('u-life-user-setup-v1')
  window.addEventListener('message', handleEbtiMessage)
  window.addEventListener('keydown', handleKeyboardNavigation)
})

onBeforeUnmount(() => {
  window.removeEventListener('message', handleEbtiMessage)
  window.removeEventListener('keydown', handleKeyboardNavigation)
  if (navWheelResetTimer) window.clearTimeout(navWheelResetTimer)
  if (navWheelCooldownTimer) window.clearTimeout(navWheelCooldownTimer)
})
</script>

<template>
  <!-- 开场动画 -->
  <Transition name="landing-fade">
    <LandingView v-if="showLanding" @enter="showLanding = false" />
  </Transition>

  <OnboardingModal v-if="!showLanding && showOnboarding" @complete="handleOnboardingComplete" />

  <div v-if="!showLanding" :class="['journal-shell', 'paper-texture', { 'sidebar-collapsed': sidebarCollapsed }]">
    <aside class="journal-sidebar">
      <div class="sidebar-brand">
        <div class="brand-row">
          <span class="film-menu-mark" aria-hidden="true">
            <i></i>
            <i></i>
            <i></i>
          </span>
          <button
            class="camera-mark sidebar-toggle"
            type="button"
            :aria-label="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
            :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
            @click="sidebarCollapsed = !sidebarCollapsed"
          >
            <span class="camera-core" aria-hidden="true"></span>
            <span
              :class="['collapse-cue', sidebarCollapsed ? 'cue-expand' : 'cue-collapse']"
              aria-hidden="true"
            ></span>
          </button>
        </div>
        <h1 class="script-title">Film Journal</h1>
        <p>记录每一次快门的心跳</p>
      </div>

      <ProfileCard :session-id="sessionId" :refresh-key="profileVersion" />

      <nav
        class="liquid-nav nav-wheel"
        aria-label="主功能"
        tabindex="0"
        @wheel="handleNavWheel"
        @keydown="handleNavKeydown"
      >
        <span
          class="nav-wheel-indicator"
          aria-hidden="true"
          :style="{ '--active-nav-index': activeNavIndex }"
        ></span>
        <span
          class="mobile-nav-indicator"
          aria-hidden="true"
          :style="{ '--active-nav-index': activeNavIndex }"
        ></span>
        <div class="nav-wheel-stage">
          <button
            v-for="item in navItems"
            :key="item.key"
            :class="['liquid-button', { active: activeView === item.key }]"
            :aria-current="activeView === item.key ? 'page' : undefined"
            :title="`${item.cn} · ${item.note}`"
            type="button"
            @click="navigateTo(item.key)"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span>
              <strong>{{ item.cn }}</strong>
              <small>{{ item.en }} · {{ item.note }}</small>
            </span>
          </button>
        </div>
        <a class="liquid-button town-link" :href="townUrl" target="_blank" title="AI 小镇 · 互动空间">
          <span class="nav-icon">⌁</span>
          <span>
            <strong>AI 小镇</strong>
            <small>Town · 互动空间</small>
          </span>
        </a>
      </nav>

      <div class="sidebar-ticket">
        <span>SESSION</span>
        <strong>{{ activeLabel }}</strong>
      </div>
      <div class="sidebar-film film-strip" />
    </aside>

    <section class="journal-stage">
      <div class="history-switcher" aria-label="页面切换历史">
        <button
          class="history-button"
          :disabled="!canGoBack"
          title="返回上一页 Alt + ←"
          aria-label="返回上一页"
          @click="goBack"
        >
          <span>‹</span>
          <strong>返回</strong>
        </button>
        <button
          class="history-button"
          :disabled="!canGoForward"
          title="前进到下一页 Alt + →"
          aria-label="前进到下一页"
          @click="goForward"
        >
          <strong>前进</strong>
          <span>›</span>
        </button>
      </div>
      <Transition name="view-develop" mode="out-in">
        <ChatView v-if="activeView === 'chat'" key="chat" />
        <LifeRecordView v-else-if="activeView === 'life'" key="life" />
        <MoodCalendarView v-else-if="activeView === 'mood'" key="mood" />
        <ResumeView v-else-if="activeView === 'resume'" key="resume" />
        <GrowthView v-else-if="activeView === 'growth'" key="growth" />
        <PlazaView v-else-if="activeView === 'plaza'" key="plaza" />
        <main v-else key="ebti" class="embedded-page">
          <div class="embedded-frame">
            <iframe
              src="/ebti-test/index.html"
              title="EBTI 测试"
            ></iframe>
          </div>
        </main>
      </Transition>
    </section>
  </div>
</template>

<style>
.landing-fade-leave-active {
  transition: opacity 0.5s ease-out;
}
.landing-fade-leave-to {
  opacity: 0;
}

.journal-shell {
  position: relative;
  height: 100vh;
  display: grid;
  grid-template-columns: 286px minmax(0, 1fr);
  transition: grid-template-columns 0.32s cubic-bezier(0.2, 0.86, 0.2, 1);
}

.journal-shell::after {
  display: none;
}

.journal-shell.sidebar-collapsed {
  grid-template-columns: 92px minmax(0, 1fr);
}

.journal-sidebar {
  position: relative;
  z-index: 3;
  height: 100vh;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px 20px;
  border-right: 1px solid rgb(255 255 255 / 58%);
  background:
    linear-gradient(115deg, rgb(255 255 255 / 74%), rgb(255 241 205 / 28%) 42%, rgb(255 255 255 / 46%)),
    radial-gradient(circle at 24% 8%, rgb(255 255 255 / 74%), transparent 20rem),
    rgb(253 251 247 / 50%);
  box-shadow:
    inset 1px 0 0 rgb(255 255 255 / 78%),
    inset -18px 0 42px rgb(232 195 108 / 12%),
    18px 0 42px rgb(62 50 40 / 14%);
  backdrop-filter: blur(24px) saturate(155%);
  -webkit-backdrop-filter: blur(24px) saturate(155%);
  overflow-y: auto;
  overscroll-behavior: auto;
  transition:
    padding 0.32s cubic-bezier(0.2, 0.86, 0.2, 1),
    box-shadow 0.34s ease,
    background 0.34s ease;
}

.sidebar-collapsed .journal-sidebar {
  gap: 16px;
  padding: 20px 12px;
  overflow-x: hidden;
}

.journal-sidebar:hover,
.journal-sidebar:focus-within {
  box-shadow:
    inset 1px 0 0 rgb(255 255 255 / 86%),
    inset -18px 0 42px rgb(232 195 108 / 16%),
    26px 0 68px rgb(62 50 40 / 22%);
}

.journal-sidebar::before,
.journal-sidebar::after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.journal-sidebar::before {
  inset: 0;
  background:
    linear-gradient(180deg, rgb(255 255 255 / 34%), transparent 36%),
    linear-gradient(90deg, transparent, rgb(255 255 255 / 20%), transparent);
  opacity: 0.36;
}

.journal-sidebar::after {
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgb(255 255 255 / 92%), transparent);
  opacity: 0.8;
}

.sidebar-brand {
  position: relative;
  z-index: 1;
  padding: 4px 6px 0;
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--journal-ink);
  font-size: 23px;
}

.film-menu-mark {
  width: 42px;
  height: 28px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  padding: 5px;
  border-radius: 12px;
  border: 1px solid rgb(62 50 40 / 16%);
  background:
    linear-gradient(145deg, rgb(255 248 232 / 62%), rgb(255 255 255 / 34%));
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 64%),
    0 8px 16px rgb(62 50 40 / 10%);
}

.film-menu-mark i {
  display: block;
  border-radius: 999px;
  background: rgb(62 50 40 / 72%);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 20%);
}

.camera-mark {
  position: relative;
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: var(--journal-kodak);
  border: 1px solid rgb(62 50 40 / 24%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 44%),
    inset 0 -8px 14px rgb(62 50 40 / 10%),
    0 8px 18px rgb(62 50 40 / 18%);
  cursor: pointer;
  color: var(--journal-ink);
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    background 0.22s ease;
}

.camera-core {
  position: absolute;
  left: 9px;
  top: 10px;
  width: 17px;
  height: 17px;
  border: 2px solid rgb(62 50 40 / 76%);
  border-radius: 999px;
  box-shadow:
    inset 0 0 0 4px rgb(62 50 40 / 12%),
    0 1px 1px rgb(255 255 255 / 30%);
}

.collapse-cue {
  position: absolute;
  right: 8px;
  top: 13px;
  width: 8px;
  height: 13px;
  color: rgb(62 50 40 / 88%);
  transition: transform 0.22s ease;
}

.collapse-cue::before,
.collapse-cue::after {
  content: "";
  position: absolute;
  right: 0;
  width: 8px;
  height: 2px;
  border-radius: 999px;
  background: currentColor;
}

.collapse-cue::before {
  top: 3px;
  transform: rotate(42deg);
  transform-origin: right center;
}

.collapse-cue::after {
  bottom: 3px;
  transform: rotate(-42deg);
  transform-origin: right center;
}

.cue-expand {
  right: 7px;
  transform: scaleX(-1);
}

.sidebar-toggle:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 42%),
    0 11px 24px rgb(62 50 40 / 22%);
}

.sidebar-toggle:hover .collapse-cue {
  transform: translateX(-2px);
}

.sidebar-toggle:hover .cue-expand {
  transform: scaleX(-1) translateX(-2px);
}

.sidebar-toggle:active {
  transform: scale(0.96);
}

.sidebar-brand h1 {
  margin: 10px 0 2px;
  font-size: 42px;
  line-height: 0.95;
  color: var(--journal-ink);
}

.sidebar-brand p {
  margin: 0;
  color: var(--journal-muted);
  font-size: 13px;
}

.sidebar-collapsed .sidebar-brand {
  display: grid;
  place-items: center;
  padding: 0;
}

.sidebar-collapsed .brand-row {
  width: 100%;
  justify-content: center;
}

.sidebar-collapsed .film-menu-mark,
.sidebar-collapsed .sidebar-brand h1,
.sidebar-collapsed .sidebar-brand p {
  display: none;
}

.sidebar-collapsed .camera-mark {
  width: 46px;
  height: 46px;
}

.sidebar-collapsed .camera-core {
  left: 11px;
  top: 12px;
  width: 18px;
  height: 18px;
}

.sidebar-collapsed .collapse-cue {
  right: 9px;
  top: 16px;
}

.liquid-nav {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 10px;
  padding: 10px;
  border-radius: 24px;
  outline: none;
  background:
    linear-gradient(145deg, rgb(255 255 255 / 42%), rgb(255 241 205 / 18%)),
    rgb(255 255 255 / 26%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 62%),
    inset 0 -18px 34px rgb(62 50 40 / 5%),
    0 14px 30px rgb(62 50 40 / 10%);
  backdrop-filter: blur(22px) saturate(150%);
  -webkit-backdrop-filter: blur(22px) saturate(150%);
  transition:
    padding 0.32s cubic-bezier(0.2, 0.86, 0.2, 1),
    border-radius 0.32s ease,
    box-shadow 0.24s ease;
}

.sidebar-collapsed .liquid-nav {
  padding: 8px;
  border-radius: 24px;
}

.liquid-nav:focus-visible {
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 72%),
    inset 0 -18px 34px rgb(62 50 40 / 5%),
    0 0 0 3px rgb(200 90 84 / 16%);
}

.nav-wheel-indicator {
  position: absolute;
  left: 10px;
  right: 10px;
  top: 10px;
  height: 62px;
  z-index: 1;
  border-radius: 19px;
  border: 1px solid rgb(255 255 255 / 74%);
  background:
    linear-gradient(145deg, rgb(255 255 255 / 76%), rgb(255 241 205 / 26%)),
    rgb(255 255 255 / 38%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 92%),
    inset 0 -12px 22px rgb(232 195 108 / 12%),
    0 12px 24px rgb(62 50 40 / 12%);
  transform: translateY(calc(var(--active-nav-index) * 72px));
  transition: transform 0.38s cubic-bezier(0.2, 0.86, 0.2, 1);
}

.sidebar-collapsed .nav-wheel-indicator {
  left: 8px;
  right: 8px;
  height: 52px;
  border-radius: 17px;
  transform: translateY(calc(var(--active-nav-index) * 60px));
}

.nav-wheel-stage {
  position: relative;
  z-index: 2;
  display: grid;
  gap: 10px;
  overflow: visible;
  border-radius: 22px;
}

.sidebar-collapsed .nav-wheel-stage {
  gap: 8px;
}

.mobile-nav-indicator {
  display: none;
}

.liquid-button {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: 62px;
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  border-radius: 19px;
  border: 1px solid rgb(255 255 255 / 68%);
  color: var(--journal-ink);
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  background:
    linear-gradient(135deg, rgb(255 255 255 / 80%), rgb(255 241 205 / 32%)),
    var(--journal-glass);
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 95%),
    inset 0 -10px 20px rgb(232 195 108 / 8%),
    0 8px 18px rgb(62 50 40 / 8%);
  opacity: 0.88;
  transform: scale(1);
  transform-origin: 50% 50%;
  transition:
    opacity 0.28s ease,
    transform 0.28s cubic-bezier(0.2, 0.85, 0.2, 1),
    box-shadow 0.25s ease,
    background 0.25s ease;
}

.sidebar-collapsed .liquid-button {
  min-height: 52px;
  justify-content: center;
  gap: 0;
  padding: 8px;
  border-radius: 17px;
}

.sidebar-collapsed .liquid-button > span:not(.nav-icon) {
  width: 0;
  opacity: 0;
  transform: translateX(-6px);
  overflow: hidden;
}

.sidebar-collapsed .liquid-button small,
.sidebar-collapsed .liquid-button strong {
  white-space: nowrap;
}

.nav-wheel-stage .liquid-button {
  z-index: 2;
}

.liquid-button > span:not(.nav-icon) {
  min-width: 0;
  transition: opacity 0.2s ease, transform 0.2s ease, width 0.2s ease;
}

.liquid-button::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(circle at 18% 12%, rgb(255 255 255 / 95%), transparent 24%),
    linear-gradient(120deg, transparent 18%, rgb(255 255 255 / 64%) 43%, transparent 66%);
  transform: translateX(-125%) skewX(-18deg);
  transition: transform 0.7s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.liquid-button::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: 18px;
  border-top: 1px solid rgb(255 255 255 / 82%);
  border-left: 1px solid rgb(255 255 255 / 42%);
  pointer-events: none;
}

.liquid-button:hover,
.liquid-button.active {
  opacity: 1;
  transform: translateY(-1px) scale(1.012);
  background:
    linear-gradient(135deg, rgb(255 255 255 / 48%), rgb(232 195 108 / 13%)),
    rgb(255 255 255 / 20%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 86%),
    inset 0 -10px 20px rgb(232 195 108 / 10%),
    0 10px 22px rgb(62 50 40 / 10%);
}

.liquid-button:hover::before,
.liquid-button.active::before {
  transform: translateX(120%) skewX(-18deg);
}

.liquid-button:active {
  transform: translateY(0) scale(0.992);
  transition-duration: 0.08s;
}

.liquid-button.active::before {
  animation: liquidShine 3.4s ease-in-out infinite;
}

.liquid-button.active .nav-icon {
  animation: navIconPop 0.52s cubic-bezier(0.2, 1.6, 0.3, 1);
}

.nav-icon {
  position: relative;
  overflow: hidden;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 12px;
  color: #fff7e8;
  background: linear-gradient(145deg, #4a3526, #1c130e);
  box-shadow: inset 0 1px 1px rgb(255 255 255 / 26%);
}

.sidebar-collapsed .nav-icon {
  width: 36px;
  height: 36px;
}

.nav-icon::after {
  content: "";
  position: absolute;
  inset: 7px;
  border-radius: 999px;
  background: rgb(255 248 232 / 38%);
  transform: scale(0);
  opacity: 0;
}

.liquid-button.active .nav-icon::after {
  animation: navIconGlow 1.6s ease-out infinite;
}

.liquid-button strong,
.liquid-button small {
  display: block;
}

.liquid-button strong {
  font-size: 15px;
}

.liquid-button small {
  margin-top: 2px;
  color: rgb(62 50 40 / 68%);
  font-size: 11px;
}

.town-link {
  margin-top: 2px;
}

.sidebar-collapsed .town-link {
  margin-top: 0;
}

.sidebar-ticket {
  margin-top: auto;
  padding: 16px;
  border: 1px dashed rgb(62 50 40 / 34%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 10px 24px rgb(62 50 40 / 10%);
}

.sidebar-ticket span,
.sidebar-ticket strong {
  display: block;
}

.sidebar-ticket span {
  color: var(--journal-stamp);
  font-size: 11px;
  font-weight: 700;
}

.sidebar-ticket strong {
  margin-top: 4px;
  font-size: 18px;
}

.sidebar-film {
  height: 48px;
  border-radius: 8px;
  box-shadow: 0 10px 20px rgb(62 50 40 / 18%);
}

.sidebar-collapsed .profile-card,
.sidebar-collapsed .sidebar-ticket,
.sidebar-collapsed .sidebar-film {
  display: none;
}

.journal-stage {
  position: relative;
  z-index: 1;
  min-width: 0;
  min-height: 0;
  height: 100vh;
  overflow: auto;
  overscroll-behavior: auto;
}

.journal-stage::before,
.journal-stage::after {
  display: none;
}

.history-switcher {
  position: sticky;
  top: 18px;
  z-index: 30;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 18px 24px 0;
  pointer-events: none;
}

.history-button {
  pointer-events: auto;
  min-width: 82px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1px solid rgb(255 255 255 / 68%);
  border-radius: 999px;
  color: var(--journal-ink);
  background:
    linear-gradient(135deg, rgb(255 255 255 / 78%), rgb(255 241 205 / 35%)),
    rgb(255 255 255 / 52%);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255 / 92%),
    0 12px 26px rgb(62 50 40 / 15%);
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
}

.history-button span {
  font-size: 25px;
  line-height: 1;
}

.history-button strong {
  font-size: 13px;
}

.history-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow:
    inset 0 1px 1px rgb(255 255 255),
    0 16px 30px rgb(62 50 40 / 19%);
}

.history-button:active:not(:disabled) {
  transform: translateY(0) scale(0.97);
}

.history-button:disabled {
  opacity: 0.42;
  cursor: not-allowed;
}

.view-develop-enter-active,
.view-develop-leave-active {
  transition:
    opacity 0.42s ease,
    transform 0.42s cubic-bezier(0.2, 0.8, 0.2, 1),
    filter 0.42s ease;
}

.view-develop-enter-from {
  opacity: 0;
  transform: translateY(18px) scale(0.985);
  filter: blur(12px) sepia(0.45) saturate(0.8);
}

.view-develop-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.992);
  filter: blur(8px) sepia(0.25) saturate(0.9);
}

.view-develop-enter-to,
.view-develop-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0) sepia(0) saturate(1);
}

.embedded-page {
  min-height: 100vh;
  padding: 26px;
}

.embedded-frame {
  height: calc(100vh - 52px);
  overflow: hidden;
  border: 10px solid #fff6df;
  border-radius: 8px;
  box-shadow: 0 18px 42px rgb(62 50 40 / 20%);
  background: #111827;
}

.embedded-frame iframe {
  width: 100%;
  height: 100%;
  border: 0;
}

@media (max-width: 860px) {
  .journal-shell {
    display: block;
    height: 100vh;
    padding-bottom: 92px;
    overflow: hidden;
  }

  .journal-shell.sidebar-collapsed {
    display: block;
  }

  .journal-sidebar {
    position: fixed;
    inset: auto 12px 12px;
    width: auto;
    height: auto;
    transform: none;
    padding: 10px;
    border: 1px solid rgb(255 255 255 / 52%);
    border-radius: 24px;
    background: rgb(255 248 232 / 56%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }

  .sidebar-toggle {
    display: none;
  }

  .journal-sidebar::before,
  .journal-sidebar::after {
    display: none;
  }

  .journal-stage {
    height: 100vh;
    padding-bottom: 92px;
    overflow: auto;
  }

  .history-switcher {
    top: 10px;
    padding: 10px 12px 0;
  }

  .history-button {
    min-width: 44px;
    width: 44px;
    padding: 0;
  }

  .history-button strong {
    display: none;
  }

  .sidebar-brand,
  .profile-card,
  .sidebar-ticket,
  .sidebar-film {
    display: none;
  }

  .liquid-nav {
    position: relative;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 10px;
    perspective: none;
    scrollbar-width: none;
  }

  .liquid-nav::before,
  .liquid-nav::after {
    display: none;
  }

  .liquid-nav::-webkit-scrollbar {
    display: none;
  }

  .nav-wheel-indicator {
    display: none;
  }

  .nav-wheel-stage {
    display: flex;
    gap: 8px;
    overflow: visible;
  }

  .mobile-nav-indicator {
    position: absolute;
    left: 0;
    top: 0;
    z-index: -1;
    width: 78px;
    height: 56px;
    display: block;
    border-radius: 18px;
    border: 1px solid rgb(200 90 84 / 32%);
    background:
      radial-gradient(circle at 50% 18%, rgb(255 255 255 / 82%), transparent 28%),
      linear-gradient(135deg, rgb(232 195 108 / 52%), rgb(200 90 84 / 16%));
    box-shadow:
      inset 0 1px 1px rgb(255 255 255 / 90%),
      0 10px 22px rgb(62 50 40 / 16%);
    transform: translateX(calc(var(--active-nav-index) * 86px));
    transition: transform 0.32s cubic-bezier(0.2, 0.9, 0.2, 1);
  }

  .liquid-button {
    position: relative;
    inset: auto;
    z-index: 1;
    min-width: 78px;
    min-height: 56px;
    justify-content: center;
    gap: 12px;
    padding: 8px 10px;
    opacity: 1;
    filter: none;
    transform: none;
    pointer-events: auto;
  }

  .sidebar-collapsed .liquid-button {
    min-height: 56px;
    min-width: 78px;
    gap: 12px;
    padding: 8px 10px;
  }

  .sidebar-collapsed .liquid-button > span:not(.nav-icon) {
    width: auto;
    opacity: 1;
    transform: none;
    overflow: visible;
  }

  .liquid-button:hover,
  .liquid-button.active,
  .liquid-button:active {
    transform: none;
  }

  .liquid-button small {
    display: none;
  }
}

@keyframes liquidShine {
  0%,
  12% {
    transform: translateX(-125%) skewX(-18deg);
  }
  48%,
  100% {
    transform: translateX(120%) skewX(-18deg);
  }
}

@keyframes navIconPop {
  0% {
    transform: scale(0.92) rotate(-4deg);
  }
  58% {
    transform: scale(1.12) rotate(3deg);
  }
  100% {
    transform: scale(1) rotate(0);
  }
}

@keyframes navIconGlow {
  0% {
    opacity: 0.45;
    transform: scale(0.2);
  }
  100% {
    opacity: 0;
    transform: scale(1.8);
  }
}

@keyframes dockGlassSweep {
  0%,
  28% {
    transform: translateX(-70%) skewX(-12deg);
    opacity: 0.16;
  }
  52% {
    opacity: 0.62;
  }
  82%,
  100% {
    transform: translateX(70%) skewX(-12deg);
    opacity: 0.18;
  }
}

@media (prefers-reduced-motion: reduce) {
  .liquid-button.active::before,
  .liquid-button.active .nav-icon,
  .liquid-button.active .nav-icon::after {
    animation: none !important;
  }

  .view-develop-enter-active,
  .view-develop-leave-active,
  .liquid-button,
  .journal-sidebar {
    transition: none !important;
  }

  .journal-sidebar::before {
    animation: none !important;
  }
}
</style>

