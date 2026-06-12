<template>
  <Transition name="onboarding-motion">
    <div class="onboarding-mask" role="dialog" aria-modal="true" aria-label="首次个性化引导">
      <section class="onboarding-card">
        <span class="washi-tape"></span>
        <header>
          <span class="kodak-chip">FIRST ROLL</span>
          <h2 class="script-title">先认识一下你</h2>
          <p>这一步会生成本地成长档案，用来驱动小曦人格、周报和隐私设置。</p>
        </header>

        <div class="onboarding-grid">
          <label>
            <span>昵称</span>
            <input v-model="draft.nickname" maxlength="32" placeholder="例如：小林" />
          </label>
          <label>
            <span>今天的状态</span>
            <select v-model="draft.currentState">
              <option value="有点累，但想继续推进">有点累，但想继续推进</option>
              <option value="状态不错，想记录生活">状态不错，想记录生活</option>
              <option value="压力较大，需要陪伴">压力较大，需要陪伴</option>
              <option value="准备求职，需要成长建议">准备求职，需要成长建议</option>
            </select>
          </label>
          <label>
            <span>最近最想解决</span>
            <select v-model="draft.focus">
              <option value="情绪陪伴">情绪陪伴</option>
              <option value="生活记录">生活记录</option>
              <option value="求职简历">求职简历</option>
              <option value="自我理解">自我理解</option>
            </select>
          </label>
          <label>
            <span>小曦人格</span>
            <select v-model="draft.personality">
              <option value="warm">温柔陪伴型</option>
              <option value="coach">成长教练型</option>
              <option value="rational">理性分析型</option>
              <option value="bright">元气鼓励型</option>
            </select>
          </label>
        </div>

        <label class="wide-field">
          <span>本周目标</span>
          <textarea v-model="draft.weeklyGoal" maxlength="160" placeholder="例如：每天记录一次情绪，把简历项目经历整理清楚。" />
        </label>

        <footer>
          <button class="ghost-button" type="button" @click="skip">稍后再说</button>
          <button class="save-button" type="button" @click="complete">生成成长档案</button>
        </footer>
      </section>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const emit = defineEmits<{ complete: [] }>()

const draft = reactive({
  nickname: '',
  currentState: '有点累，但想继续推进',
  focus: '情绪陪伴',
  personality: 'warm',
  weeklyGoal: '',
})

const saveSetup = (completed: boolean) => {
  const payload = {
    ...draft,
    nickname: draft.nickname.trim() || '胶片旅人',
    weeklyGoal: draft.weeklyGoal.trim() || '每天留下一次真实记录',
    completed,
    createdAt: new Date().toISOString(),
  }
  localStorage.setItem('u-life-user-setup-v1', JSON.stringify(payload))
  localStorage.setItem('u-life-xiaoxi-personality-v1', draft.personality)
  window.dispatchEvent(new CustomEvent('u-life-settings-changed'))
}

const complete = () => {
  saveSetup(true)
  emit('complete')
}

const skip = () => {
  saveSetup(false)
  emit('complete')
}
</script>

<style scoped>
.onboarding-mask {
  position: fixed;
  inset: 0;
  z-index: 160;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgb(28 19 14 / 46%);
}

.onboarding-card {
  position: relative;
  width: min(720px, 100%);
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  padding: 28px;
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 30px 90px rgb(28 19 14 / 34%);
}

.washi-tape {
  position: absolute;
  top: -13px;
  left: 42px;
  width: 132px;
  height: 30px;
  rotate: -4deg;
  background: rgb(232 195 108 / 58%);
  border: 1px solid rgb(62 50 40 / 10%);
}

.kodak-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

h2 {
  margin: 10px 0 0;
  font-size: clamp(42px, 7vw, 68px);
  line-height: 0.92;
}

p {
  margin: 10px 0 0;
  color: var(--journal-muted);
  font-size: 14px;
}

.onboarding-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

label,
.wide-field {
  display: grid;
  gap: 7px;
}

label span,
.wide-field span {
  color: var(--journal-muted);
  font-size: 12px;
  font-weight: 700;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.72rem 0.8rem;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
}

textarea {
  min-height: 96px;
  resize: vertical;
  line-height: 1.6;
}

input:focus,
select:focus,
textarea:focus {
  border-color: rgb(200 90 84 / 48%);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
}

.wide-field {
  margin-top: 14px;
}

footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

.ghost-button,
.save-button {
  min-height: 42px;
  border-radius: 10px;
  padding: 0 16px;
  cursor: pointer;
  font-weight: 700;
}

.ghost-button {
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 70%);
}

.save-button {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 16%);
}

.onboarding-motion-enter-active,
.onboarding-motion-leave-active {
  transition: opacity 0.28s ease;
}

.onboarding-motion-enter-active .onboarding-card,
.onboarding-motion-leave-active .onboarding-card {
  transition:
    transform 0.34s cubic-bezier(0.2, 0.9, 0.2, 1),
    filter 0.34s ease,
    opacity 0.34s ease;
}

.onboarding-motion-enter-from,
.onboarding-motion-leave-to {
  opacity: 0;
}

.onboarding-motion-enter-from .onboarding-card {
  opacity: 0;
  transform: translateY(28px) scale(0.94) rotate(-1.2deg);
  filter: blur(12px) sepia(0.35);
}

@media (max-width: 680px) {
  .onboarding-card {
    padding: 24px 18px;
  }

  .onboarding-grid {
    grid-template-columns: 1fr;
  }

  footer {
    display: grid;
  }
}
</style>
