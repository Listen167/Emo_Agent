<template>
  <section :class="rootClasses" aria-label="记录发布器">
    <span v-if="variant === 'life'" class="washi-tape"></span>
    <div v-if="variant === 'life' && avatarSrc" class="xiaoxi-lab-sticker" aria-hidden="true">
      <img :src="avatarSrc" alt="" />
      <span>PHOTO LAB</span>
    </div>

    <div :class="['record-composer-heading', { 'record-composer-heading-plaza': variant === 'plaza' }]">
      <div>
        <span v-if="eyebrow" class="record-composer-eyebrow">{{ eyebrow }}</span>
        <h2>{{ title }}</h2>
      </div>
      <div v-if="variant === 'plaza'" class="record-composer-visibility" aria-label="动态可见性">
        <button
          :class="{ active: visibility === 'public' }"
          type="button"
          @click="visibility = 'public'"
        >
          公开
        </button>
        <button
          :class="{ active: visibility === 'private' }"
          type="button"
          @click="visibility = 'private'"
        >
          私密
        </button>
      </div>
    </div>

    <div class="record-composer-form">
      <input v-model="draftTitle" class="record-composer-input" maxlength="60" :placeholder="titlePlaceholder" />
      <textarea
        v-model="content"
        class="record-composer-input"
        maxlength="800"
        :placeholder="contentPlaceholder"
      />
      <input v-model="location" class="record-composer-input" maxlength="60" :placeholder="locationPlaceholder" />
      <input
        v-model="tags"
        class="record-composer-input"
        maxlength="120"
        :placeholder="tagsPlaceholder"
      />
      <select v-model="moodLabel" class="record-composer-input">
        <option value="">关联情绪（可选）</option>
        <option value="happy">开心</option>
        <option value="neutral">平静</option>
        <option value="anxious">焦虑</option>
        <option value="sad">难过</option>
        <option value="angry">生气</option>
        <option value="surprised">惊讶</option>
      </select>

      <div v-if="variant === 'life'" class="record-composer-visibility life-visibility" aria-label="记录可见性">
        <button
          :class="{ active: visibility === 'private' }"
          type="button"
          @click="visibility = 'private'"
        >
          仅自己可见
        </button>
        <button
          :class="{ active: visibility === 'public' }"
          type="button"
          @click="visibility = 'public'"
        >
          发布到广场
        </button>
      </div>

      <label class="record-composer-file-picker">
        <span>{{ image ? image.name : attachmentPlaceholder }}</span>
        <input :key="imageInputKey" type="file" accept="image/*" @change="onFileChange" />
      </label>

      <Transition name="developing-wash">
        <div v-if="developing" class="upload-developing" aria-live="polite">
          <span class="developing-window"></span>
          <div>
            <strong>PHOTO LAB</strong>
            <small>正在冲洗显影这一张照片</small>
          </div>
        </div>
      </Transition>
    </div>

    <p v-if="warning" class="moderation-warning">{{ warning }}</p>

    <footer :class="['record-composer-actions', { 'record-composer-actions-life': variant === 'life' }]">
      <span>
        {{ visibility === 'public' ? publicHint : privateHint }}
      </span>
      <button class="ghost-button" type="button" @click="resetComposer">清空</button>
      <button class="publish-button" type="button" :disabled="saving || !canSubmit" @click="submit">
        {{ saving ? savingLabel : submitLabel }}
      </button>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

import { createLifeRecord, type LifeRecordItem } from '../api/life'

type Visibility = 'private' | 'public'
type ComposerVariant = 'life' | 'plaza'

const props = withDefaults(defineProps<{
  sessionId: string
  variant?: ComposerVariant
  defaultVisibility?: Visibility
  title?: string
  eyebrow?: string
  titlePlaceholder?: string
  contentPlaceholder?: string
  locationPlaceholder?: string
  tagsPlaceholder?: string
  attachmentPlaceholder?: string
  emptyContent?: string
  privateHint?: string
  publicHint?: string
  privateSubmitLabel?: string
  publicSubmitLabel?: string
  savingLabel?: string
  moderatePublic?: boolean
  avatarSrc?: string
}>(), {
  variant: 'life',
  defaultVisibility: 'private',
  title: '新增记录',
  eyebrow: '',
  titlePlaceholder: '标题，例如：晚上的校园散步',
  contentPlaceholder: '写下今天发生了什么...',
  locationPlaceholder: '地点，例如：图书馆 / 操场',
  tagsPlaceholder: '标签，用逗号分隔，例如：学习,朋友,运动',
  attachmentPlaceholder: '选择一张照片 / Image',
  emptyContent: '分享了一张生活胶片',
  privateHint: '私密动态只保存到个人资料里的成长记录。',
  publicHint: '公开动态会进入聊天广场。',
  privateSubmitLabel: '保存记录',
  publicSubmitLabel: '发布到广场',
  savingLabel: '保存中...',
  moderatePublic: false,
  avatarSrc: '',
})

const emit = defineEmits<{
  (event: 'created', record: LifeRecordItem): void
}>()

const draftTitle = ref('')
const content = ref('')
const location = ref('')
const tags = ref('')
const moodLabel = ref('')
const visibility = ref<Visibility>(props.defaultVisibility)
const image = ref<File | null>(null)
const imageInputKey = ref(0)
const saving = ref(false)
const developing = ref(false)
const warning = ref('')
let developingTimer: number | undefined

const rootClasses = computed(() => [
  'record-composer',
  props.variant === 'life' ? 'record-form-card record-composer-life' : 'plaza-composer-card record-composer-plaza',
])
const variant = computed(() => props.variant)
const canSubmit = computed(() => Boolean(content.value.trim() || image.value))
const submitLabel = computed(() =>
  visibility.value === 'public' ? props.publicSubmitLabel : props.privateSubmitLabel
)

watch(
  () => props.defaultVisibility,
  value => {
    visibility.value = value
  }
)

onBeforeUnmount(() => {
  if (developingTimer) window.clearTimeout(developingTimer)
})

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  image.value = input.files?.[0] || null
  if (image.value) showDeveloping()
}

function showDeveloping() {
  developing.value = true
  if (developingTimer) window.clearTimeout(developingTimer)
  developingTimer = window.setTimeout(() => {
    developing.value = false
  }, 1400)
}

function resetComposer() {
  draftTitle.value = ''
  content.value = ''
  location.value = ''
  tags.value = ''
  moodLabel.value = ''
  visibility.value = props.defaultVisibility
  image.value = null
  imageInputKey.value += 1
  warning.value = ''
}

function moderateContent(value: string) {
  const riskyWords = ['傻逼', '垃圾', '去死', '人肉', '手机号', '身份证', '住址']
  const matched = riskyWords.find(word => value.includes(word))
  if (!matched) return ''
  if (['手机号', '身份证', '住址'].includes(matched)) return '这条内容可能包含隐私信息，请确认后再公开发送。'
  return '这条内容可能不符合温和社区规则，请换一种更尊重的表达。'
}

async function submit() {
  const cleanContent = content.value.trim()
  if (!cleanContent && !image.value) return

  const nextWarning = props.moderatePublic && visibility.value === 'public'
    ? moderateContent(cleanContent)
    : ''
  if (nextWarning && warning.value !== nextWarning) {
    warning.value = nextWarning
    return
  }

  saving.value = true
  warning.value = ''
  if (image.value) showDeveloping()
  try {
    const form = new FormData()
    form.append('session_id', props.sessionId)
    form.append('content', cleanContent || props.emptyContent)
    if (draftTitle.value.trim()) form.append('title', draftTitle.value.trim())
    if (location.value.trim()) form.append('location', location.value.trim())
    if (tags.value.trim()) form.append('tags', tags.value.trim())
    if (moodLabel.value) form.append('mood_label', moodLabel.value)
    form.append('visibility', visibility.value)
    if (image.value) form.append('image', image.value)

    const { data } = await createLifeRecord(form)
    emit('created', data)
    resetComposer()
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.record-composer {
  position: relative;
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 18px 42px rgb(62 50 40 / 16%);
}

.record-composer-life {
  position: sticky;
  top: 24px;
  height: fit-content;
  padding: 24px;
  clip-path: polygon(0 2%, 98% 0, 100% 97%, 2% 100%);
}

.record-composer-plaza {
  margin-top: 18px;
  padding: 20px;
  border-color: rgb(62 50 40 / 16%);
  background:
    linear-gradient(115deg, rgb(255 248 232 / 86%), rgb(253 251 247 / 72%)),
    #fff8e8;
  box-shadow: 0 16px 34px rgb(62 50 40 / 12%);
}

.washi-tape {
  position: absolute;
  top: -12px;
  left: 34px;
  width: 112px;
  height: 28px;
  rotate: -4deg;
  background: rgb(232 195 108 / 58%);
  border: 1px solid rgb(62 50 40 / 10%);
}

.xiaoxi-lab-sticker {
  position: absolute;
  right: 16px;
  top: -18px;
  z-index: 2;
  display: grid;
  justify-items: center;
  width: 76px;
  padding: 6px 6px 7px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 12px;
  background: rgb(253 251 247 / 92%);
  box-shadow: 0 10px 18px rgb(62 50 40 / 12%);
  rotate: 4deg;
  pointer-events: none;
}

.xiaoxi-lab-sticker img {
  width: 52px;
  height: 52px;
  object-fit: contain;
  filter: drop-shadow(0 5px 8px rgb(62 50 40 / 13%));
  animation: labStickerFloat 3.4s ease-in-out infinite;
}

.xiaoxi-lab-sticker span {
  margin-top: -3px;
  color: var(--journal-stamp);
  font-size: 9px;
  font-weight: 900;
}

.record-composer-heading,
.record-composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.record-composer-heading h2 {
  margin: 0 0 16px;
  color: var(--journal-ink);
  font-size: 22px;
}

.record-composer-heading-plaza h2 {
  margin: 4px 0 0;
}

.record-composer-eyebrow {
  display: inline-block;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.record-composer-form {
  display: grid;
  gap: 12px;
}

.record-composer-plaza .record-composer-form {
  gap: 10px;
  margin-top: 16px;
}

.record-composer-input {
  width: 100%;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.72rem 0.8rem;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
}

textarea.record-composer-input {
  min-height: 112px;
  resize: vertical;
  line-height: 1.6;
}

.record-composer-input:focus {
  border-color: rgb(200 90 84 / 48%);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
}

.record-composer-visibility {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 5px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 12px;
  background: rgb(253 251 247 / 58%);
}

.record-composer-plaza .record-composer-visibility {
  display: inline-flex;
  border-radius: 13px;
  background: rgb(253 251 247 / 64%);
}

.record-composer-visibility button {
  min-height: 36px;
  border-radius: 9px;
  color: var(--journal-muted);
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.record-composer-plaza .record-composer-visibility button {
  min-height: 34px;
  padding: 0 13px;
}

.record-composer-visibility button.active {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 8px 16px rgb(62 50 40 / 14%);
}

.record-composer-plaza .record-composer-visibility button.active {
  background: var(--journal-stamp);
  box-shadow: 0 7px 16px rgb(200 90 84 / 16%);
}

.record-composer-file-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 44px;
  padding: 0 12px;
  border: 1px dashed rgb(62 50 40 / 34%);
  border-radius: 10px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 58%);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.record-composer-file-picker::after {
  content: "选择图片";
  color: var(--journal-stamp);
}

.record-composer-file-picker input {
  display: none;
}

.upload-developing {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  padding: 10px;
  border: 1px dashed rgb(62 50 40 / 20%);
  border-radius: 12px;
  background: rgb(253 251 247 / 68%);
  overflow: hidden;
}

.developing-window {
  position: relative;
  height: 46px;
  border-radius: 8px;
  border: 1px solid rgb(62 50 40 / 16%);
  background:
    linear-gradient(90deg, transparent 0 10%, rgb(62 50 40 / 22%) 10% 14%, transparent 14% 28%, rgb(62 50 40 / 20%) 28% 32%, transparent 32% 100%),
    linear-gradient(135deg, #30251d, #e8c36c 54%, #fff8e8);
  box-shadow: inset 0 0 0 5px rgb(32 21 15 / 82%);
}

.developing-window::after {
  content: "";
  position: absolute;
  inset: 6px;
  background: linear-gradient(90deg, transparent, rgb(255 248 232 / 76%), transparent);
  transform: translateX(-120%);
  animation: developingSweep 1.15s ease-in-out infinite;
}

.upload-developing strong,
.upload-developing small {
  display: block;
}

.upload-developing strong {
  color: var(--journal-stamp);
  font-size: 12px;
}

.upload-developing small {
  margin-top: 4px;
  color: var(--journal-muted);
  font-size: 12px;
}

.developing-wash-enter-active,
.developing-wash-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease, filter 0.28s ease;
}

.developing-wash-enter-from,
.developing-wash-leave-to {
  opacity: 0;
  transform: translateY(8px);
  filter: blur(5px);
}

.moderation-warning {
  margin: 10px 0 0;
  padding: 10px 12px;
  border-left: 4px solid var(--journal-stamp);
  color: var(--journal-stamp);
  background: rgb(255 231 224 / 68%);
  font-size: 12px;
  line-height: 1.55;
}

.record-composer-actions {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed rgb(62 50 40 / 18%);
}

.record-composer-actions span {
  color: var(--journal-muted);
  font-size: 12px;
}

.record-composer-actions-life {
  display: grid;
  grid-template-columns: 1fr;
}

.record-composer-actions-life span {
  line-height: 1.45;
}

.ghost-button {
  min-height: 40px;
  border-radius: 10px;
  padding: 0 14px;
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 70%);
  cursor: pointer;
}

.publish-button {
  min-height: 40px;
  border-radius: 10px;
  padding: 0 16px;
  color: #fff8e8;
  font-weight: 700;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 18%);
  cursor: pointer;
}

.record-composer-actions-life .publish-button {
  width: 100%;
  min-height: 46px;
  border-radius: 12px;
}

.publish-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes developingSweep {
  to {
    transform: translateX(120%);
  }
}

@keyframes labStickerFloat {
  0%,
  100% {
    transform: translateY(0) rotate(-1deg);
  }
  50% {
    transform: translateY(-3px) rotate(2deg);
  }
}

@media (max-width: 920px) {
  .record-composer-life {
    position: relative;
    top: auto;
    margin-bottom: 24px;
  }
}

@media (max-width: 680px) {
  .record-composer-heading,
  .record-composer-actions {
    display: grid;
  }

  .record-composer-plaza .record-composer-visibility {
    width: 100%;
  }

  .record-composer-plaza .record-composer-visibility button {
    flex: 1;
  }
}
</style>
