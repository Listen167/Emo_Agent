import api from './client'

export interface PlazaAuthor {
  session_id: string
  nickname: string
  avatar_url?: string | null
  ebti_type?: string | null
  ebti_name?: string | null
}

export interface PlazaPostItem {
  id: number
  title?: string | null
  content: string
  mood_label?: string | null
  location?: string | null
  tags: string[]
  media_url?: string | null
  author: PlazaAuthor
  like_count: number
  comment_count: number
  repost_count: number
  liked: boolean
  xiaoxi_liked: boolean
  reposted: boolean
  published_at?: string | null
  created_at: string
}

export interface PlazaCommentItem {
  id: number
  record_id: number
  parent_id?: number | null
  reply_to_comment_id?: number | null
  reply_to_author?: PlazaAuthor | null
  author: PlazaAuthor
  author_type: 'user' | 'xiaoxi'
  content: string
  like_count: number
  reply_count: number
  replies: PlazaCommentReplyItem[]
  created_at: string
}

export interface PlazaCommentReplyItem {
  id: number
  record_id: number
  parent_id: number
  reply_to_comment_id?: number | null
  reply_to_author?: PlazaAuthor | null
  author: PlazaAuthor
  author_type: 'user' | 'xiaoxi'
  content: string
  like_count: number
  created_at: string
}

export const getPlazaPosts = (sid: string) =>
  api.get<PlazaPostItem[]>(`/plaza/posts?session_id=${encodeURIComponent(sid)}`)

export const likePlazaPost = (id: number, sid: string) =>
  api.post<PlazaPostItem>(`/plaza/posts/${id}/like?session_id=${encodeURIComponent(sid)}`)

export const unlikePlazaPost = (id: number, sid: string) =>
  api.delete<PlazaPostItem>(`/plaza/posts/${id}/like?session_id=${encodeURIComponent(sid)}`)

export const repostPlazaPost = (id: number, sid: string) =>
  api.post<PlazaPostItem>(`/plaza/posts/${id}/repost?session_id=${encodeURIComponent(sid)}`)

export const getPlazaComments = (id: number) =>
  api.get<PlazaCommentItem[]>(`/plaza/posts/${id}/comments`)

export const createPlazaComment = (id: number, sid: string, content: string) =>
  api.post<PlazaCommentItem>(`/plaza/posts/${id}/comments`, {
    session_id: sid,
    content,
  })

export const getPlazaCommentReplies = (id: number) =>
  api.get<PlazaCommentReplyItem[]>(`/plaza/comments/${id}/replies`)

export const createPlazaCommentReply = (id: number, sid: string, content: string) =>
  api.post<PlazaCommentReplyItem>(`/plaza/comments/${id}/replies`, {
    session_id: sid,
    content,
  })
