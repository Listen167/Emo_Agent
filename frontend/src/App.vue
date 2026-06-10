<script setup lang="ts">
import { computed, ref } from 'vue'

import ProfileCard from './components/ProfileCard.vue'
import ChatView from './views/ChatView.vue'
import LandingView from './views/LandingView.vue'
import LifeRecordView from './views/LifeRecordView.vue'
import MoodCalendarView from './views/MoodCalendarView.vue'
import ResumeView from './views/ResumeView.vue'
import { BACKEND_ORIGIN } from './api/client'

const showLanding = ref(true)
const sessionId = ref(localStorage.getItem('sid') || crypto.randomUUID())
localStorage.setItem('sid', sessionId.value)
const activeView = ref<'chat' | 'life' | 'mood' | 'resume' | 'ebti'>('chat')
const townUrl = `/ai-town/index.html${BACKEND_ORIGIN ? `?backend=${encodeURIComponent(`${BACKEND_ORIGIN}/api/town`)}` : ''}`
const navItems = [
  { key: 'chat', cn: '首页', en: 'Home', icon: '⌂', note: '和小曦对话' },
  { key: 'life', cn: '胶卷库', en: 'Rolls', icon: '▣', note: '生活记录' },
  { key: 'mood', cn: '拍摄记录', en: 'Log', icon: '◫', note: '心情日历' },
  { key: 'resume', cn: '简历工坊', en: 'Resume', icon: '▤', note: '简历制作' },
  { key: 'ebti', cn: '我的暗房', en: 'Darkroom', icon: '✦', note: 'EBTI 测试' },
] as const
const activeLabel = computed(() => navItems.find(item => item.key === activeView.value)?.note || 'Film Journal')
</script>

<template>
  <!-- 开场动画 -->
  <Transition name="landing-fade">
    <LandingView v-if="showLanding" @enter="showLanding = false" />
  </Transition>

  <div v-if="!showLanding" class="journal-shell paper-texture">
    <aside class="journal-sidebar">
      <div class="sidebar-brand">
        <div class="brand-row">
          <span class="menu-mark">☰</span>
          <span class="camera-mark">◉</span>
        </div>
        <h1 class="script-title">Film Journal</h1>
        <p>记录每一次快门的心跳</p>
      </div>

      <ProfileCard :session-id="sessionId" />

      <nav class="liquid-nav" aria-label="主功能">
        <button
          v-for="item in navItems"
          :key="item.key"
          :class="['liquid-button', { active: activeView === item.key }]"
          @click="activeView = item.key"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span>
            <strong>{{ item.cn }}</strong>
            <small>{{ item.en }} · {{ item.note }}</small>
          </span>
        </button>
        <a class="liquid-button town-link" :href="townUrl" target="_blank">
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
      <ChatView v-if="activeView === 'chat'" />
      <LifeRecordView v-else-if="activeView === 'life'" />
      <MoodCalendarView v-else-if="activeView === 'mood'" />
      <ResumeView v-else-if="activeView === 'resume'" />
      <main v-else class="embedded-page">
        <div class="embedded-frame">
          <iframe
            src="/ebti-test/index.html"
            title="EBTI 测试"
          ></iframe>
        </div>
      </main>
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
  height: 100vh;
  display: grid;
  grid-template-columns: 286px minmax(0, 1fr);
}

.journal-sidebar {
  position: relative;
  z-index: 20;
  height: 100vh;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 20px;
  border-right: 1px solid rgb(62 50 40 / 18%);
  background:
    linear-gradient(90deg, rgb(62 50 40 / 8%), transparent 20%),
    rgb(253 251 247 / 54%);
  box-shadow: 14px 0 40px rgb(62 50 40 / 10%);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.sidebar-brand {
  position: relative;
  padding: 8px 6px 0;
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--journal-ink);
  font-size: 23px;
}

.menu-mark {
  font-size: 26px;
}

.camera-mark {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: var(--journal-kodak);
  border: 1px solid rgb(62 50 40 / 24%);
  box-shadow: 0 8px 18px rgb(62 50 40 / 18%);
}

.sidebar-brand h1 {
  margin: 14px 0 2px;
  font-size: 45px;
  line-height: 0.95;
  color: var(--journal-ink);
}

.sidebar-brand p {
  margin: 0;
  color: var(--journal-muted);
  font-size: 13px;
}

.liquid-nav {
  display: grid;
  gap: 13px;
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
    inset 0 -12px 26px rgb(232 195 108 / 14%),
    0 15px 32px rgb(62 50 40 / 16%),
    0 2px 6px rgb(62 50 40 / 10%);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
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
  transform: translateY(-2px) scale(1.015);
  background:
    linear-gradient(135deg, rgb(255 255 255 / 86%), rgb(232 195 108 / 26%)),
    rgb(255 255 255 / 66%);
  box-shadow:
    inset 0 1px 2px rgb(255 255 255),
    inset 0 -14px 28px rgb(232 195 108 / 20%),
    0 20px 42px rgb(62 50 40 / 22%);
}

.liquid-button:hover::before,
.liquid-button.active::before {
  transform: translateX(120%) skewX(-18deg);
}

.nav-icon {
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

.journal-stage {
  position: relative;
  z-index: 1;
  min-width: 0;
  min-height: 0;
  height: 100vh;
  overflow: auto;
  overscroll-behavior: contain;
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

  .journal-sidebar {
    position: fixed;
    inset: auto 12px 12px;
    width: auto;
    height: auto;
    padding: 10px;
    border: 1px solid rgb(255 255 255 / 52%);
    border-radius: 24px;
    background: rgb(255 248 232 / 56%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }

  .journal-stage {
    height: 100vh;
    padding-bottom: 92px;
    overflow: auto;
  }

  .sidebar-brand,
  .profile-card,
  .sidebar-ticket,
  .sidebar-film {
    display: none;
  }

  .liquid-nav {
    display: flex;
    gap: 8px;
    overflow-x: auto;
  }

  .liquid-button {
    min-width: 78px;
    min-height: 56px;
    justify-content: center;
    padding: 8px 10px;
  }

  .liquid-button small {
    display: none;
  }
}
</style>
