<template>
  <div class="plaza-view">
    <header v-develop class="plaza-header">
      <div>
        <span class="kodak-chip">Public Contact Sheet</span>
        <h1 class="script-title">聊天广场</h1>
        <p>这里收集大家公开发布的生活胶片。点赞、评论，给彼此留下一点回声。</p>
      </div>
      <div class="plaza-header-actions">
        <label class="anonymous-toggle">
          <input v-model="anonymousMode" type="checkbox" @change="saveAnonymousMode" />
          <span>匿名互动</span>
        </label>
        <button class="refresh-button" :disabled="loading" @click="loadPosts">
          {{ loading ? '刷新中...' : '刷新广场' }}
        </button>
      </div>
    </header>

    <main class="plaza-layout">
      <section class="plaza-feed">
        <div v-if="posts.length === 0 && !loading" class="empty-plaza">
          <span>NO PUBLIC ROLL</span>
          <p>还没有公开记录。去胶卷库发布第一条广场胶片吧。</p>
        </div>

        <article v-for="post in posts" :key="post.id" v-develop="90" class="plaza-post">
          <header class="post-author-row">
            <span class="author-avatar">
              <img v-if="post.author.avatar_url" :src="authorAvatarUrl(post.author.avatar_url)" alt="用户头像" />
              <span v-else>{{ post.author.nickname.slice(0, 1) }}</span>
            </span>
            <div class="author-copy">
              <strong>{{ post.author.nickname }}</strong>
              <small>
                {{ formatTime(post.published_at || post.created_at) }}
                <template v-if="post.author.ebti_type">
                  · {{ post.author.ebti_type }} {{ post.author.ebti_name || '' }}
                </template>
              </small>
            </div>
          </header>

          <div class="post-body">
            <h2 v-if="post.title">{{ post.title }}</h2>
            <p>{{ post.content }}</p>
            <div v-if="post.media_url" class="post-image-frame">
              <img :src="resolveAssetUrl(post.media_url)" alt="生活记录图片" />
            </div>
            <div class="post-tags">
              <span v-if="post.xiaoxi_liked" class="xiaoxi-like-tag">小曦喜欢过</span>
              <span v-if="post.location">地点：{{ post.location }}</span>
              <span v-if="post.mood_label">情绪：{{ moodText(post.mood_label) }}</span>
              <span v-for="tag in post.tags" :key="tag">#{{ tag }}</span>
            </div>
          </div>

          <footer class="post-actions">
            <button
              :class="{ active: post.liked, 'action-pulse': reactionKey === `${post.id}-like` }"
              @click="toggleLike(post)"
            >
              {{ post.liked ? '已喜欢' : '喜欢' }} · {{ post.like_count }}
            </button>
            <button
              :class="{ active: openCommentPostId === post.id, 'action-pulse': reactionKey === `${post.id}-comment` }"
              @click="toggleComments(post)"
            >
              评论 · {{ post.comment_count }}
            </button>
            <button
              :class="{ active: post.reposted, 'action-pulse': reactionKey === `${post.id}-repost` }"
              @click="repost(post)"
            >
              {{ post.reposted ? '已转发' : '转发' }} · {{ post.repost_count }}
            </button>
          </footer>

          <section v-if="openCommentPostId === post.id" class="comments-panel">
            <div class="comment-list">
              <p v-if="comments[post.id]?.length === 0" class="empty-comments">还没有评论。</p>
              <article
                v-for="comment in comments[post.id] || []"
                :key="comment.id"
                :class="['comment-item', { 'xiaoxi-comment': comment.author_type === 'xiaoxi' }]"
              >
                <span class="comment-avatar">
                  <img v-if="comment.author.avatar_url" :src="authorAvatarUrl(comment.author.avatar_url)" alt="评论者头像" />
                  <span v-else>{{ comment.author.nickname.slice(0, 1) }}</span>
                </span>
                <div class="comment-main">
                  <div class="comment-meta">
                    <strong>{{ commentAuthorName(comment) }}</strong>
                    <small>{{ formatTime(comment.created_at) }}</small>
                  </div>
                  <p>{{ comment.content }}</p>
                  <div class="comment-tools">
                    <button @click="beginReply(post.id, comment.id, comment.id, commentAuthorName(comment))">回复</button>
                    <button
                      v-if="comment.reply_count > comment.replies.length"
                      @click="loadAllReplies(comment)"
                    >
                      展开全部 {{ comment.reply_count }} 条回复
                    </button>
                  </div>

                  <div v-if="comment.replies.length" class="reply-thread">
                    <article
                      v-for="reply in comment.replies"
                      :key="reply.id"
                      :class="['reply-item', { 'xiaoxi-reply': reply.author_type === 'xiaoxi' }]"
                    >
                      <span class="reply-avatar">
                        <img v-if="reply.author.avatar_url" :src="authorAvatarUrl(reply.author.avatar_url)" alt="回复者头像" />
                        <span v-else>{{ reply.author.nickname.slice(0, 1) }}</span>
                      </span>
                      <div class="reply-main">
                        <div class="comment-meta">
                          <strong>{{ commentAuthorName(reply) }}</strong>
                          <small>{{ formatTime(reply.created_at) }}</small>
                        </div>
                        <p>
                          <span v-if="reply.reply_to_author" class="reply-to">
                            回复 {{ replyAuthorName(reply.reply_to_author) }}：
                          </span>
                          {{ reply.content }}
                        </p>
                        <div class="comment-tools compact">
                          <button @click="beginReply(post.id, comment.id, reply.id, commentAuthorName(reply))">回复</button>
                        </div>
                      </div>
                    </article>
                  </div>

                  <div v-if="isReplying(post.id, comment.id)" class="reply-composer">
                    <input
                      v-model="replyDraft"
                      :placeholder="`回复 ${activeReplyTarget?.targetName || '这条评论'}，@小曦 她也会回应...`"
                      @keydown.enter.prevent="submitReply(post, comment)"
                    />
                    <button :disabled="!replyDraft.trim()" @click="submitReply(post, comment)">发送</button>
                    <button class="ghost-button" @click="cancelReply">取消</button>
                  </div>
                </div>
              </article>
            </div>
            <div class="comment-composer">
              <input
                v-model="commentDrafts[post.id]"
                placeholder="写下你的回复，@小曦 她一定会回应..."
                @keydown.enter.prevent="submitComment(post)"
              />
              <button :disabled="!commentDrafts[post.id]?.trim()" @click="submitComment(post)">发送</button>
            </div>
            <p v-if="moderationWarnings[post.id]" class="moderation-warning">
              {{ moderationWarnings[post.id] }}
            </p>
          </section>
        </article>
      </section>

      <aside class="plaza-side">
        <section v-develop="120" class="side-note">
          <span>PLAZA</span>
          <strong>{{ posts.length }}</strong>
          <p>公开胶片</p>
        </section>
        <section v-develop="160" class="side-rule">
          <h2>广场规则</h2>
          <p>只有在胶卷库选择“发布到广场”的记录会出现在这里。私密记录仍然只保存在自己的胶卷库。</p>
        </section>
        <section v-develop="200" class="moderation-card">
          <h2>温和社区机制</h2>
          <ul>
            <li>匿名互动默认隐藏身份线索。</li>
            <li>发送前检测攻击性和隐私泄露风险。</li>
            <li>后端可继续接入举报、屏蔽和人工审核队列。</li>
          </ul>
        </section>
      </aside>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import {
  createPlazaCommentReply,
  createPlazaComment,
  getPlazaCommentReplies,
  getPlazaComments,
  getPlazaPosts,
  likePlazaPost,
  repostPlazaPost,
  unlikePlazaPost,
  type PlazaCommentItem,
  type PlazaCommentReplyItem,
  type PlazaPostItem,
} from '../api/plaza'
import { resolveAssetUrl } from '../api/client'
import { createClientId } from '../utils/id'

const sid = ref(localStorage.getItem('sid') || createClientId())
const posts = ref<PlazaPostItem[]>([])
const comments = reactive<Record<number, PlazaCommentItem[]>>({})
const commentDrafts = reactive<Record<number, string>>({})
const replyDraft = ref('')
const openCommentPostId = ref<number | null>(null)
const activeReplyTarget = ref<{
  postId: number
  parentId: number
  targetId: number
  targetName: string
} | null>(null)
const loading = ref(false)
const anonymousMode = ref(localStorage.getItem('u-life-plaza-anonymous-v1') === 'true')
const moderationWarnings = reactive<Record<number, string>>({})
const reactionKey = ref('')
let reactionTimer: number | undefined

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  void loadPosts()
})

onBeforeUnmount(() => {
  if (reactionTimer) window.clearTimeout(reactionTimer)
})

const loadPosts = async () => {
  loading.value = true
  try {
    const { data } = await getPlazaPosts(sid.value)
    posts.value = data
  } finally {
    loading.value = false
  }
}

const replacePost = (next: PlazaPostItem) => {
  const index = posts.value.findIndex(post => post.id === next.id)
  if (index >= 0) posts.value[index] = { ...posts.value[index], ...next }
}

const saveAnonymousMode = () => {
  localStorage.setItem('u-life-plaza-anonymous-v1', String(anonymousMode.value))
  window.dispatchEvent(new CustomEvent('u-life-settings-changed'))
}

const moderateContent = (content: string) => {
  const riskyWords = ['傻逼', '垃圾', '去死', '人肉', '手机号', '身份证', '住址']
  const matched = riskyWords.find(word => content.includes(word))
  if (!matched) return ''
  if (['手机号', '身份证', '住址'].includes(matched)) return '这条内容可能包含隐私信息，请确认后再公开发送。'
  return '这条内容可能不符合温和社区规则，请换一种更尊重的表达。'
}

const authorAvatarUrl = (url: string) => {
  if (url.startsWith('/xiaoxi/')) return url
  return resolveAssetUrl(url)
}

const toggleLike = async (post: PlazaPostItem) => {
  pulseAction(post.id, 'like')
  const { data } = post.liked
    ? await unlikePlazaPost(post.id, sid.value)
    : await likePlazaPost(post.id, sid.value)
  replacePost({
    ...post,
    ...data,
    liked: !post.liked,
    reposted: post.reposted,
  })
}

const repost = async (post: PlazaPostItem) => {
  if (post.reposted) return
  pulseAction(post.id, 'repost')
  const { data } = await repostPlazaPost(post.id, sid.value)
  replacePost({
    ...post,
    ...data,
    liked: post.liked,
    reposted: true,
  })
}

const toggleComments = async (post: PlazaPostItem) => {
  pulseAction(post.id, 'comment')
  if (openCommentPostId.value === post.id) {
    openCommentPostId.value = null
    cancelReply()
    return
  }
  openCommentPostId.value = post.id
  if (!comments[post.id]) {
    const { data } = await getPlazaComments(post.id)
    comments[post.id] = data
  }
}

const pulseAction = (postId: number, action: 'like' | 'comment' | 'repost') => {
  reactionKey.value = `${postId}-${action}`
  if (reactionTimer) window.clearTimeout(reactionTimer)
  reactionTimer = window.setTimeout(() => {
    reactionKey.value = ''
  }, 420)
}

const submitComment = async (post: PlazaPostItem) => {
  const content = (commentDrafts[post.id] || '').trim()
  if (!content) return
  const warning = moderateContent(content)
  if (warning && moderationWarnings[post.id] !== warning) {
    moderationWarnings[post.id] = warning
    return
  }
  const { data } = await createPlazaComment(post.id, sid.value, content)
  comments[post.id] = [...(comments[post.id] || []), data]
  commentDrafts[post.id] = ''
  moderationWarnings[post.id] = ''
  replacePost({ ...post, comment_count: post.comment_count + 1 })
  const commentsResp = await getPlazaComments(post.id)
  comments[post.id] = commentsResp.data
  await loadPosts()
}

const commentAuthorName = (comment: PlazaCommentItem | PlazaCommentReplyItem) =>
  comment.author_type === 'xiaoxi' ? '小曦' : comment.author.nickname

const replyAuthorName = (author: PlazaCommentItem['author']) =>
  author.session_id === 'xiaoxi' ? '小曦' : author.nickname

const beginReply = (postId: number, parentId: number, targetId: number, targetName: string) => {
  activeReplyTarget.value = { postId, parentId, targetId, targetName }
  replyDraft.value = ''
}

const isReplying = (postId: number, parentId: number) =>
  activeReplyTarget.value?.postId === postId && activeReplyTarget.value.parentId === parentId

const cancelReply = () => {
  activeReplyTarget.value = null
  replyDraft.value = ''
}

const loadAllReplies = async (comment: PlazaCommentItem) => {
  const { data } = await getPlazaCommentReplies(comment.id)
  comment.replies = data
}

const submitReply = async (post: PlazaPostItem, parentComment: PlazaCommentItem) => {
  const target = activeReplyTarget.value
  const content = replyDraft.value.trim()
  if (!target || !content) return
  const warning = moderateContent(content)
  if (warning && moderationWarnings[post.id] !== warning) {
    moderationWarnings[post.id] = warning
    return
  }

  await createPlazaCommentReply(target.targetId, sid.value, content)
  const { data } = await getPlazaCommentReplies(parentComment.id)
  parentComment.replies = data
  parentComment.reply_count = Math.max(parentComment.reply_count + 1, data.length)
  cancelReply()
  moderationWarnings[post.id] = ''
  replacePost({ ...post, comment_count: post.comment_count + 1 })
  await loadPosts()
}

const formatTime = (value?: string | null) => {
  if (!value) return ''
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
</script>

<style scoped>
.plaza-view {
  min-height: 100vh;
  padding: 26px 30px 42px;
}

.plaza-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.kodak-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.plaza-header h1 {
  margin: 8px 0 0;
  font-size: clamp(44px, 6vw, 72px);
  line-height: 0.9;
}

.plaza-header p {
  margin: 8px 0 0;
  max-width: 680px;
  color: var(--journal-muted);
  font-size: 14px;
}

.refresh-button {
  align-self: center;
  min-height: 42px;
  border-radius: 12px;
  padding: 0 16px;
  color: #fff8e8;
  font-weight: 700;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.plaza-header-actions {
  align-self: center;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.anonymous-toggle {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgb(62 50 40 / 16%);
  border-radius: 12px;
  padding: 0 12px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 70%);
  font-size: 12px;
  font-weight: 700;
}

.anonymous-toggle input {
  width: 16px;
  height: 16px;
}

.refresh-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.plaza-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  padding-top: 26px;
}

.plaza-feed {
  display: grid;
  gap: 18px;
}

.empty-plaza,
.plaza-post,
.side-note,
.side-rule,
.moderation-card {
  border: 1px solid rgb(62 50 40 / 16%);
  background: #fff8e8;
  box-shadow: 0 16px 34px rgb(62 50 40 / 14%);
}

.empty-plaza {
  padding: 42px;
  text-align: center;
}

.empty-plaza span {
  color: var(--journal-stamp);
  font-weight: 700;
}

.empty-plaza p {
  margin: 10px 0 0;
  color: var(--journal-muted);
}

.plaza-post {
  padding: 20px;
}

.post-author-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar,
.comment-avatar {
  display: grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  color: #fff8e8;
  background: linear-gradient(145deg, rgb(200 90 84 / 88%), rgb(62 50 40));
  font-weight: 700;
}

.author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 14px;
}

.author-avatar img,
.comment-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-copy strong,
.author-copy small {
  display: block;
}

.author-copy strong {
  color: var(--journal-ink);
  font-size: 15px;
}

.author-copy small {
  margin-top: 3px;
  color: var(--journal-muted);
  font-size: 12px;
}

.post-body {
  margin-top: 16px;
}

.post-body h2 {
  margin: 0 0 8px;
  color: var(--journal-ink);
  font-size: 20px;
}

.post-body p {
  margin: 0;
  color: var(--journal-ink);
  font-size: 14px;
  line-height: 1.75;
  white-space: pre-wrap;
}

.post-image-frame {
  margin-top: 14px;
  padding: 10px;
  background: #fdfbf7;
  border: 1px solid rgb(62 50 40 / 14%);
}

.post-image-frame img {
  display: block;
  width: 100%;
  max-height: 520px;
  object-fit: cover;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.post-tags span {
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 999px;
  background: rgb(253 251 247 / 72%);
  color: var(--journal-muted);
  padding: 0.28rem 0.62rem;
  font-size: 12px;
}

.post-tags .xiaoxi-like-tag {
  position: relative;
  overflow: hidden;
  color: #fff8e8;
  background: var(--journal-stamp);
  transform-origin: 50% 50%;
  animation: xiaoxiStampIn 0.56s cubic-bezier(0.22, 1.28, 0.36, 1) both;
}

.post-tags .xiaoxi-like-tag::after {
  content: "";
  position: absolute;
  inset: 3px;
  border: 1px solid rgb(255 248 232 / 52%);
  border-radius: inherit;
  opacity: 0.82;
  pointer-events: none;
}

.post-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed rgb(62 50 40 / 18%);
}

.post-actions button {
  position: relative;
  overflow: hidden;
  min-height: 38px;
  border-radius: 10px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 66%);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.post-actions button:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgb(62 50 40 / 10%);
}

.post-actions button:active {
  transform: translateY(0) scale(0.98);
}

.post-actions button.active {
  color: #fff8e8;
  background: var(--journal-stamp);
}

.post-actions button.action-pulse {
  animation: plazaActionPulse 0.38s ease-out;
}

.post-actions button.action-pulse::after {
  content: "";
  position: absolute;
  inset: 50%;
  border-radius: 999px;
  background: rgb(232 195 108 / 32%);
  animation: plazaActionRipple 0.42s ease-out;
}

.comments-panel {
  margin-top: 14px;
  padding: 14px;
  border: 1px dashed rgb(62 50 40 / 22%);
  background: rgb(253 251 247 / 56%);
}

.comment-list {
  display: grid;
  gap: 12px;
}

.empty-comments {
  margin: 0;
  color: var(--journal-muted);
  font-size: 13px;
}

.comment-item {
  display: flex;
  gap: 10px;
}

.comment-main,
.reply-main {
  min-width: 0;
  flex: 1;
}

.comment-avatar,
.reply-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  font-size: 13px;
}

.reply-avatar {
  display: grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  color: #fff8e8;
  background: linear-gradient(145deg, rgb(200 90 84 / 78%), rgb(62 50 40));
  font-size: 11px;
  font-weight: 700;
}

.reply-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.comment-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.comment-item strong,
.reply-item strong {
  color: var(--journal-stamp);
  font-size: 12px;
}

.comment-meta small {
  color: var(--journal-muted);
  font-size: 11px;
}

.comment-item p,
.reply-item p {
  margin: 4px 0 0;
  color: var(--journal-ink);
  font-size: 13px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.xiaoxi-comment {
  padding: 10px;
  border: 1px solid rgb(200 90 84 / 22%);
  background: rgb(255 248 232 / 72%);
}

.xiaoxi-comment strong::after {
  content: " · AI";
  color: var(--journal-muted);
  font-weight: 400;
}

.comment-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
}

.comment-tools button {
  min-height: 24px;
  padding: 0;
  border: 0;
  color: var(--journal-muted);
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.comment-tools button:hover {
  color: var(--journal-stamp);
}

.comment-tools.compact {
  margin-top: 4px;
}

.reply-thread {
  display: grid;
  gap: 10px;
  margin-top: 10px;
  padding: 10px 12px;
  border-left: 3px solid rgb(200 90 84 / 22%);
  background: rgb(255 248 232 / 54%);
}

.reply-item {
  display: flex;
  gap: 8px;
}

.xiaoxi-reply {
  padding: 8px;
  border: 1px solid rgb(200 90 84 / 18%);
  background: rgb(255 255 255 / 42%);
}

.reply-to {
  color: var(--journal-stamp);
  font-weight: 700;
}

.reply-composer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 8px;
  margin-top: 10px;
}

.comment-composer {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

.comment-composer input,
.reply-composer input {
  flex: 1;
  min-width: 0;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0 12px;
  outline: none;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 86%);
}

.reply-composer input {
  min-height: 34px;
}

.comment-composer button,
.reply-composer button {
  min-height: 38px;
  border-radius: 10px;
  padding: 0 14px;
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.reply-composer button {
  min-height: 34px;
  padding: 0 12px;
}

.reply-composer .ghost-button {
  color: var(--journal-muted);
  background: rgb(253 251 247 / 72%);
}

.comment-composer button:disabled,
.reply-composer button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
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

.plaza-side {
  position: sticky;
  top: 24px;
  display: grid;
  gap: 16px;
  height: fit-content;
}

.side-note,
.side-rule,
.moderation-card {
  padding: 18px;
}

.side-note span {
  color: var(--journal-stamp);
  font-size: 11px;
  font-weight: 700;
}

.side-note strong {
  display: block;
  margin-top: 4px;
  font-size: 42px;
  line-height: 1;
}

.side-note p,
.side-rule p {
  margin: 8px 0 0;
  color: var(--journal-muted);
  font-size: 13px;
  line-height: 1.6;
}

.side-rule h2 {
  margin: 0;
  font-size: 18px;
}

.moderation-card h2 {
  margin: 0;
  font-size: 18px;
}

.moderation-card ul {
  display: grid;
  gap: 8px;
  margin: 10px 0 0;
  padding-left: 18px;
  color: var(--journal-muted);
  font-size: 13px;
  line-height: 1.6;
}

@keyframes plazaActionPulse {
  0% {
    transform: scale(1);
  }
  45% {
    transform: scale(1.045);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes plazaActionRipple {
  from {
    inset: 50%;
    opacity: 0.65;
  }
  to {
    inset: -18%;
    opacity: 0;
  }
}

@keyframes xiaoxiStampIn {
  0% {
    opacity: 0;
    transform: scale(1.35) rotate(-10deg);
    filter: blur(2px);
  }
  70% {
    opacity: 1;
    transform: scale(0.96) rotate(-2deg);
    filter: blur(0);
  }
  100% {
    transform: scale(1) rotate(0);
  }
}

@media (max-width: 980px) {
  .plaza-view {
    padding: 16px 14px 26px;
  }

  .plaza-layout {
    display: block;
  }

  .plaza-side {
    position: relative;
    top: auto;
    margin-top: 18px;
  }
}

@media (max-width: 680px) {
  .plaza-header {
    display: block;
    padding: 20px;
  }

  .refresh-button {
    margin-top: 14px;
  }

  .plaza-header-actions {
    justify-content: flex-start;
    margin-top: 14px;
  }

  .post-actions {
    grid-template-columns: 1fr;
  }

  .reply-composer {
    grid-template-columns: 1fr;
  }
}
</style>

