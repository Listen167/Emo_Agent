<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

type AuthMode = 'login' | 'register'

const emit = defineEmits<{
  authenticated: [payload: { email: string; nickname: string }]
}>()

const mode = ref<AuthMode>('login')
const error = ref('')
const form = reactive({
  email: '',
  password: '',
  nickname: '',
})

const isRegister = computed(() => mode.value === 'register')
const title = computed(() => (isRegister.value ? '创建你的胶片账号' : '回到 U-Life'))
const subtitle = computed(() =>
  isRegister.value ? '用邮箱留下你的身份，之后每一次记录都能被找回。' : '输入邮箱，继续和小曦一起记录今天。',
)

const switchMode = (nextMode: AuthMode) => {
  mode.value = nextMode
  error.value = ''
}

const isEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)

const submit = () => {
  const email = form.email.trim().toLowerCase()
  const password = form.password.trim()
  const nickname = form.nickname.trim()

  if (!isEmail(email)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  if (password.length < 6) {
    error.value = '密码至少需要 6 位'
    return
  }
  if (isRegister.value && !nickname) {
    error.value = '注册时需要填写昵称'
    return
  }

  const displayName = nickname || email.split('@')[0] || '胶片旅人'
  localStorage.setItem('auth_email', email)
  localStorage.setItem('auth_nickname', displayName)
  localStorage.setItem('auth_mode', mode.value)
  emit('authenticated', { email, nickname: displayName })
}
</script>

<template>
  <main class="auth-view paper-texture">
    <section class="auth-panel" aria-label="邮箱登录注册">
      <div class="auth-brand">
        <span class="kodak-chip">U-Life Account</span>
        <h1 class="script-title">Film Journal</h1>
        <p>{{ subtitle }}</p>
      </div>

      <div class="auth-card">
        <div class="auth-tabs" role="tablist">
          <button :class="{ active: mode === 'login' }" type="button" @click="switchMode('login')">登录</button>
          <button :class="{ active: mode === 'register' }" type="button" @click="switchMode('register')">注册</button>
        </div>

        <form class="auth-form" @submit.prevent="submit">
          <header>
            <strong>{{ title }}</strong>
            <small>{{ isRegister ? '邮箱注册' : '邮箱登录' }}</small>
          </header>

          <label>
            <span>邮箱</span>
            <input v-model="form.email" type="email" autocomplete="email" placeholder="you@example.com" />
          </label>

          <label v-if="isRegister">
            <span>昵称</span>
            <input v-model="form.nickname" type="text" maxlength="24" autocomplete="nickname" placeholder="给自己取个名字" />
          </label>

          <label>
            <span>密码</span>
            <input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              placeholder="至少 6 位"
            />
          </label>

          <p v-if="error" class="auth-error">{{ error }}</p>

          <button class="auth-submit" type="submit">
            {{ isRegister ? '注册并进入' : '登录' }}
          </button>
        </form>
      </div>
    </section>

    <aside class="auth-visual" aria-hidden="true">
      <div class="film-card primary">
        <span>EMAIL</span>
        <strong>你的记录会和邮箱绑定</strong>
      </div>
      <div class="film-card">
        <span>XIAOXI</span>
        <strong>登录后继续进入小曦的世界</strong>
      </div>
    </aside>
  </main>
</template>

<style scoped>
.auth-view {
  position: relative;
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 440px);
  gap: 32px;
  padding: 36px;
  overflow: hidden;
}

.auth-panel {
  position: relative;
  z-index: 1;
  display: grid;
  align-content: center;
  max-width: 760px;
}

.auth-brand {
  max-width: 620px;
}

.kodak-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.auth-brand h1 {
  margin: 18px 0 0;
  color: var(--journal-ink);
  font-size: clamp(60px, 10vw, 112px);
  line-height: 0.86;
}

.auth-brand p {
  margin: 16px 0 0;
  max-width: 480px;
  color: var(--journal-muted);
  font-size: 15px;
  line-height: 1.7;
}

.auth-card {
  width: min(100%, 430px);
  margin-top: 34px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 78%);
  box-shadow: 0 20px 48px rgb(62 50 40 / 18%);
}

.auth-tabs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  padding: 8px;
  gap: 8px;
}

.auth-tabs button {
  min-height: 38px;
  border-radius: 10px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 68%);
  cursor: pointer;
  font-weight: 700;
}

.auth-tabs button.active {
  color: #fff8e8;
  background: var(--journal-stamp);
}

.auth-form {
  display: grid;
  gap: 14px;
  padding: 20px;
}

.auth-form header strong,
.auth-form header small {
  display: block;
}

.auth-form header strong {
  color: var(--journal-ink);
  font-size: 22px;
}

.auth-form header small {
  margin-top: 4px;
  color: var(--journal-muted);
  font-size: 12px;
}

.auth-form label {
  display: grid;
  gap: 6px;
}

.auth-form label span {
  color: var(--journal-muted);
  font-size: 12px;
  font-weight: 700;
}

.auth-form input {
  width: 100%;
  min-height: 44px;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0 12px;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 92%);
}

.auth-form input:focus {
  border-color: var(--journal-stamp);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 13%);
}

.auth-error {
  margin: 0;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.auth-submit {
  min-height: 44px;
  border-radius: 12px;
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
  font-weight: 700;
}

.auth-visual {
  position: relative;
  z-index: 1;
  display: grid;
  align-content: center;
  gap: 18px;
}

.film-card {
  min-height: 150px;
  padding: 22px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: #fff8e8;
  box-shadow: 0 20px 42px rgb(62 50 40 / 14%);
}

.film-card.primary {
  background:
    radial-gradient(circle at 78% 18%, rgb(232 195 108 / 30%), transparent 7rem),
    #fff8e8;
}

.film-card span,
.film-card strong {
  display: block;
}

.film-card span {
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.film-card strong {
  margin-top: 12px;
  max-width: 260px;
  color: var(--journal-ink);
  font-size: 22px;
  line-height: 1.35;
}

@media (max-width: 860px) {
  .auth-view {
    display: block;
    padding: 20px;
    overflow: auto;
  }

  .auth-panel {
    min-height: calc(100vh - 40px);
  }

  .auth-brand h1 {
    font-size: 64px;
  }

  .auth-visual {
    display: none;
  }
}
</style>
