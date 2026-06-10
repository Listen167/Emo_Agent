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
      <div v-if="editing" class="profile-modal-mask" @click.self="closeEditor">
        <section class="profile-modal" role="dialog" aria-modal="true" aria-label="编辑个人资料">
          <header class="profile-modal-header">
            <div>
              <span>PROFILE</span>
              <h2>个人资料</h2>
            </div>
            <button class="close-button" type="button" @click="closeEditor">关闭</button>
          </header>

          <div class="avatar-editor">
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
            <small>后续接入 EBTI 结果同步后，这里会自动显示第一次测试结果。</small>
          </div>

          <footer class="profile-modal-actions">
            <button class="ghost-button" type="button" @click="closeEditor">取消</button>
            <button class="save-button" type="button" :disabled="saving" @click="saveProfile">
              {{ saving ? '保存中...' : '保存资料' }}
            </button>
          </footer>
        </section>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { getProfile, updateProfile, uploadProfileAvatar, type UserProfile } from '../api/profile'
import { resolveAssetUrl } from '../api/client'

const props = defineProps<{
  sessionId: string
}>()

const profile = ref<UserProfile | null>(null)
const editing = ref(false)
const saving = ref(false)
const avatarFile = ref<File | null>(null)
const draftAvatarUrl = ref('')
const draft = reactive({
  nickname: '',
  motto: '',
  gender: '',
})

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

onMounted(() => {
  void loadProfile()
})

watch(
  () => props.sessionId,
  () => {
    void loadProfile()
  }
)

const loadProfile = async () => {
  if (!props.sessionId) return
  const { data } = await getProfile(props.sessionId)
  profile.value = data
  syncDraft(data)
}

const syncDraft = (value: UserProfile | null) => {
  draft.nickname = value?.nickname || ''
  draft.motto = value?.motto || ''
  draft.gender = value?.gender || ''
  draftAvatarUrl.value = value?.avatar_url ? resolveAssetUrl(value.avatar_url) : ''
  avatarFile.value = null
}

const openEditor = () => {
  syncDraft(profile.value)
  editing.value = true
}

const closeEditor = () => {
  editing.value = false
  syncDraft(profile.value)
}

const onAvatarChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] || null
  avatarFile.value = file
  if (file) {
    draftAvatarUrl.value = URL.createObjectURL(file)
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
    editing.value = false
  } finally {
    saving.value = false
  }
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
  width: min(520px, 100%);
  max-height: min(760px, calc(100vh - 40px));
  overflow-y: auto;
  padding: 24px;
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 28px 80px rgb(28 19 14 / 32%);
}

.profile-modal-header {
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
  display: flex;
  align-items: center;
  gap: 18px;
  margin-top: 22px;
}

.large-avatar {
  width: 96px;
  height: 96px;
  border-radius: 22px;
  font-size: 34px;
}

.avatar-upload {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
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
  gap: 14px;
  margin-top: 22px;
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
  min-height: 92px;
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
  margin-top: 18px;
  padding: 14px;
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

.profile-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

.save-button {
  min-height: 40px;
  border-radius: 10px;
  padding: 0 16px;
  color: #fff8e8;
  font-weight: 700;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.save-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
