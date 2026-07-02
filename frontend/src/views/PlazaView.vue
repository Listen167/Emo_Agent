<template>
  <div class="plaza-view">
    <header v-develop class="plaza-header">
      <div class="plaza-header-copy">
        <span class="kodak-chip">Public Contact Sheet</span>
        <h1 class="script-title">聊天广场</h1>
        <p>这里收集大家公开发布的生活胶片。点赞、评论，给彼此留下一点回声。</p>
        <div class="plaza-header-actions">
          <label class="anonymous-toggle">
            <input v-model="anonymousMode" type="checkbox" @change="saveAnonymousMode" />
            <span>匿名互动</span>
          </label>
          <button
            :class="['filter-button', { active: showMyInteractionsOnly }]"
            :disabled="interactionScanning"
            @click="toggleMyInteractionsFilter"
          >
            {{ interactionScanning ? '筛选中...' : showMyInteractionsOnly ? '查看全部' : '只看我的互动' }}
          </button>
          <button
            :class="['silent-notice-button', { active: totalUnreadComments > 0 }]"
            :disabled="totalUnreadComments === 0"
            @click="markAllCommentsRead"
          >
            静默消息
            <span v-if="totalUnreadComments > 0">{{ totalUnreadComments }}</span>
          </button>
          <button
            :class="['compose-toggle-button', { active: composerOpen }]"
            type="button"
            @click="toggleComposer"
          >
            {{ composerOpen ? '收起发布' : '发布动态' }}
          </button>
          <button class="refresh-button" :disabled="loading" @click="loadPosts">
            {{ loading ? '刷新中...' : '刷新广场' }}
          </button>
        </div>
      </div>
      <div class="plaza-wall-props" aria-hidden="true">
        <span class="notice-pin pin-left"></span>
        <span class="notice-pin pin-right"></span>
        <div class="polaroid-wall">
          <span class="polaroid-card card-one"></span>
          <span class="polaroid-card card-two"></span>
          <span class="polaroid-card card-three"></span>
        </div>
        <div class="xiaoxi-patrol-sticker">
          <img src="/xiaoxi/happy.png" alt="" />
          <span>XIAO XI PASS</span>
        </div>
      </div>
    </header>

    <Transition name="composer-drop">
      <div v-if="composerOpen" v-develop="80">
        <RecordComposer
          :session-id="sid"
          variant="plaza"
          default-visibility="public"
          title="发布一条校园动态"
          eyebrow="STUDENT MOMENT"
          title-placeholder="标题，例如：晚自习后的操场"
          content-placeholder="写下学习、生活或情绪里的一个片段..."
          location-placeholder="地点，例如：图书馆 / 宿舍"
          tags-placeholder="校园标签，用逗号分隔，例如：备考压力,宿舍生活,自我鼓励"
          attachment-placeholder="添加图片 / 成长记忆"
          empty-content="分享了一张校园成长记忆"
          private-hint="私密动态只保存到个人资料里的成长记录。"
          public-hint="公开动态会进入聊天广场。"
          private-submit-label="保存私密记录"
          public-submit-label="发布到广场"
          saving-label="发布中..."
          moderate-public
          @created="handlePostCreated"
        />
        <p v-if="composerNotice" class="composer-notice">{{ composerNotice }}</p>
      </div>
    </Transition>

    <main class="plaza-layout">
      <section class="plaza-feed">
        <div v-if="visiblePosts.length === 0 && !loading" class="empty-plaza">
          <span>{{ showMyInteractionsOnly ? 'NO MATCHED ROLL' : 'NO PUBLIC ROLL' }}</span>
          <p>
            {{ showMyInteractionsOnly
              ? '还没有找到你互动过的公开胶片。'
              : '还没有公开动态。可以在这里发布第一条校园动态。' }}
          </p>
          <button v-if="!showMyInteractionsOnly" class="empty-compose-button" type="button" @click="openComposer">
            发布动态
          </button>
        </div>

        <article v-for="post in visiblePosts" :key="post.id" v-develop="90" class="plaza-post">
          <header class="post-author-row">
            <button
              class="author-avatar avatar-zoom-trigger"
              type="button"
              :aria-label="`查看 ${post.author.nickname} 的头像`"
              @click="openAvatarPreview(post.author)"
            >
              <img v-if="post.author.avatar_url" :src="authorAvatarUrl(post.author.avatar_url)" alt="用户头像" />
              <span v-else>{{ post.author.nickname.slice(0, 1) }}</span>
            </button>
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
              <button
                class="post-image-zoom"
                type="button"
                aria-label="放大查看生活记录图片"
                @click="openMediaPreview(post)"
              >
                <img :src="resolveAssetUrl(post.media_url)" alt="生活记录图片" />
              </button>
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
              :class="{
                active: openCommentPostId === post.id,
                'action-pulse': reactionKey === `${post.id}-comment`,
                'has-unread-comments': unreadCommentCount(post) > 0,
              }"
              @click="toggleComments(post)"
            >
              评论 · {{ post.comment_count }}
              <span v-if="unreadCommentCount(post) > 0" class="comment-unread-badge">
                +{{ unreadCommentCount(post) }}
              </span>
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
              <p v-if="visibleComments(post.id).length === 0" class="empty-comments">还没有评论。</p>
              <article
                v-for="comment in visibleComments(post.id)"
                :key="comment.id"
                :class="['comment-item', { 'xiaoxi-comment': comment.author_type === 'xiaoxi' }]"
              >
                <button
                  class="comment-avatar avatar-zoom-trigger"
                  type="button"
                  :aria-label="`查看 ${commentAuthorName(comment)} 的头像`"
                  @click="openAvatarPreview(comment.author)"
                >
                  <img v-if="comment.author.avatar_url" :src="authorAvatarUrl(comment.author.avatar_url)" alt="评论者头像" />
                  <span v-else>{{ comment.author.nickname.slice(0, 1) }}</span>
                </button>
                <div class="comment-main">
                  <div class="comment-meta">
                    <strong>{{ commentAuthorName(comment) }}</strong>
                    <small>{{ formatTime(comment.created_at) }}</small>
                  </div>
                  <p>{{ comment.content }}</p>
                  <div class="comment-tools">
                    <button
                      :class="{ active: isCommentLiked(comment), 'tool-pulse': reactionKey === `comment-${comment.id}-like` }"
                      @click="toggleCommentLike(post, comment)"
                    >
                      {{ isCommentLiked(comment) ? '已喜欢' : '喜欢' }} · {{ commentLikeCount(comment) }}
                    </button>
                    <button @click="beginReply(post.id, comment.id, comment.id, commentAuthorName(comment))">回复</button>
                    <button
                      v-if="isMine(comment)"
                      class="danger-tool"
                      @click="hideComment(post, comment)"
                    >
                      撤回
                    </button>
                    <button
                      v-if="comment.reply_count > comment.replies.length"
                      @click="loadAllReplies(comment)"
                    >
                      展开全部 {{ comment.reply_count }} 条回复
                    </button>
                  </div>

                  <div v-if="comment.replies.length" class="reply-thread">
                    <article
                      v-for="reply in visibleReplies(comment)"
                      :key="reply.id"
                      :class="['reply-item', { 'xiaoxi-reply': reply.author_type === 'xiaoxi' }]"
                    >
                      <button
                        class="reply-avatar avatar-zoom-trigger"
                        type="button"
                        :aria-label="`查看 ${commentAuthorName(reply)} 的头像`"
                        @click="openAvatarPreview(reply.author)"
                      >
                        <img v-if="reply.author.avatar_url" :src="authorAvatarUrl(reply.author.avatar_url)" alt="回复者头像" />
                        <span v-else>{{ reply.author.nickname.slice(0, 1) }}</span>
                      </button>
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
                          <button
                            :class="{ active: isReplyLiked(reply), 'tool-pulse': reactionKey === `reply-${reply.id}-like` }"
                            @click="toggleReplyLike(post, reply)"
                          >
                            {{ isReplyLiked(reply) ? '已喜欢' : '喜欢' }} · {{ replyLikeCount(reply) }}
                          </button>
                          <button @click="beginReply(post.id, comment.id, reply.id, commentAuthorName(reply))">回复</button>
                          <button
                            v-if="isMine(reply)"
                            class="danger-tool"
                            @click="hideReply(post, comment, reply)"
                          >
                            撤回
                          </button>
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
                    <button class="xiaoxi-suggest-button" @click="suggestReply(post)">小曦来一句</button>
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
              <button class="xiaoxi-suggest-button" @click="suggestComment(post)">小曦来一句</button>
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
          <strong>{{ visiblePosts.length }}</strong>
          <p>{{ showMyInteractionsOnly ? '我的互动' : '公开胶片' }}</p>
        </section>
        <section v-develop="160" class="side-rule">
          <h2>广场规则</h2>
          <p>发布时选择公开会进入广场；选择私密会沉淀到个人资料的成长记录。图片内容作为成长记忆保存。</p>
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

    <Transition name="avatar-preview">
      <div
        v-if="avatarPreview"
        class="avatar-preview-backdrop"
        @click.self="closeAvatarPreview"
      >
        <section class="avatar-preview-card" role="dialog" aria-modal="true" aria-label="头像预览">
          <button class="avatar-preview-close" type="button" @click="closeAvatarPreview">关闭</button>
          <div class="avatar-preview-image">
            <img v-if="avatarPreview.avatarUrl" :src="avatarPreview.avatarUrl" :alt="`${avatarPreview.name} 的头像`" />
            <span v-else>{{ avatarPreview.initial }}</span>
          </div>
          <strong>{{ avatarPreview.name }}</strong>
          <small v-if="avatarPreview.ebti">{{ avatarPreview.ebti }}</small>
        </section>
      </div>
    </Transition>

    <Transition name="media-preview">
      <div
        v-if="mediaPreview"
        class="media-preview-backdrop"
        @click.self="closeMediaPreview"
      >
        <section class="media-preview-card" role="dialog" aria-modal="true" aria-label="图片预览">
          <button class="media-preview-close" type="button" @click="closeMediaPreview">关闭</button>
          <img :src="mediaPreview.url" :alt="mediaPreview.title" />
          <footer>
            <strong>{{ mediaPreview.title }}</strong>
            <small>{{ mediaPreview.meta }}</small>
          </footer>
        </section>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import {
  createPlazaCommentReply,
  createPlazaComment,
  getPlazaCommentReplies,
  getPlazaComments,
  getPlazaPosts,
  likePlazaPost,
  repostPlazaPost,
  unlikePlazaPost,
  type PlazaAuthor,
  type PlazaCommentItem,
  type PlazaCommentReplyItem,
  type PlazaPostItem,
} from '../api/plaza'
import RecordComposer from '../components/RecordComposer.vue'
import type { LifeRecordItem } from '../api/life'
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
const composerOpen = ref(false)
const composerNotice = ref('')
const anonymousMode = ref(localStorage.getItem('u-life-plaza-anonymous-v1') === 'true')
const moderationWarnings = reactive<Record<number, string>>({})
const reactionKey = ref('')
const hiddenCommentIds = ref<Set<number>>(new Set())
const hiddenReplyIds = ref<Set<number>>(new Set())
const likedCommentIds = ref<Set<number>>(new Set())
const likedReplyIds = ref<Set<number>>(new Set())
const myInteractionPostIds = ref<Set<number>>(new Set())
const readCommentCounts = ref<Record<number, number>>({})
const showMyInteractionsOnly = ref(false)
const interactionScanning = ref(false)
const avatarPreview = ref<{
  name: string
  initial: string
  avatarUrl: string
  ebti: string
} | null>(null)
const mediaPreview = ref<{
  url: string
  title: string
  meta: string
} | null>(null)
let reactionTimer: number | undefined
const HIDDEN_COMMENTS_KEY = 'u-life-plaza-hidden-comments-v1'
const HIDDEN_REPLIES_KEY = 'u-life-plaza-hidden-replies-v1'
const COMMENT_LIKES_KEY = 'u-life-plaza-comment-likes-v1'
const REPLY_LIKES_KEY = 'u-life-plaza-reply-likes-v1'
const MY_INTERACTIONS_KEY = 'u-life-plaza-my-interactions-v1'
const READ_COMMENT_COUNTS_KEY = 'u-life-plaza-read-comment-counts-v1'

onMounted(() => {
  localStorage.setItem('sid', sid.value)
  hiddenCommentIds.value = loadHiddenIds(HIDDEN_COMMENTS_KEY)
  hiddenReplyIds.value = loadHiddenIds(HIDDEN_REPLIES_KEY)
  likedCommentIds.value = loadHiddenIds(COMMENT_LIKES_KEY)
  likedReplyIds.value = loadHiddenIds(REPLY_LIKES_KEY)
  myInteractionPostIds.value = loadHiddenIds(MY_INTERACTIONS_KEY)
  readCommentCounts.value = loadReadCommentCounts()
  void loadPosts()
  window.addEventListener('keydown', handlePreviewKeydown)
})

onBeforeUnmount(() => {
  if (reactionTimer) window.clearTimeout(reactionTimer)
  window.removeEventListener('keydown', handlePreviewKeydown)
})

const loadHiddenIds = (key: string) => {
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || '[]')
    return new Set<number>(Array.isArray(parsed) ? parsed.filter(id => Number.isFinite(id)) : [])
  } catch {
    return new Set<number>()
  }
}

const saveHiddenIds = (key: string, ids: Set<number>) => {
  localStorage.setItem(key, JSON.stringify([...ids]))
}

const loadReadCommentCounts = () => {
  try {
    const parsed = JSON.parse(localStorage.getItem(READ_COMMENT_COUNTS_KEY) || '{}')
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {}
    return Object.fromEntries(
      Object.entries(parsed)
        .map(([key, value]) => [Number(key), Number(value)])
        .filter(([key, value]) => Number.isFinite(key) && Number.isFinite(value) && value >= 0)
    ) as Record<number, number>
  } catch {
    return {}
  }
}

const saveReadCommentCounts = () => {
  localStorage.setItem(READ_COMMENT_COUNTS_KEY, JSON.stringify(readCommentCounts.value))
}

const visiblePosts = computed(() =>
  showMyInteractionsOnly.value
    ? posts.value.filter(post => hasMyInteraction(post))
    : posts.value
)
const totalUnreadComments = computed(() =>
  posts.value.reduce((total, post) => total + unreadCommentCount(post), 0)
)

const loadPosts = async () => {
  loading.value = true
  try {
    const { data } = await getPlazaPosts(sid.value)
    posts.value = data
    ensureCommentReadBaselines(data)
  } finally {
    loading.value = false
  }
}

const replacePost = (next: PlazaPostItem) => {
  const index = posts.value.findIndex(post => post.id === next.id)
  if (index >= 0) posts.value[index] = { ...posts.value[index], ...next }
}

const unreadCommentCount = (post: PlazaPostItem) =>
  Math.max(0, post.comment_count - (readCommentCounts.value[post.id] ?? post.comment_count))

const markPostCommentsRead = (post: PlazaPostItem) => {
  readCommentCounts.value = {
    ...readCommentCounts.value,
    [post.id]: post.comment_count,
  }
  saveReadCommentCounts()
}

const ensureCommentReadBaselines = (nextPosts: PlazaPostItem[]) => {
  const missingEntries = nextPosts
    .filter(post => readCommentCounts.value[post.id] === undefined)
    .map(post => [post.id, post.comment_count])
  if (missingEntries.length === 0) return
  readCommentCounts.value = {
    ...readCommentCounts.value,
    ...Object.fromEntries(missingEntries),
  }
  saveReadCommentCounts()
}

const markAllCommentsRead = () => {
  readCommentCounts.value = Object.fromEntries(
    posts.value.map(post => [post.id, post.comment_count])
  )
  saveReadCommentCounts()
}

const saveAnonymousMode = () => {
  localStorage.setItem('u-life-plaza-anonymous-v1', String(anonymousMode.value))
  window.dispatchEvent(new CustomEvent('u-life-settings-changed'))
}

const toggleComposer = () => {
  composerOpen.value = !composerOpen.value
  composerNotice.value = ''
}

const openComposer = () => {
  composerOpen.value = true
  composerNotice.value = ''
}

const handlePostCreated = async (record: LifeRecordItem) => {
  composerOpen.value = true
  composerNotice.value = record.visibility === 'public'
    ? '已发布到聊天广场。'
    : '已保存为私密成长记录，可在个人资料中查看。'
  if (record.visibility === 'public') await loadPosts()
}

const authorAvatarUrl = (url: string) => {
  if (url.startsWith('/xiaoxi/')) return url
  return resolveAssetUrl(url)
}

const isMine = (item: PlazaCommentItem | PlazaCommentReplyItem) =>
  item.author_type !== 'xiaoxi' && item.author.session_id === sid.value

const markPostInteraction = (postId: number) => {
  if (myInteractionPostIds.value.has(postId)) return
  myInteractionPostIds.value = new Set([...myInteractionPostIds.value, postId])
  saveHiddenIds(MY_INTERACTIONS_KEY, myInteractionPostIds.value)
}

const hasLoadedCommentInteraction = (postId: number) =>
  (comments[postId] || []).some(comment =>
    isMine(comment) ||
    likedCommentIds.value.has(comment.id) ||
    comment.replies.some(reply => isMine(reply) || likedReplyIds.value.has(reply.id))
  )

const hasMyInteraction = (post: PlazaPostItem) =>
  post.author.session_id === sid.value ||
  post.liked ||
  post.reposted ||
  myInteractionPostIds.value.has(post.id) ||
  hasLoadedCommentInteraction(post.id)

const scanMyInteractions = async () => {
  interactionScanning.value = true
  try {
    for (const post of posts.value) {
      if (!comments[post.id]) {
        try {
          const { data } = await getPlazaComments(post.id)
          comments[post.id] = data
        } catch {
          comments[post.id] = []
        }
      }
      if (hasLoadedCommentInteraction(post.id) || post.liked || post.reposted) {
        markPostInteraction(post.id)
      }
    }
  } finally {
    interactionScanning.value = false
  }
}

const toggleMyInteractionsFilter = async () => {
  showMyInteractionsOnly.value = !showMyInteractionsOnly.value
  if (showMyInteractionsOnly.value) {
    await scanMyInteractions()
  }
}

const visibleComments = (postId: number) =>
  (comments[postId] || []).filter(comment => !hiddenCommentIds.value.has(comment.id))

const visibleReplies = (comment: PlazaCommentItem) =>
  comment.replies.filter(reply => !hiddenReplyIds.value.has(reply.id))

const hideComment = (post: PlazaPostItem, comment: PlazaCommentItem) => {
  if (!isMine(comment)) return
  hiddenCommentIds.value = new Set([...hiddenCommentIds.value, comment.id])
  saveHiddenIds(HIDDEN_COMMENTS_KEY, hiddenCommentIds.value)
  replacePost({ ...post, comment_count: Math.max(0, post.comment_count - 1 - comment.reply_count) })
  if (activeReplyTarget.value?.parentId === comment.id) cancelReply()
}

const hideReply = (post: PlazaPostItem, comment: PlazaCommentItem, reply: PlazaCommentReplyItem) => {
  if (!isMine(reply)) return
  hiddenReplyIds.value = new Set([...hiddenReplyIds.value, reply.id])
  saveHiddenIds(HIDDEN_REPLIES_KEY, hiddenReplyIds.value)
  comment.reply_count = Math.max(0, comment.reply_count - 1)
  replacePost({ ...post, comment_count: Math.max(0, post.comment_count - 1) })
}

const openAvatarPreview = (author: PlazaAuthor) => {
  const name = author.session_id === 'xiaoxi' ? '小曦' : author.nickname
  avatarPreview.value = {
    name,
    initial: name.slice(0, 1),
    avatarUrl: author.avatar_url ? authorAvatarUrl(author.avatar_url) : '',
    ebti: author.ebti_type ? `${author.ebti_type} ${author.ebti_name || ''}`.trim() : '',
  }
}

const closeAvatarPreview = () => {
  avatarPreview.value = null
}

const handlePreviewKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeAvatarPreview()
    closeMediaPreview()
  }
}

const toggleLike = async (post: PlazaPostItem) => {
  pulseAction(post.id, 'like')
  const { data } = post.liked
    ? await unlikePlazaPost(post.id, sid.value)
    : await likePlazaPost(post.id, sid.value)
  if (!post.liked) markPostInteraction(post.id)
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
  markPostInteraction(post.id)
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
  markPostCommentsRead(post)
}

const pulseAction = (postId: number, action: 'like' | 'comment' | 'repost') => {
  pulseReaction(`${postId}-${action}`)
}

const pulseReaction = (key: string) => {
  reactionKey.value = key
  if (reactionTimer) window.clearTimeout(reactionTimer)
  reactionTimer = window.setTimeout(() => {
    reactionKey.value = ''
  }, 420)
}

const isCommentLiked = (comment: PlazaCommentItem) => likedCommentIds.value.has(comment.id)

const isReplyLiked = (reply: PlazaCommentReplyItem) => likedReplyIds.value.has(reply.id)

const commentLikeCount = (comment: PlazaCommentItem) =>
  comment.like_count + (isCommentLiked(comment) ? 1 : 0)

const replyLikeCount = (reply: PlazaCommentReplyItem) =>
  reply.like_count + (isReplyLiked(reply) ? 1 : 0)

const toggleCommentLike = (post: PlazaPostItem, comment: PlazaCommentItem) => {
  const next = new Set(likedCommentIds.value)
  if (next.has(comment.id)) {
    next.delete(comment.id)
  } else {
    next.add(comment.id)
    markPostInteraction(post.id)
  }
  likedCommentIds.value = next
  saveHiddenIds(COMMENT_LIKES_KEY, next)
  pulseReaction(`comment-${comment.id}-like`)
}

const toggleReplyLike = (post: PlazaPostItem, reply: PlazaCommentReplyItem) => {
  const next = new Set(likedReplyIds.value)
  if (next.has(reply.id)) {
    next.delete(reply.id)
  } else {
    next.add(reply.id)
    markPostInteraction(post.id)
  }
  likedReplyIds.value = next
  saveHiddenIds(REPLY_LIKES_KEY, next)
  pulseReaction(`reply-${reply.id}-like`)
}

const openMediaPreview = (post: PlazaPostItem) => {
  if (!post.media_url) return
  mediaPreview.value = {
    url: resolveAssetUrl(post.media_url),
    title: post.title || '生活记录图片',
    meta: `${post.author.nickname} · ${formatTime(post.published_at || post.created_at)}`,
  }
}

const closeMediaPreview = () => {
  mediaPreview.value = null
}

const suggestionMoodText = (post: PlazaPostItem) =>
  post.mood_label ? moodText(post.mood_label) : '这一刻'

const pickSuggestion = (post: PlazaPostItem, targetName?: string) => {
  const target = targetName && targetName !== '小曦' ? `${targetName}，` : ''
  const options = [
    `${target}这条记录很有画面感，愿这份${suggestionMoodText(post)}被好好接住。`,
    `${target}我读到这里觉得很温柔，也想听你继续说说这一帧后面的故事。`,
    `${target}小曦来盖章：这段分享值得被认真保存。`,
    `${target}谢谢你把这一刻放到广场里，它让今天多了一点回声。`,
  ]
  return options[(post.id + (targetName?.length || 0)) % options.length]
}

const suggestComment = (post: PlazaPostItem) => {
  commentDrafts[post.id] = pickSuggestion(post)
}

const suggestReply = (post: PlazaPostItem) => {
  replyDraft.value = pickSuggestion(post, activeReplyTarget.value?.targetName)
}

const moderateContent = (content: string) => {
  const riskyWords = ['傻逼', '垃圾', '去死', '人肉', '手机号', '身份证', '住址']
  const matched = riskyWords.find(word => content.includes(word))
  if (!matched) return ''
  if (['手机号', '身份证', '住址'].includes(matched)) return '这条内容可能包含隐私信息，请确认后再公开发送。'
  return '这条内容可能不符合温和社区规则，请换一种更尊重的表达。'
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
  markPostInteraction(post.id)
  comments[post.id] = [...(comments[post.id] || []), data]
  commentDrafts[post.id] = ''
  moderationWarnings[post.id] = ''
  replacePost({ ...post, comment_count: post.comment_count + 1 })
  const commentsResp = await getPlazaComments(post.id)
  comments[post.id] = commentsResp.data
  markPostCommentsRead({ ...post, comment_count: post.comment_count + 1 })
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
  markPostInteraction(post.id)
  const { data } = await getPlazaCommentReplies(parentComment.id)
  parentComment.replies = data
  parentComment.reply_count = Math.max(parentComment.reply_count + 1, data.length)
  cancelReply()
  moderationWarnings[post.id] = ''
  replacePost({ ...post, comment_count: post.comment_count + 1 })
  markPostCommentsRead({ ...post, comment_count: post.comment_count + 1 })
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
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.plaza-header-copy {
  flex: 1;
  min-width: 0;
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

.refresh-button,
.filter-button,
.silent-notice-button,
.compose-toggle-button,
.empty-compose-button,
.publish-button {
  align-self: center;
  min-height: 42px;
  border-radius: 12px;
  padding: 0 16px;
  color: #fff8e8;
  font-weight: 700;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  cursor: pointer;
}

.filter-button,
.silent-notice-button,
.compose-toggle-button,
.empty-compose-button {
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 72%);
}

.filter-button.active,
.silent-notice-button.active,
.compose-toggle-button.active {
  color: #fff8e8;
  background: var(--journal-stamp);
  box-shadow: 0 10px 22px rgb(200 90 84 / 18%);
}

.silent-notice-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.silent-notice-button span {
  min-width: 20px;
  height: 20px;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  color: var(--journal-stamp);
  background: #fff8e8;
  font-size: 11px;
  font-weight: 900;
  animation: silentNoticePulse 2.2s ease-in-out infinite;
}

.silent-notice-button.active::after {
  content: "";
  position: absolute;
  top: 7px;
  right: 8px;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #fff8e8;
  box-shadow: 0 0 0 4px rgb(255 248 232 / 20%);
  animation: silentNoticePulse 2.2s ease-in-out infinite;
}

.plaza-header-actions {
  width: fit-content;
  margin-top: 14px;
  padding: 7px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  border: 1px solid rgb(62 50 40 / 12%);
  border-radius: 14px;
  background: rgb(253 251 247 / 54%);
  box-shadow: inset 0 1px 1px rgb(255 255 255 / 62%);
}

.plaza-wall-props {
  position: relative;
  flex: 0 0 244px;
  width: 244px;
  height: 134px;
}

.notice-pin {
  position: absolute;
  z-index: 5;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: radial-gradient(circle at 35% 28%, #fff8e8 0 18%, var(--journal-stamp) 19% 100%);
  box-shadow: 0 6px 10px rgb(62 50 40 / 16%);
}

.pin-left {
  left: 28px;
  top: 15px;
}

.pin-right {
  right: 48px;
  top: 8px;
}

.polaroid-wall {
  position: absolute;
  left: 4px;
  right: 10px;
  top: 16px;
  bottom: 14px;
  border: 1px dashed rgb(62 50 40 / 16%);
  border-radius: 18px;
  background: rgb(253 251 247 / 34%);
}

.polaroid-card {
  position: absolute;
  width: 70px;
  height: 82px;
  padding: 7px 7px 18px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: #fdfbf7;
  box-shadow: 0 12px 20px rgb(62 50 40 / 12%);
  transform-origin: 50% 10%;
  animation: plazaPhotoSway 4.8s ease-in-out infinite;
}

.polaroid-card::after {
  content: "";
  display: block;
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, rgb(232 195 108 / 82%), rgb(200 90 84 / 52%));
}

.card-one {
  left: 16px;
  top: 24px;
  rotate: -7deg;
}

.card-two {
  left: 82px;
  top: 12px;
  rotate: 4deg;
  animation-delay: 0.35s;
}

.card-two::after {
  background: linear-gradient(145deg, rgb(58 82 78 / 72%), rgb(255 248 232 / 84%));
}

.card-three {
  right: 14px;
  top: 28px;
  rotate: -2deg;
  animation-delay: 0.7s;
}

.card-three::after {
  background: linear-gradient(145deg, rgb(154 122 168 / 70%), rgb(232 195 108 / 62%));
}

.xiaoxi-patrol-sticker {
  position: absolute;
  right: 4px;
  bottom: -2px;
  z-index: 6;
  display: grid;
  justify-items: center;
  width: 78px;
  padding: 6px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 14px;
  background: rgb(255 248 232 / 94%);
  box-shadow: 0 12px 22px rgb(62 50 40 / 14%);
  rotate: 5deg;
}

.xiaoxi-patrol-sticker img {
  width: 54px;
  height: 54px;
  object-fit: contain;
  filter: drop-shadow(0 5px 8px rgb(62 50 40 / 14%));
  animation: plazaStickerFloat 3.3s ease-in-out infinite;
}

.xiaoxi-patrol-sticker span {
  margin-top: -3px;
  color: var(--journal-stamp);
  font-size: 9px;
  font-weight: 900;
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

.filter-button:disabled,
.silent-notice-button:disabled,
.publish-button:disabled {
  opacity: 0.55;
  cursor: default;
}

.composer-drop-enter-active,
.composer-drop-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.composer-drop-enter-from,
.composer-drop-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.composer-notice {
  margin: 12px 0 0;
  color: var(--journal-stamp);
  font-size: 13px;
  font-weight: 700;
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

.empty-compose-button {
  margin-top: 16px;
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
  border: 0;
  padding: 0;
  display: grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  color: #fff8e8;
  background: linear-gradient(145deg, rgb(200 90 84 / 88%), rgb(62 50 40));
  font-weight: 700;
}

.avatar-zoom-trigger {
  position: relative;
  cursor: zoom-in;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    filter 0.18s ease;
}

.avatar-zoom-trigger:hover {
  transform: translateY(-1px) scale(1.04);
  filter: saturate(1.08);
  box-shadow: 0 8px 16px rgb(62 50 40 / 16%);
}

.avatar-zoom-trigger:focus-visible {
  outline: 3px solid rgb(200 90 84 / 32%);
  outline-offset: 3px;
}

.author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 14px;
}

.author-avatar img,
.comment-avatar img,
.reply-avatar img {
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

.post-image-zoom {
  position: relative;
  overflow: hidden;
  display: block;
  width: 100%;
  padding: 0;
  background: transparent;
  cursor: zoom-in;
}

.post-image-zoom::after {
  content: "点击放大";
  position: absolute;
  right: 10px;
  bottom: 10px;
  padding: 5px 9px;
  border-radius: 999px;
  color: #fff8e8;
  background: rgb(62 50 40 / 68%);
  font-size: 11px;
  font-weight: 700;
  opacity: 0;
  transform: translateY(4px);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.post-image-zoom:hover::after {
  opacity: 1;
  transform: translateY(0);
}

.post-image-zoom img {
  display: block;
  width: 100%;
  max-height: 520px;
  object-fit: cover;
  transition: transform 0.24s ease, filter 0.24s ease;
}

.post-image-zoom:hover img {
  transform: scale(1.015);
  filter: saturate(1.06);
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

.post-actions button.has-unread-comments {
  color: var(--journal-stamp);
  background: rgb(255 248 232 / 86%);
  box-shadow: inset 0 0 0 1px rgb(200 90 84 / 18%);
}

.post-actions button.has-unread-comments::before {
  content: "";
  position: absolute;
  top: 7px;
  right: 9px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #c85a54;
  box-shadow: 0 0 0 4px rgb(200 90 84 / 13%);
  animation: silentNoticePulse 2.2s ease-in-out infinite;
}

.comment-unread-badge {
  margin-left: 6px;
  padding: 2px 6px;
  border-radius: 999px;
  color: #fff8e8;
  background: var(--journal-stamp);
  font-size: 10px;
  font-weight: 900;
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
  border: 0;
  padding: 0;
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

.comment-tools button.active {
  color: var(--journal-stamp);
}

.comment-tools button.tool-pulse {
  animation: plazaActionPulse 0.38s ease-out;
}

.comment-tools .danger-tool {
  color: #b84742;
}

.comment-tools .danger-tool:hover {
  color: #8f2f2b;
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
  grid-template-columns: minmax(0, 1fr) auto auto auto;
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

.comment-composer .xiaoxi-suggest-button,
.reply-composer .xiaoxi-suggest-button {
  color: var(--journal-ink);
  background: var(--journal-kodak);
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

.avatar-preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgb(31 22 17 / 54%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.avatar-preview-card {
  position: relative;
  width: min(360px, 92vw);
  padding: 30px 24px 24px;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 18px;
  text-align: center;
  background:
    linear-gradient(180deg, rgb(255 248 232), rgb(242 218 154 / 92%));
  box-shadow: 0 26px 70px rgb(15 10 8 / 34%);
}

.avatar-preview-close {
  position: absolute;
  top: 12px;
  right: 12px;
  min-height: 32px;
  border-radius: 999px;
  padding: 0 12px;
  color: var(--journal-muted);
  background: rgb(253 251 247 / 78%);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.avatar-preview-image {
  display: grid;
  place-items: center;
  overflow: hidden;
  width: 190px;
  height: 190px;
  margin: 6px auto 18px;
  border: 10px solid #fdfbf7;
  border-radius: 34px;
  color: #fff8e8;
  background: linear-gradient(145deg, rgb(200 90 84 / 92%), rgb(62 50 40));
  box-shadow: 0 18px 34px rgb(62 50 40 / 22%);
  font-size: 64px;
  font-weight: 900;
}

.avatar-preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-preview-card strong,
.avatar-preview-card small {
  display: block;
}

.avatar-preview-card strong {
  color: var(--journal-ink);
  font-size: 20px;
}

.avatar-preview-card small {
  margin-top: 6px;
  color: var(--journal-stamp);
  font-size: 13px;
  font-weight: 700;
}

.avatar-preview-enter-active,
.avatar-preview-leave-active {
  transition: opacity 0.22s ease;
}

.avatar-preview-enter-active .avatar-preview-card,
.avatar-preview-leave-active .avatar-preview-card {
  transition:
    transform 0.24s cubic-bezier(0.2, 0.9, 0.2, 1),
    filter 0.24s ease;
}

.avatar-preview-enter-from,
.avatar-preview-leave-to {
  opacity: 0;
}

.avatar-preview-enter-from .avatar-preview-card,
.avatar-preview-leave-to .avatar-preview-card {
  transform: translateY(14px) scale(0.94) rotate(-1.5deg);
  filter: blur(5px);
}

.media-preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 82;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgb(31 22 17 / 64%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.media-preview-card {
  position: relative;
  width: min(880px, 94vw);
  max-height: 92vh;
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgb(255 248 232 / 34%);
  background: #fdfbf7;
  box-shadow: 0 30px 86px rgb(15 10 8 / 42%);
}

.media-preview-card > img {
  display: block;
  width: 100%;
  max-height: min(72vh, 720px);
  object-fit: contain;
  background: #1f1611;
}

.media-preview-close {
  position: absolute;
  top: 16px;
  right: 16px;
  min-height: 32px;
  border-radius: 999px;
  padding: 0 12px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 86%);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.media-preview-card footer {
  display: grid;
  gap: 4px;
}

.media-preview-card strong {
  color: var(--journal-ink);
  font-size: 15px;
}

.media-preview-card small {
  color: var(--journal-muted);
  font-size: 12px;
}

.media-preview-enter-active,
.media-preview-leave-active {
  transition: opacity 0.22s ease;
}

.media-preview-enter-active .media-preview-card,
.media-preview-leave-active .media-preview-card {
  transition:
    transform 0.24s cubic-bezier(0.2, 0.9, 0.2, 1),
    filter 0.24s ease;
}

.media-preview-enter-from,
.media-preview-leave-to {
  opacity: 0;
}

.media-preview-enter-from .media-preview-card,
.media-preview-leave-to .media-preview-card {
  transform: translateY(14px) scale(0.96);
  filter: blur(5px);
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

@keyframes silentNoticePulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.18);
    opacity: 0.72;
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

@keyframes plazaPhotoSway {
  0%,
  100% {
    transform: rotate(-1deg);
  }
  50% {
    transform: rotate(1.6deg);
  }
}

@keyframes plazaStickerFloat {
  0%,
  100% {
    transform: translateY(0) rotate(-1deg);
  }
  50% {
    transform: translateY(-3px) rotate(2deg);
  }
}

@media (max-width: 980px) {
  .plaza-view {
    padding: 16px 14px 26px;
  }

  .plaza-header {
    align-items: flex-start;
  }

  .plaza-wall-props {
    flex-basis: 190px;
    transform: scale(0.86);
    transform-origin: right top;
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

  .plaza-header-actions {
    justify-content: flex-start;
    margin-top: 14px;
  }

  .filter-button,
  .silent-notice-button,
  .refresh-button,
  .anonymous-toggle {
    width: 100%;
    justify-content: center;
  }

  .plaza-wall-props {
    display: none;
  }

  .post-actions {
    grid-template-columns: 1fr;
  }

  .reply-composer {
    grid-template-columns: 1fr;
  }

  .comment-composer {
    display: grid;
    grid-template-columns: 1fr;
  }

  .media-preview-backdrop,
  .avatar-preview-backdrop {
    padding: 14px;
  }
}
</style>
