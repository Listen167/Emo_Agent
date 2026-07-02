<template>
  <div class="resume-workshop">
    <header v-develop class="resume-header">
      <div class="resume-header-copy">
        <span class="kodak-chip">Career Contact Sheet</span>
        <h1 class="script-title">简历工坊</h1>
        <p>把经历整理成清晰的一页纸。内容默认保存在本地，只有使用 AI 时才发送选中文本。</p>
        <div class="resume-actions">
          <button class="secondary-button" @click="downloadJson">导出 JSON</button>
          <label class="secondary-button import-button">
            导入 JSON
            <input type="file" accept="application/json" @change="importJson" />
          </label>
          <button class="print-button" @click="printResume">打印 / PDF</button>
        </div>
      </div>
      <div class="resume-desk-props" aria-hidden="true">
        <div class="typewriter-prop">
          <span class="typewriter-paper"></span>
          <span class="typewriter-body"></span>
          <span class="typewriter-keys"></span>
        </div>
        <div class="clipped-resume-prop">
          <span class="paperclip"></span>
          <span class="resume-sheet sheet-front"></span>
          <span class="resume-sheet sheet-back"></span>
        </div>
        <div class="approved-stamp-prop">APPROVED</div>
      </div>
    </header>

    <main class="resume-layout">
      <section class="resume-editor">
        <div v-develop="60" class="editor-card">
          <span class="washi-tape"></span>
          <div class="section-title-row">
            <h2>基础信息</h2>
            <button class="ghost-button" @click="resetDemo">填入示例</button>
          </div>
          <div class="form-grid two-columns">
            <label class="field">
              <span>姓名</span>
              <input v-model="resume.basics.name" class="input" placeholder="例如：陈小曦" />
            </label>
            <label class="field">
              <span>求职方向</span>
              <input v-model="resume.basics.headline" class="input" placeholder="例如：前端开发实习生" />
            </label>
            <label class="field">
              <span>手机</span>
              <input v-model="resume.basics.phone" class="input" placeholder="138 0000 0000" />
            </label>
            <label class="field">
              <span>邮箱</span>
              <input v-model="resume.basics.email" class="input" placeholder="name@example.com" />
            </label>
            <label class="field">
              <span>城市</span>
              <input v-model="resume.basics.location" class="input" placeholder="广州" />
            </label>
            <label class="field">
              <span>链接</span>
              <input v-model="resume.basics.website" class="input" placeholder="GitHub / 作品集链接" />
            </label>
          </div>
          <label class="field">
            <span>个人简介</span>
            <textarea
              v-model="resume.basics.summary"
              class="input min-h-28"
              placeholder="用 2-3 句话概括你的优势、方向和代表经历。"
            />
          </label>
          <div class="ai-row">
            <button
              :class="['ai-button', { scanning: polishing === '个人简介' }]"
              :disabled="polishing === '个人简介'"
              @click="polishSummary"
            >
              {{ polishing === '个人简介' ? '润色中...' : 'AI 润色简介' }}
            </button>
          </div>
        </div>

        <div v-develop="90" class="editor-card">
          <div class="section-title-row">
            <h2>教育经历</h2>
            <button class="ghost-button" @click="addEducation">新增</button>
          </div>
          <article v-for="item in resume.education" :key="item.id" class="repeat-item">
            <div class="item-toolbar">
              <strong>{{ item.school || '未命名学校' }}</strong>
              <button class="delete-button" @click="removeById(resume.education, item.id)">删除</button>
            </div>
            <div class="form-grid two-columns">
              <label class="field">
                <span>学校</span>
                <input v-model="item.school" class="input" />
              </label>
              <label class="field">
                <span>专业</span>
                <input v-model="item.major" class="input" />
              </label>
              <label class="field">
                <span>时间</span>
                <input v-model="item.period" class="input" placeholder="2022.09 - 2026.06" />
              </label>
              <label class="field">
                <span>成绩/排名</span>
                <input v-model="item.detail" class="input" placeholder="GPA / 排名 / 相关课程" />
              </label>
            </div>
          </article>
        </div>

        <div v-develop="120" class="editor-card">
          <div class="section-title-row">
            <h2>项目经历</h2>
            <button class="ghost-button" @click="addProject">新增</button>
          </div>
          <article v-for="item in resume.projects" :key="item.id" class="repeat-item">
            <div class="item-toolbar">
              <strong>{{ item.name || '未命名项目' }}</strong>
              <div>
                <button
                  :class="['small-ai-button', { scanning: polishing === item.id }]"
                  :disabled="polishing === item.id"
                  @click="polishExperience(item, '项目经历')"
                >
                  {{ polishing === item.id ? '润色中...' : 'AI 润色' }}
                </button>
                <button class="delete-button" @click="removeById(resume.projects, item.id)">删除</button>
              </div>
            </div>
            <div class="form-grid two-columns">
              <label class="field">
                <span>项目名称</span>
                <input v-model="item.name" class="input" />
              </label>
              <label class="field">
                <span>角色</span>
                <input v-model="item.role" class="input" placeholder="负责人 / 前端开发 / 算法" />
              </label>
              <label class="field">
                <span>时间</span>
                <input v-model="item.period" class="input" />
              </label>
              <label class="field">
                <span>技术栈</span>
                <input v-model="item.stack" class="input" placeholder="Vue, FastAPI, LLM" />
              </label>
            </div>
            <label class="field">
              <span>经历要点</span>
              <textarea
                v-model="item.description"
                class="input min-h-32"
                placeholder="每行一条，尽量写清动作、技术、结果。"
              />
            </label>
          </article>
        </div>

        <div v-develop="150" class="editor-card">
          <div class="section-title-row">
            <h2>实习 / 工作</h2>
            <button class="ghost-button" @click="addWork">新增</button>
          </div>
          <article v-for="item in resume.work" :key="item.id" class="repeat-item">
            <div class="item-toolbar">
              <strong>{{ item.company || '未命名经历' }}</strong>
              <div>
                <button
                  :class="['small-ai-button', { scanning: polishing === item.id }]"
                  :disabled="polishing === item.id"
                  @click="polishExperience(item, '实习经历')"
                >
                  {{ polishing === item.id ? '润色中...' : 'AI 润色' }}
                </button>
                <button class="delete-button" @click="removeById(resume.work, item.id)">删除</button>
              </div>
            </div>
            <div class="form-grid two-columns">
              <label class="field">
                <span>组织 / 公司</span>
                <input v-model="item.company" class="input" />
              </label>
              <label class="field">
                <span>职位</span>
                <input v-model="item.position" class="input" />
              </label>
              <label class="field">
                <span>时间</span>
                <input v-model="item.period" class="input" />
              </label>
              <label class="field">
                <span>地点</span>
                <input v-model="item.location" class="input" />
              </label>
            </div>
            <label class="field">
              <span>工作内容</span>
              <textarea v-model="item.description" class="input min-h-32" placeholder="每行一条。" />
            </label>
          </article>
        </div>

        <div v-develop="180" class="editor-card">
          <div class="section-title-row">
            <h2>技能与荣誉</h2>
          </div>
          <label class="field">
            <span>技能标签</span>
            <textarea v-model="resume.skills" class="input min-h-24" placeholder="Vue, TypeScript, FastAPI, SQL, 机器学习" />
          </label>
          <label class="field">
            <span>荣誉奖项</span>
            <textarea v-model="resume.awards" class="input min-h-24" placeholder="每行一项，例如：第十五届蓝桥杯省级一等奖" />
          </label>
        </div>

        <div v-develop="210" class="editor-card">
          <div class="section-title-row">
            <h2>岗位适配</h2>
            <button class="ghost-button" :disabled="analyzing" @click="analyzeMatch">
              {{ analyzing ? '分析中...' : '分析匹配度' }}
            </button>
          </div>
          <label class="field">
            <span>目标岗位 JD</span>
            <textarea
              v-model="jobDescription"
              class="input min-h-32"
              placeholder="粘贴岗位描述后，可以让 AI 分析关键词、优势和缺口。"
            />
          </label>
          <div v-if="analysisResult" class="analysis-box">
            <strong>AI 分析结果</strong>
            <p>{{ analysisResult }}</p>
          </div>
        </div>

        <div v-develop="240" class="editor-card">
          <div class="section-title-row">
            <h2>简历评分</h2>
            <button class="ghost-button" @click="scoreResume">重新评分</button>
          </div>
          <div class="score-panel">
            <div
              class="score-dial"
              :style="{ '--score-angle': `${Math.round(resumeScore.total * 1.8 - 90)}deg` }"
            >
              <i aria-hidden="true"></i>
              <strong>{{ resumeScore.total }}</strong>
              <span>/ 100</span>
            </div>
            <div class="score-bars">
              <div v-for="item in resumeScore.items" :key="item.label" class="score-row">
                <span>{{ item.label }}</span>
                <i><b :style="{ width: `${item.value}%` }"></b></i>
                <em>{{ item.value }}</em>
              </div>
            </div>
          </div>
          <div class="score-suggestions">
            <p v-for="tip in resumeScore.tips" :key="tip">{{ tip }}</p>
          </div>
        </div>

        <div v-develop="270" class="editor-card">
          <div class="section-title-row">
            <h2>面试模拟</h2>
            <button class="ghost-button" @click="generateInterview">生成问题</button>
          </div>
          <label class="field">
            <span>目标岗位</span>
            <input v-model="interviewRole" class="input" placeholder="例如：前端开发实习生 / AI 产品实习生" />
          </label>
          <div class="interview-list">
            <article v-for="(question, index) in interviewQuestions" :key="question" class="interview-item">
              <span>Q{{ index + 1 }}</span>
              <p>{{ question }}</p>
            </article>
          </div>
        </div>
      </section>

      <aside v-develop="120" class="resume-preview-panel">
        <div class="preview-toolbar">
          <span>LIVE PREVIEW</span>
          <button class="ghost-button" @click="clearResume">清空</button>
        </div>
        <article class="resume-paper" aria-label="简历预览">
          <header class="paper-header">
            <div>
              <h2>{{ resume.basics.name || '你的姓名' }}</h2>
              <p>{{ resume.basics.headline || '求职方向 / 个人定位' }}</p>
            </div>
            <ul class="contact-list">
              <li v-if="resume.basics.phone">{{ resume.basics.phone }}</li>
              <li v-if="resume.basics.email">{{ resume.basics.email }}</li>
              <li v-if="resume.basics.location">{{ resume.basics.location }}</li>
              <li v-if="resume.basics.website">{{ resume.basics.website }}</li>
            </ul>
          </header>

          <section v-if="resume.basics.summary.trim()" class="paper-section">
            <h3>个人简介</h3>
            <p>{{ resume.basics.summary }}</p>
          </section>

          <section v-if="visibleEducation.length" class="paper-section">
            <h3>教育经历</h3>
            <div v-for="item in visibleEducation" :key="item.id" class="paper-item">
              <div class="paper-item-head">
                <strong>{{ item.school }}</strong>
                <span>{{ item.period }}</span>
              </div>
              <p>{{ joinParts([item.major, item.detail]) }}</p>
            </div>
          </section>

          <section v-if="visibleProjects.length" class="paper-section">
            <h3>项目经历</h3>
            <div v-for="item in visibleProjects" :key="item.id" class="paper-item">
              <div class="paper-item-head">
                <strong>{{ item.name }}</strong>
                <span>{{ item.period }}</span>
              </div>
              <p class="muted-line">{{ joinParts([item.role, item.stack]) }}</p>
              <ul>
                <li v-for="line in splitLines(item.description)" :key="line">{{ line }}</li>
              </ul>
            </div>
          </section>

          <section v-if="visibleWork.length" class="paper-section">
            <h3>实习 / 工作经历</h3>
            <div v-for="item in visibleWork" :key="item.id" class="paper-item">
              <div class="paper-item-head">
                <strong>{{ joinParts([item.company, item.position]) }}</strong>
                <span>{{ item.period }}</span>
              </div>
              <p v-if="item.location" class="muted-line">{{ item.location }}</p>
              <ul>
                <li v-for="line in splitLines(item.description)" :key="line">{{ line }}</li>
              </ul>
            </div>
          </section>

          <section v-if="skillList.length" class="paper-section compact-section">
            <h3>技能</h3>
            <p>{{ skillList.join(' / ') }}</p>
          </section>

          <section v-if="awardList.length" class="paper-section compact-section">
            <h3>荣誉奖项</h3>
            <ul>
              <li v-for="line in awardList" :key="line">{{ line }}</li>
            </ul>
          </section>
        </article>
      </aside>
    </main>

    <button
      :class="['resume-xiaoxi-fab', `resume-xiaoxi-${currentAvatarKey}`, { active: assistantOpen, thinking: assistantSending }]"
      type="button"
      aria-describedby="resume-xiaoxi-role-tip"
      aria-label="打开小曦 AI 面试官"
      @click="assistantOpen = !assistantOpen"
    >
      <img :src="currentXiaoxiAvatar.src" :alt="currentXiaoxiAvatar.alt" />
      <span id="resume-xiaoxi-role-tip" class="resume-xiaoxi-role-tip" role="tooltip">
        简历准备好了吗？我是小曦 AI 面试官，点我来一轮真实追问。
      </span>
      <span v-if="assistantSending" class="resume-xiaoxi-status-dot" aria-hidden="true"></span>
    </button>

    <Transition name="resume-assistant-panel">
      <section v-if="assistantOpen" class="resume-assistant-panel" aria-label="简历工坊小曦悬浮窗">
        <header class="assistant-panel-head">
          <div>
            <span class="kodak-chip">Resume Xiao Xi</span>
            <h2>小曦简历面试官</h2>
          </div>
          <button class="assistant-icon-button" type="button" aria-label="关闭" @click="assistantOpen = false">×</button>
        </header>

        <div ref="assistantBoard" class="assistant-message-board">
          <article
            v-for="message in assistantMessages"
            :key="message.id"
            :class="['assistant-message', message.role === 'user' ? 'assistant-user-message' : 'assistant-ai-message']"
          >
            <img
              v-if="message.role === 'assistant'"
              :class="['assistant-xiaoxi-avatar', `assistant-xiaoxi-${currentAvatarKey}`]"
              :src="currentXiaoxiAvatar.src"
              :alt="currentXiaoxiAvatar.alt"
            />
            <div>
              <span>{{ message.role === 'user' ? '我' : '小曦' }}</span>
              <p>{{ message.content }}</p>
              <audio
                v-if="message.role === 'assistant' && message.ttsAudioUrl"
                :src="resolveAssetUrl(message.ttsAudioUrl)"
                controls
                preload="none"
              ></audio>
            </div>
          </article>
          <div v-if="assistantMessages.length === 0" class="assistant-empty">
            <img
              :class="['assistant-empty-avatar', `assistant-xiaoxi-${currentAvatarKey}`]"
              :src="currentXiaoxiAvatar.src"
              :alt="currentXiaoxiAvatar.alt"
            />
            <strong>把大学经历发给我，我来帮你整理成简历表达。</strong>
            <p>输入“面试模拟”后，我会基于当前简历、岗位和技术栈进行 10 题模拟，并在结束后评分。</p>
          </div>
          <div v-if="assistantSending" class="assistant-thinking">小曦正在整理...</div>
        </div>

        <div class="assistant-quick-actions">
          <button type="button" @click="fillAssistantDraft('请帮我根据当前简历润色，并指出还需要补充哪些大学经历。')">润色补充</button>
          <button type="button" @click="fillAssistantDraft('面试模拟')">面试模拟</button>
          <button type="button" @click="clearAssistantMessages">清空窗口</button>
        </div>

        <footer class="assistant-composer">
          <textarea
            v-model="assistantDraft"
            rows="2"
            placeholder="补充经历，或输入“面试模拟”开始 10 题练习..."
            @keydown.enter.exact.prevent="sendAssistantText"
          />
          <div class="assistant-composer-actions">
            <button
              :class="['assistant-record-button', { recording: assistantRecording }]"
              :disabled="assistantSending"
              type="button"
              @click="toggleAssistantRecording"
            >
              {{ assistantRecording ? '停止' : '语音' }}
            </button>
            <button :disabled="assistantSending || !assistantDraft.trim()" type="button" @click="sendAssistantText">
              {{ assistantSending ? '发送中' : '发送' }}
            </button>
          </div>
        </footer>
      </section>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { transcribeLocalAudio } from '../api/asr'
import { resolveAssetUrl } from '../api/client'
import { analyzeResumeMatch, polishResumeText, sendResumeAssistant } from '../api/resume'
import { createClientId } from '../utils/id'

interface Basics {
  name: string
  headline: string
  phone: string
  email: string
  location: string
  website: string
  summary: string
}

interface Education {
  id: string
  school: string
  major: string
  period: string
  detail: string
}

interface Project {
  id: string
  name: string
  role: string
  period: string
  stack: string
  description: string
}

interface Work {
  id: string
  company: string
  position: string
  period: string
  location: string
  description: string
}

interface ResumeData {
  basics: Basics
  education: Education[]
  projects: Project[]
  work: Work[]
  skills: string
  awards: string
}

type RepeatItem = { id: string }
type PolishableExperience = Project | Work
type AssistantRole = 'user' | 'assistant'

interface AssistantMessage {
  id: string
  role: AssistantRole
  content: string
  ttsAudioUrl?: string | null
}

const STORAGE_KEY = 'emo-agent-resume-v1'
const ASSISTANT_STORAGE_KEY = 'emo-agent-resume-assistant-v1'
const ASSISTANT_SESSION_KEY = 'emo-agent-resume-assistant-sid-v1'
const XIAOXI_AVATAR_STORAGE_KEY = 'u-life-xiaoxi-avatar-key-v1'
const TARGET_SAMPLE_RATE = 16000

const xiaoxiAvatars = {
  usual: { src: '/xiaoxi/usual.png', alt: '小曦日常表情' },
  happy: { src: '/xiaoxi/happy.png', alt: '小曦开心表情' },
  comfort: { src: '/xiaoxi/comfort.png', alt: '小曦安慰表情' },
  angry: { src: '/xiaoxi/angry.png', alt: '小曦生气表情' },
  shy: { src: '/xiaoxi/shy.png', alt: '小曦害羞表情' },
  think: { src: '/xiaoxi/think.png', alt: '小曦思考表情' },
  naughty: { src: '/xiaoxi/naughty.png', alt: '小曦俏皮表情' },
} as const

type XiaoxiAvatarKey = keyof typeof xiaoxiAvatars

const emptyResume = (): ResumeData => ({
  basics: {
    name: '',
    headline: '',
    phone: '',
    email: '',
    location: '',
    website: '',
    summary: '',
  },
  education: [newEducation()],
  projects: [newProject()],
  work: [],
  skills: '',
  awards: '',
})

const demoResume = (): ResumeData => ({
  basics: {
    name: '林小曦',
    headline: '前端开发实习生 / AI 应用开发方向',
    phone: '138 0000 0000',
    email: 'xiaoxi@example.com',
    location: '广州',
    website: 'github.com/xiaoxi · xiaoxi.dev',
    summary: '计算机科学与技术本科生，主攻前端工程化与 AI 应用落地，熟悉 Vue 3、TypeScript、FastAPI 与 LLM/RAG 基础开发。具备从需求拆解、交互设计、前端实现到接口联调的完整项目经验，能够把复杂功能整理成稳定、可演示、可迭代的产品体验。',
  },
  education: [
    {
      id: createClientId(),
      school: '广东工业大学',
      major: '计算机科学与技术',
      period: '2022.09 - 2026.06',
      detail: 'GPA 3.7/4.0，专业前 15%；主修数据结构、数据库系统、计算机网络、软件工程、机器学习、Web 前端开发',
    },
  ],
  projects: [
    {
      id: createClientId(),
      name: 'Emo Agent 情绪陪伴与成长记录平台',
      role: '核心开发 / 前端负责人',
      period: '2026.03 - 至今',
      stack: 'Vue 3, TypeScript, Vite, FastAPI, SQLAlchemy, LLM, RAG, WebSocket',
      description: '负责聊天广场、成长记忆、简历工坊等核心页面开发，抽象 RecordComposer 通用发布器，减少重复表单逻辑并统一 public/private 发布心智。\n接入 ASR、TTS、情绪识别与流式对话能力，完成录音、转写、回复播放和异常兜底流程，提升多模态交互完整度。\n基于本地校园知识库设计 RAG 检索链路，让模型在回答竞赛、推免、课程与就业问题时优先引用可信资料。\n优化小曦头像选择与跨页面状态同步，使用 localStorage 与自定义事件保证聊天页、成长页、简历面试页展示一致。',
    },
    {
      id: createClientId(),
      name: 'AI 简历工坊与模拟面试助手',
      role: '独立开发',
      period: '2026.04 - 2026.06',
      stack: 'Vue 3, TypeScript, REST API, Prompt Engineering, LocalStorage',
      description: '设计一页式简历编辑与实时预览界面，支持基础信息、教育经历、项目经历、实习经历、技能荣誉的结构化维护。\n实现简历评分、岗位 JD 匹配、AI 润色和 10 题模拟面试流程，帮助用户从“写经历”过渡到“准备追问”。\n封装简历文本构建与历史上下文传递逻辑，使 AI 面试官能够基于当前简历、目标岗位和对话历史连续追问。\n提供 JSON 导入导出与打印/PDF 能力，保证用户数据可迁移、可备份、可直接用于投递材料整理。',
    },
  ],
  work: [
    {
      id: createClientId(),
      company: '校级软件创新实验室',
      position: '前端开发成员',
      period: '2025.09 - 2026.01',
      location: '广州',
      description: '参与实验室项目管理平台开发，负责任务看板、成员主页与数据统计模块，完成从 Figma 标注到 Vue 组件实现的交付。\n与后端同学协作制定接口字段和错误码约定，使用 Mock 数据提前联调，减少接口变更导致的返工。\n整理前端组件命名、表单校验和页面状态处理规范，沉淀 12 个可复用业务组件。',
    },
  ],
  skills: 'Vue 3, TypeScript, JavaScript ES6+, Vite, Pinia, HTML5, CSS3, Responsive Design, FastAPI, Python, SQLAlchemy, MySQL, REST API, WebSocket, LLM 应用, RAG, Prompt Engineering, Git, Figma',
  awards: '蓝桥杯程序设计竞赛省级一等奖\n大学生创新创业训练计划项目负责人\n校级优秀学生奖学金\n校级软件设计大赛二等奖',
})

function newEducation(): Education {
  return {
    id: createClientId(),
    school: '',
    major: '',
    period: '',
    detail: '',
  }
}

function newProject(): Project {
  return {
    id: createClientId(),
    name: '',
    role: '',
    period: '',
    stack: '',
    description: '',
  }
}

function newWork(): Work {
  return {
    id: createClientId(),
    company: '',
    position: '',
    period: '',
    location: '',
    description: '',
  }
}

const normalizeResume = (value: Partial<ResumeData> | null): ResumeData => {
  const fallback = emptyResume()
  if (!value || typeof value !== 'object') return fallback
  return {
    basics: { ...fallback.basics, ...(value.basics || {}) },
    education: Array.isArray(value.education) && value.education.length ? value.education.map(item => ({ ...newEducation(), ...item, id: item.id || createClientId() })) : fallback.education,
    projects: Array.isArray(value.projects) && value.projects.length ? value.projects.map(item => ({ ...newProject(), ...item, id: item.id || createClientId() })) : fallback.projects,
    work: Array.isArray(value.work) ? value.work.map(item => ({ ...newWork(), ...item, id: item.id || createClientId() })) : fallback.work,
    skills: typeof value.skills === 'string' ? value.skills : fallback.skills,
    awards: typeof value.awards === 'string' ? value.awards : fallback.awards,
  }
}

const loadInitialResume = (): ResumeData => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (!saved) return demoResume()
  try {
    return normalizeResume(JSON.parse(saved))
  } catch {
    return demoResume()
  }
}

const resume = reactive<ResumeData>(loadInitialResume())
const jobDescription = ref('岗位职责：参与 AI 产品前端研发，负责 Web 端页面、组件和交互体验实现；与后端协作完成接口联调，关注性能、可维护性和用户体验。\n任职要求：熟悉 Vue / TypeScript / JavaScript，了解 REST API、工程化构建和 Git 协作；有 AI 应用、LLM、RAG 或多模态交互项目经验优先。')
const analysisResult = ref('')
const polishing = ref<string | null>(null)
const analyzing = ref(false)
const interviewRole = ref('前端开发实习生')
const interviewQuestions = ref<string[]>([
  '请用 1 分钟介绍自己，并说明你为什么适合前端开发实习生 / AI 应用开发方向。',
  '你在「Emo Agent 情绪陪伴与成长记录平台」中承担了什么角色？最难的问题是什么？',
  '你为什么要抽象 RecordComposer？它解决了哪些重复操作和用户心智问题？',
  '讲一下你如何处理小曦头像跨页面同步，为什么选择 localStorage + 自定义事件？',
  '如果面试官追问 RAG 在项目中的价值，你会如何说明检索链路和可信回答之间的关系？',
  '如果让你重新做一次简历工坊，你会优先优化哪一部分？为什么？',
])
const assistantOpen = ref(false)
const assistantDraft = ref('')
const assistantSending = ref(false)
const assistantRecording = ref(false)
const assistantBoard = ref<HTMLElement>()
const assistantSessionId = ref(localStorage.getItem(ASSISTANT_SESSION_KEY) || createClientId())
const assistantMessages = ref<AssistantMessage[]>(loadAssistantMessages())
const storedXiaoxiAvatarKey = localStorage.getItem(XIAOXI_AVATAR_STORAGE_KEY)
const currentAvatarKey = ref<XiaoxiAvatarKey>(
  isXiaoxiAvatarKey(storedXiaoxiAvatarKey) ? storedXiaoxiAvatarKey : 'think'
)
const currentXiaoxiAvatar = computed(() => xiaoxiAvatars[currentAvatarKey.value])
let assistantMediaStream: MediaStream | null = null
let assistantRecorder: MediaRecorder | null = null
let assistantAudio: HTMLAudioElement | null = null
const resumeScore = reactive({
  total: 0,
  items: [
    { label: '完整度', value: 0 },
    { label: '项目表达', value: 0 },
    { label: '岗位匹配', value: 0 },
    { label: '量化结果', value: 0 },
  ],
  tips: ['点击重新评分，生成一份本地可演示的简历诊断。'],
})

localStorage.setItem(ASSISTANT_SESSION_KEY, assistantSessionId.value)

watch(
  resume,
  value => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
  },
  { deep: true }
)

watch(
  assistantMessages,
  value => {
    localStorage.setItem(ASSISTANT_STORAGE_KEY, JSON.stringify(value.slice(-40)))
  },
  { deep: true }
)

onMounted(() => {
  syncCurrentAvatar()
  window.addEventListener('u-life-xiaoxi-avatar-changed', syncCurrentAvatar)
})

onBeforeUnmount(() => {
  window.removeEventListener('u-life-xiaoxi-avatar-changed', syncCurrentAvatar)
  stopAssistantMedia()
  if (assistantAudio) {
    assistantAudio.pause()
    assistantAudio = null
  }
})

function isXiaoxiAvatarKey(value: string | null): value is XiaoxiAvatarKey {
  return Boolean(value && value in xiaoxiAvatars)
}

function syncCurrentAvatar() {
  const value = localStorage.getItem(XIAOXI_AVATAR_STORAGE_KEY)
  currentAvatarKey.value = isXiaoxiAvatarKey(value) ? value : 'think'
}

const visibleEducation = computed(() =>
  resume.education.filter(item => item.school.trim() || item.major.trim() || item.detail.trim())
)

const visibleProjects = computed(() =>
  resume.projects.filter(item => item.name.trim() || item.description.trim())
)

const visibleWork = computed(() =>
  resume.work.filter(item => item.company.trim() || item.position.trim() || item.description.trim())
)

const skillList = computed(() => splitTags(resume.skills))
const awardList = computed(() => splitLines(resume.awards))

const assignResume = (next: ResumeData) => {
  resume.basics = next.basics
  resume.education = next.education
  resume.projects = next.projects
  resume.work = next.work
  resume.skills = next.skills
  resume.awards = next.awards
}

const addEducation = () => {
  resume.education.push(newEducation())
}

const addProject = () => {
  resume.projects.push(newProject())
}

const addWork = () => {
  resume.work.push(newWork())
}

const removeById = <T extends RepeatItem>(items: T[], id: string) => {
  const index = items.findIndex(item => item.id === id)
  if (index >= 0) items.splice(index, 1)
}

const resetDemo = () => {
  assignResume(demoResume())
}

const clearResume = () => {
  assignResume(emptyResume())
  analysisResult.value = ''
  jobDescription.value = ''
}

const printResume = () => {
  window.print()
}

const downloadJson = () => {
  const blob = new Blob([JSON.stringify(resume, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${resume.basics.name || 'resume'}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}

const importJson = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    const text = await file.text()
    assignResume(normalizeResume(JSON.parse(text)))
  } finally {
    input.value = ''
  }
}

const polishSummary = async () => {
  const content = resume.basics.summary.trim()
  if (!content) return
  polishing.value = '个人简介'
  try {
    const { data } = await polishResumeText({
      section: '个人简介',
      content,
      job_description: jobDescription.value.trim() || undefined,
    })
    if (data.text) resume.basics.summary = data.text
  } finally {
    polishing.value = null
  }
}

const polishExperience = async (item: PolishableExperience, section: string) => {
  const content = item.description.trim()
  if (!content) return
  polishing.value = item.id
  try {
    const { data } = await polishResumeText({
      section,
      content,
      job_description: jobDescription.value.trim() || undefined,
    })
    if (data.text) item.description = data.text
  } finally {
    polishing.value = null
  }
}

const analyzeMatch = async () => {
  const jd = jobDescription.value.trim()
  const resumeText = buildResumeText()
  if (!jd || !resumeText) return
  analyzing.value = true
  analysisResult.value = ''
  try {
    const { data } = await analyzeResumeMatch({
      resume_text: resumeText,
      job_description: jd,
    })
    analysisResult.value = data.analysis
  } finally {
    analyzing.value = false
  }
}

const scoreResume = () => {
  const resumeText = buildResumeText()
  const hasContact = Boolean(resume.basics.phone.trim() && resume.basics.email.trim())
  const hasSummary = resume.basics.summary.trim().length >= 40
  const hasEducation = visibleEducation.value.length > 0
  const hasProject = visibleProjects.value.length > 0
  const hasSkills = skillList.value.length >= 4
  const completeness = [hasContact, hasSummary, hasEducation, hasProject, hasSkills].filter(Boolean).length * 20

  const projectText = resume.projects.map(item => item.description).join('\n')
  const actionWords = ['负责', '设计', '实现', '优化', '接入', '提升', '完成', '搭建', '分析']
  const actionScore = Math.min(100, actionWords.filter(word => projectText.includes(word)).length * 14 + visibleProjects.value.length * 12)

  const jd = jobDescription.value.trim()
  const jdKeywords = splitTags(jd.replace(/[，。；、\s]+/g, ',')).filter(word => word.length >= 2)
  const matchedKeywords = jdKeywords.filter(word => resumeText.includes(word)).length
  const matchScore = jdKeywords.length ? Math.min(100, Math.round((matchedKeywords / jdKeywords.length) * 100)) : Math.min(100, skillList.value.length * 10 + visibleProjects.value.length * 16)

  const quantified = (resumeText.match(/\d+|%|百分比|提升|降低|增长|用户|请求|并发/g) || []).length
  const quantityScore = Math.min(100, quantified * 12)

  resumeScore.items = [
    { label: '完整度', value: completeness },
    { label: '项目表达', value: actionScore },
    { label: '岗位匹配', value: matchScore },
    { label: '量化结果', value: quantityScore },
  ]
  resumeScore.total = Math.round(resumeScore.items.reduce((sum, item) => sum + item.value, 0) / resumeScore.items.length)

  const tips: string[] = []
  if (completeness < 80) tips.push('补齐联系方式、个人简介、教育经历、项目经历和技能标签，先保证基础完整。')
  if (actionScore < 70) tips.push('项目经历建议用“动作 + 技术 + 结果”表达，例如：设计并实现某模块，提升某指标。')
  if (matchScore < 70) tips.push('把目标 JD 里的关键词同步到技能、项目和个人简介中，但不要堆砌。')
  if (quantityScore < 60) tips.push('增加量化结果，例如响应时间、准确率、用户数、代码量、效率提升比例。')
  if (tips.length === 0) tips.push('整体结构已经比较完整，可以继续针对具体岗位做关键词和面试问答优化。')
  resumeScore.tips = tips
}

const generateInterview = () => {
  const role = interviewRole.value.trim() || resume.basics.headline || '目标岗位'
  const firstProject = visibleProjects.value[0]
  const projectName = firstProject?.name || '你的代表项目'
  const stack = firstProject?.stack || resume.skills || '你的技术栈'
  interviewQuestions.value = [
    `请用 1 分钟介绍自己，并说明你为什么适合${role}。`,
    `你在「${projectName}」中承担了什么角色？最难的问题是什么？`,
    `项目中使用了 ${stack}，你如何权衡技术选型？`,
    '如果让你重新做一次这个项目，你会优先优化哪一部分？为什么？',
    '请举一个你面对压力或不确定需求时推进任务的例子。',
    jobDescription.value.trim()
      ? '结合目标 JD，你认为自己最匹配的三项能力是什么？还有什么短板？'
      : '如果面试官追问项目结果，你会用哪些数据证明价值？',
  ]
}

function loadAssistantMessages(): AssistantMessage[] {
  const saved = localStorage.getItem(ASSISTANT_STORAGE_KEY)
  if (!saved) return []
  try {
    const parsed = JSON.parse(saved)
    if (!Array.isArray(parsed)) return []
    return parsed
      .filter(item => item && (item.role === 'user' || item.role === 'assistant') && typeof item.content === 'string')
      .map(item => ({
        id: typeof item.id === 'string' ? item.id : createClientId(),
        role: item.role,
        content: item.content,
        ttsAudioUrl: typeof item.ttsAudioUrl === 'string' ? item.ttsAudioUrl : null,
      }))
  } catch {
    return []
  }
}

const assistantHistoryPayload = () =>
  assistantMessages.value.slice(-24).map(message => ({
    role: message.role,
    content: message.content,
  }))

const fillAssistantDraft = (value: string) => {
  assistantDraft.value = value
  assistantOpen.value = true
}

const clearAssistantMessages = () => {
  assistantMessages.value = []
  localStorage.removeItem(ASSISTANT_STORAGE_KEY)
  assistantSessionId.value = createClientId()
  localStorage.setItem(ASSISTANT_SESSION_KEY, assistantSessionId.value)
}

const sendAssistantText = async () => {
  const msg = assistantDraft.value.trim()
  if (!msg || assistantSending.value) return
  assistantDraft.value = ''
  await submitAssistantMessage(msg)
}

const submitAssistantMessage = async (text: string) => {
  assistantOpen.value = true
  assistantSending.value = true
  const historyBeforeSend = assistantHistoryPayload()
  assistantMessages.value.push({
    id: createClientId(),
    role: 'user',
    content: text,
  })
  await scrollAssistantToBottom()

  await requestResumeAssistant(text, historyBeforeSend)
}

const requestResumeAssistant = async (text: string, historyBeforeSend = assistantHistoryPayload()) => {
  try {
    const { data } = await sendResumeAssistant({
      text,
      session_id: assistantSessionId.value,
      resume_text: buildResumeText(),
      job_description: jobDescription.value.trim() || undefined,
      interview_role: interviewRole.value.trim() || resume.basics.headline || undefined,
      history: historyBeforeSend,
      enable_tts: true,
    })
    const latestUser = [...assistantMessages.value].reverse().find(message => message.role === 'user')
    if (latestUser && data.user_text) latestUser.content = data.user_text
    assistantMessages.value.push({
      id: createClientId(),
      role: 'assistant',
      content: data.text,
      ttsAudioUrl: data.tts_audio_url,
    })
    await scrollAssistantToBottom()
    playAssistantReply(data.tts_audio_url)
  } catch (error) {
    const fallbackMessage = '这次没有处理成功。你可以稍后重试，或先用文字补充经历。'
    const responseMessage = typeof (error as any)?.response?.data?.detail === 'string'
      ? (error as any).response.data.detail
      : ''
    assistantMessages.value.push({
      id: createClientId(),
      role: 'assistant',
      content: responseMessage ? `${fallbackMessage}\n\n错误信息：${responseMessage}` : fallbackMessage,
    })
  } finally {
    assistantSending.value = false
  }
}

const toggleAssistantRecording = async () => {
  if (assistantRecording.value) {
    assistantRecorder?.stop()
    assistantRecording.value = false
    return
  }
  try {
    assistantMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const chunks: Blob[] = []
    assistantRecorder = new MediaRecorder(assistantMediaStream)
    assistantRecorder.ondataavailable = event => {
      if (event.data.size > 0) chunks.push(event.data)
    }
    assistantRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/webm' })
      chunks.length = 0
      stopAssistantMedia()
      const wavBlob = await convertToWav(blob)
      await submitAssistantAudio(wavBlob)
    }
    assistantRecorder.start()
    assistantRecording.value = true
  } catch {
    assistantRecording.value = false
    stopAssistantMedia()
  }
}

const submitAssistantAudio = async (wavBlob: Blob) => {
  assistantOpen.value = true
  assistantSending.value = true
  const historyBeforeSend = assistantHistoryPayload()
  const placeholder: AssistantMessage = {
    id: createClientId(),
    role: 'user',
    content: '语音输入识别中...',
  }
  assistantMessages.value.push(placeholder)
  await scrollAssistantToBottom()

  try {
    const { data } = await transcribeLocalAudio(wavBlob)
    const recognizedText = data.text.trim()
    if (!recognizedText) throw new Error('empty transcription')
    placeholder.content = recognizedText
    await requestResumeAssistant(recognizedText, historyBeforeSend)
  } catch {
    placeholder.content = '语音识别失败。请确认本地后端正在运行，或先用文字发送。'
    assistantSending.value = false
  }
}

const stopAssistantMedia = () => {
  assistantMediaStream?.getTracks().forEach(track => track.stop())
  assistantMediaStream = null
}

const playAssistantReply = async (url?: string | null) => {
  if (!url) return
  if (assistantAudio) {
    assistantAudio.pause()
    assistantAudio = null
  }
  try {
    assistantAudio = new Audio(resolveAssetUrl(url))
    await assistantAudio.play()
  } catch {
    assistantAudio = null
  }
}

const scrollAssistantToBottom = async () => {
  await nextTick()
  if (assistantBoard.value) {
    assistantBoard.value.scrollTop = assistantBoard.value.scrollHeight
  }
}

const convertToWav = async (blob: Blob): Promise<Blob> => {
  const arrayBuffer = await blob.arrayBuffer()
  const audioContext = new AudioContext()
  try {
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer.slice(0))
    const monoData = mixToMono(audioBuffer)
    const resampled = resampleAudio(monoData, audioBuffer.sampleRate, TARGET_SAMPLE_RATE)
    const wavBuffer = encodeWav(resampled, TARGET_SAMPLE_RATE)
    return new Blob([wavBuffer], { type: 'audio/wav' })
  } finally {
    audioContext.close()
  }
}

const mixToMono = (buffer: AudioBuffer): Float32Array => {
  const length = buffer.length
  const result = new Float32Array(length)
  for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
    const data = buffer.getChannelData(ch)
    for (let i = 0; i < length; i++) result[i] += data[i]
  }
  for (let i = 0; i < length; i++) result[i] /= buffer.numberOfChannels
  return result
}

const resampleAudio = (data: Float32Array, fromRate: number, toRate: number): Float32Array => {
  if (fromRate === toRate) return data
  const ratio = fromRate / toRate
  const newLength = Math.round(data.length / ratio)
  const result = new Float32Array(newLength)
  for (let i = 0; i < newLength; i++) {
    const srcIdx = i * ratio
    const srcIdxFloor = Math.floor(srcIdx)
    const srcIdxCeil = Math.min(srcIdxFloor + 1, data.length - 1)
    const t = srcIdx - srcIdxFloor
    result[i] = data[srcIdxFloor] * (1 - t) + data[srcIdxCeil] * t
  }
  return result
}

const encodeWav = (samples: Float32Array, sampleRate: number): ArrayBuffer => {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
  }
  writeString(0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, samples.length * 2, true)
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
  }
  return buffer
}

const buildResumeText = () => {
  const lines = [
    resume.basics.name,
    resume.basics.headline,
    resume.basics.summary,
    ...resume.education.map(item => joinParts([item.school, item.major, item.period, item.detail])),
    ...resume.projects.map(item => joinParts([item.name, item.role, item.period, item.stack, item.description])),
    ...resume.work.map(item => joinParts([item.company, item.position, item.period, item.location, item.description])),
    resume.skills,
    resume.awards,
  ]
  return lines.filter(Boolean).join('\n')
}

const splitLines = (value: string) =>
  value
    .split(/\r?\n/)
    .map(line => line.trim().replace(/^[\-*•]\s*/, ''))
    .filter(Boolean)

const splitTags = (value: string) =>
  value
    .replace(/，/g, ',')
    .split(/[,;\n]/)
    .map(item => item.trim())
    .filter(Boolean)

const joinParts = (parts: Array<string | undefined | null>) =>
  parts.map(part => (part || '').trim()).filter(Boolean).join(' · ')

scoreResume()
generateInterview()
</script>

<style scoped>
.resume-workshop {
  min-height: 100vh;
  padding: 26px 30px 42px;
}

.resume-header {
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

.resume-header-copy {
  min-width: 0;
  flex: 1;
}

.resume-header h1 {
  margin: 8px 0 0;
  font-size: clamp(44px, 6vw, 72px);
  line-height: 0.9;
}

.resume-header p {
  margin: 8px 0 0;
  max-width: 680px;
  color: var(--journal-muted);
  font-size: 14px;
}

.kodak-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--journal-kodak);
  color: var(--journal-ink);
  font-size: 12px;
  font-weight: 700;
}

.resume-actions {
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

.resume-desk-props {
  position: relative;
  flex: 0 0 230px;
  width: 230px;
  height: 130px;
}

.typewriter-prop {
  position: absolute;
  right: 8px;
  bottom: 5px;
  width: 124px;
  height: 88px;
  transform: rotate(-2deg);
}

.typewriter-paper {
  position: absolute;
  left: 34px;
  top: 0;
  width: 58px;
  height: 48px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(253 251 247 / 94%);
  box-shadow: 0 5px 10px rgb(62 50 40 / 8%);
}

.typewriter-paper::after {
  content: "";
  position: absolute;
  left: 9px;
  right: 9px;
  top: 13px;
  height: 2px;
  background: rgb(62 50 40 / 18%);
  box-shadow: 0 9px 0 rgb(62 50 40 / 14%), 0 18px 0 rgb(62 50 40 / 10%);
}

.typewriter-body {
  position: absolute;
  left: 8px;
  right: 6px;
  bottom: 0;
  height: 50px;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 16px 16px 10px 10px;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: inset 0 1px 1px rgb(255 255 255 / 18%), 0 12px 24px rgb(62 50 40 / 18%);
}

.typewriter-keys {
  position: absolute;
  left: 24px;
  right: 22px;
  bottom: 12px;
  height: 16px;
  background:
    radial-gradient(circle, #fff8e8 0 3px, transparent 3px) 0 0 / 14px 8px repeat;
  animation: typewriterKeys 1.5s steps(2, end) infinite;
}

.clipped-resume-prop {
  position: absolute;
  left: 8px;
  bottom: 18px;
  width: 88px;
  height: 98px;
  transform: rotate(5deg);
}

.resume-sheet {
  position: absolute;
  width: 70px;
  height: 88px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(253 251 247 / 94%);
  box-shadow: 0 10px 18px rgb(62 50 40 / 12%);
}

.sheet-back {
  left: 10px;
  top: 5px;
  background: rgb(255 248 232 / 92%);
}

.sheet-front {
  left: 0;
  top: 0;
  z-index: 2;
}

.sheet-front::after {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  top: 20px;
  height: 3px;
  background: rgb(62 50 40 / 20%);
  box-shadow:
    0 14px 0 rgb(62 50 40 / 14%),
    0 28px 0 rgb(62 50 40 / 12%),
    0 42px 0 rgb(62 50 40 / 10%);
}

.paperclip {
  position: absolute;
  z-index: 4;
  left: 9px;
  top: -8px;
  width: 18px;
  height: 36px;
  border: 3px solid var(--journal-stamp);
  border-left-width: 2px;
  border-radius: 999px;
  transform: rotate(-18deg);
}

.approved-stamp-prop {
  position: absolute;
  right: 78px;
  bottom: 12px;
  z-index: 5;
  padding: 7px 10px;
  border: 2px solid var(--journal-stamp);
  border-radius: 8px;
  color: var(--journal-stamp);
  background: rgb(255 248 232 / 58%);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
  transform: rotate(-10deg);
  opacity: 0.74;
}

.secondary-button,
.print-button,
.ghost-button,
.ai-button,
.small-ai-button,
.delete-button {
  min-height: 38px;
  border-radius: 10px;
  padding: 0 14px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.secondary-button,
.ghost-button {
  color: var(--journal-ink);
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(253 251 247 / 70%);
}

.print-button,
.ai-button {
  position: relative;
  overflow: hidden;
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 16%);
}

.small-ai-button {
  position: relative;
  overflow: hidden;
  margin-right: 8px;
  color: #fff8e8;
  background: var(--journal-stamp);
}

.ai-button.scanning::after,
.small-ai-button.scanning::after {
  content: "";
  position: absolute;
  inset: -30% auto -30% -42%;
  width: 42%;
  background: linear-gradient(90deg, transparent, rgb(255 248 232 / 52%), transparent);
  transform: skewX(-18deg);
  animation: aiScanline 0.82s ease-in-out infinite;
}

.delete-button {
  min-height: 32px;
  padding: 0 10px;
  color: var(--journal-stamp);
  background: transparent;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.import-button {
  display: inline-flex;
  align-items: center;
}

.import-button input {
  display: none;
}

.resume-layout {
  display: grid;
  grid-template-columns: minmax(340px, 480px) minmax(620px, 1fr);
  gap: 24px;
  align-items: start;
  padding-top: 26px;
}

.resume-editor {
  display: grid;
  gap: 18px;
}

.editor-card {
  position: relative;
  padding: 22px;
  border: 1px solid rgb(62 50 40 / 18%);
  background: #fff8e8;
  box-shadow: 0 18px 42px rgb(62 50 40 / 14%);
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

.section-title-row,
.item-toolbar,
.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-title-row {
  margin-bottom: 14px;
}

.section-title-row h2 {
  margin: 0;
  color: var(--journal-ink);
  font-size: 21px;
}

.form-grid {
  display: grid;
  gap: 12px;
}

.two-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.field {
  display: grid;
  gap: 6px;
  margin-top: 12px;
}

.field span {
  color: var(--journal-muted);
  font-size: 12px;
  font-weight: 700;
}

.input {
  width: 100%;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 10px;
  padding: 0.72rem 0.8rem;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 76%);
}

textarea.input {
  resize: vertical;
  line-height: 1.6;
}

.input:focus {
  border-color: rgb(200 90 84 / 48%);
  box-shadow: 0 0 0 3px rgb(200 90 84 / 12%);
}

.min-h-24 {
  min-height: 96px;
}

.min-h-28 {
  min-height: 112px;
}

.min-h-32 {
  min-height: 128px;
}

.repeat-item {
  margin-top: 14px;
  padding: 14px;
  border: 1px dashed rgb(62 50 40 / 22%);
  background: rgb(253 251 247 / 48%);
}

.item-toolbar strong {
  color: var(--journal-ink);
  font-size: 14px;
}

.ai-row {
  margin-top: 12px;
}

.analysis-box {
  margin-top: 14px;
  padding: 14px;
  border-left: 4px solid var(--journal-stamp);
  background: rgb(253 251 247 / 70%);
}

.analysis-box strong {
  color: var(--journal-stamp);
  font-size: 13px;
}

.analysis-box p {
  margin: 8px 0 0;
  white-space: pre-wrap;
  color: var(--journal-ink);
  font-size: 13px;
  line-height: 1.7;
}

.score-panel {
  display: grid;
  grid-template-columns: 124px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  margin-top: 14px;
}

.score-dial {
  position: relative;
  overflow: hidden;
  width: 124px;
  height: 124px;
  display: grid;
  place-items: center;
  border: 8px solid #f5e8ce;
  border-radius: 999px;
  color: #fff8e8;
  background: radial-gradient(circle at center, #3e3228 0 34%, #20150f 35% 100%);
  box-shadow: inset 0 0 0 2px rgb(255 255 255 / 18%), 0 12px 26px rgb(62 50 40 / 18%);
}

.score-dial::before {
  content: "";
  position: absolute;
  inset: 9px;
  border-radius: inherit;
  background:
    conic-gradient(from 270deg, var(--journal-kodak) 0 180deg, transparent 180deg 360deg),
    repeating-conic-gradient(from 270deg, rgb(255 248 232 / 42%) 0deg 2deg, transparent 2deg 12deg);
  mask: radial-gradient(circle, transparent 0 55%, #000 56% 100%);
  animation: gaugeWarmup 0.9s ease-out both;
}

.score-dial::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 17px;
  width: 2px;
  height: 44px;
  border-radius: 999px;
  background: #f7d66c;
  box-shadow: 0 0 10px rgb(247 214 108 / 50%);
  transform-origin: 50% 45px;
  transform: translateX(-50%) rotate(var(--score-angle));
  transition: transform 0.55s cubic-bezier(0.2, 0.9, 0.2, 1);
}

.score-dial i {
  position: absolute;
  left: 50%;
  top: 57px;
  z-index: 2;
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: #fff8e8;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 0 4px rgb(62 50 40 / 32%);
}

.score-dial strong,
.score-dial span {
  position: relative;
  z-index: 3;
  display: block;
  line-height: 1;
}

.score-dial strong {
  align-self: end;
  font-size: 42px;
}

.score-dial span {
  align-self: start;
  color: rgb(255 248 232 / 78%);
  font-size: 12px;
}

.score-bars {
  display: grid;
  gap: 10px;
}

.score-row {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr) 36px;
  gap: 10px;
  align-items: center;
  color: var(--journal-muted);
  font-size: 12px;
  font-weight: 700;
}

.score-row i {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: rgb(62 50 40 / 10%);
}

.score-row b {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--journal-stamp), var(--journal-kodak));
  transition: width 0.35s ease;
}

.score-row em {
  color: var(--journal-ink);
  font-style: normal;
  text-align: right;
}

.score-suggestions,
.interview-list {
  display: grid;
  gap: 9px;
  margin-top: 14px;
}

.score-suggestions p,
.interview-item {
  margin: 0;
  padding: 11px 13px;
  border-left: 4px solid var(--journal-stamp);
  background: rgb(253 251 247 / 66%);
  color: var(--journal-muted);
  font-size: 13px;
  line-height: 1.65;
}

.interview-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 10px;
  border-left-color: var(--journal-kodak);
}

@keyframes aiScanline {
  to {
    transform: translateX(340%) skewX(-18deg);
  }
}

@keyframes gaugeWarmup {
  from {
    opacity: 0.2;
    transform: rotate(-8deg);
  }
  to {
    opacity: 1;
    transform: rotate(0);
  }
}

@keyframes typewriterKeys {
  0%,
  100% {
    opacity: 0.72;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(1px);
  }
}

.interview-item span {
  color: var(--journal-stamp);
  font-weight: 700;
}

.interview-item p {
  margin: 0;
  color: var(--journal-ink);
}

.resume-preview-panel {
  position: sticky;
  top: 24px;
  align-self: start;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  overscroll-behavior: contain;
  padding-right: 8px;
  scrollbar-gutter: stable;
}

.resume-preview-panel::-webkit-scrollbar {
  width: 8px;
}

.resume-preview-panel::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgb(62 50 40 / 22%);
}

.resume-preview-panel::-webkit-scrollbar-track {
  background: rgb(255 248 232 / 32%);
}

.preview-toolbar {
  position: sticky;
  top: 0;
  z-index: 2;
  margin-bottom: 12px;
  padding: 12px 14px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(255 248 232 / 66%);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.preview-toolbar span {
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 700;
}

.resume-paper {
  width: min(100%, 820px);
  min-height: 1120px;
  margin: 0 auto;
  padding: 46px 54px;
  color: #1f2933;
  background: #fffdf8;
  border: 1px solid rgb(62 50 40 / 14%);
  box-shadow: 0 24px 58px rgb(62 50 40 / 18%);
  font-family: Arial, "Microsoft YaHei", sans-serif;
}

.paper-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 18px;
  border-bottom: 2px solid #293241;
}

.paper-header h2 {
  margin: 0;
  color: #111827;
  font-size: 32px;
  line-height: 1.15;
  letter-spacing: 0;
}

.paper-header p {
  margin: 8px 0 0;
  color: #4b5563;
  font-size: 15px;
}

.contact-list {
  display: grid;
  gap: 4px;
  margin: 0;
  padding: 0;
  color: #4b5563;
  font-size: 12px;
  text-align: right;
  list-style: none;
}

.paper-section {
  margin-top: 18px;
}

.paper-section h3 {
  margin: 0 0 9px;
  padding-bottom: 5px;
  color: #111827;
  border-bottom: 1px solid #d1d5db;
  font-size: 15px;
  letter-spacing: 0;
}

.paper-section p {
  margin: 0;
  color: #26313f;
  font-size: 13px;
  line-height: 1.65;
}

.paper-item {
  margin-top: 10px;
}

.paper-item-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.paper-item-head strong {
  color: #111827;
  font-size: 14px;
}

.paper-item-head span {
  flex: 0 0 auto;
  color: #4b5563;
  font-size: 12px;
}

.muted-line {
  color: #4b5563 !important;
  font-size: 12px !important;
}

.paper-section ul {
  margin: 6px 0 0;
  padding-left: 18px;
}

.paper-section li {
  margin: 3px 0;
  color: #26313f;
  font-size: 12.5px;
  line-height: 1.55;
}

.compact-section p {
  font-size: 12.5px;
}

.resume-xiaoxi-fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 50;
  width: 76px;
  height: 76px;
  display: grid;
  place-items: center;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 24px;
  background: rgb(255 248 232 / 88%);
  box-shadow: 0 18px 40px rgb(62 50 40 / 22%);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.resume-xiaoxi-fab:hover,
.resume-xiaoxi-fab:focus-visible,
.resume-xiaoxi-fab.active {
  transform: translateY(-3px);
  box-shadow: 0 22px 48px rgb(62 50 40 / 26%);
}

.resume-xiaoxi-fab img {
  width: 64px;
  height: 64px;
  object-fit: contain;
  filter: drop-shadow(0 8px 10px rgb(62 50 40 / 16%));
  transform-origin: 50% 88%;
}

.resume-xiaoxi-usual img,
.assistant-xiaoxi-usual {
  animation: xiaoxiBreathe 4.6s ease-in-out infinite;
}

.resume-xiaoxi-think img,
.assistant-xiaoxi-think {
  animation: xiaoxiThink 1.45s ease-in-out infinite;
}

.resume-xiaoxi-happy img,
.assistant-xiaoxi-happy {
  animation: xiaoxiHappy 1.9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}

.resume-xiaoxi-comfort img,
.assistant-xiaoxi-comfort {
  animation: xiaoxiComfort 3.2s ease-in-out infinite;
}

.resume-xiaoxi-angry img,
.assistant-xiaoxi-angry {
  animation: xiaoxiAngry 0.42s ease-in-out infinite;
}

.resume-xiaoxi-shy img,
.assistant-xiaoxi-shy {
  animation: xiaoxiShy 2.2s ease-in-out infinite;
}

.resume-xiaoxi-naughty img,
.assistant-xiaoxi-naughty {
  animation: xiaoxiNaughty 2.1s ease-in-out infinite;
}

.resume-xiaoxi-role-tip {
  position: absolute;
  right: calc(100% + 12px);
  bottom: 8px;
  width: 236px;
  padding: 10px 12px;
  border: 1px solid rgb(62 50 40 / 16%);
  border-radius: 12px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 96%);
  box-shadow: 0 14px 30px rgb(62 50 40 / 18%);
  font-size: 12px;
  font-weight: 800;
  line-height: 1.55;
  text-align: left;
  opacity: 0;
  pointer-events: none;
  transform: translateX(8px) translateY(4px);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.resume-xiaoxi-role-tip::after {
  content: "";
  position: absolute;
  right: -7px;
  bottom: 20px;
  width: 12px;
  height: 12px;
  border-top: 1px solid rgb(62 50 40 / 16%);
  border-right: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 96%);
  transform: rotate(45deg);
}

.resume-xiaoxi-fab:hover .resume-xiaoxi-role-tip,
.resume-xiaoxi-fab:focus-visible .resume-xiaoxi-role-tip {
  opacity: 1;
  transform: translateX(0) translateY(0);
}

.resume-xiaoxi-status-dot {
  position: absolute;
  right: 10px;
  top: 10px;
  width: 12px;
  height: 12px;
  border: 2px solid #fff8e8;
  border-radius: 999px;
  background: var(--journal-stamp);
  box-shadow: 0 0 0 5px rgb(200 90 84 / 14%);
}

.resume-assistant-panel {
  position: fixed;
  right: 28px;
  bottom: 116px;
  z-index: 49;
  width: min(420px, calc(100vw - 32px));
  height: min(650px, calc(100vh - 142px));
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto auto;
  overflow: hidden;
  border: 1px solid rgb(62 50 40 / 18%);
  background: rgb(255 248 232 / 96%);
  box-shadow: 0 28px 68px rgb(62 50 40 / 26%);
}

.assistant-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 12px;
  border-bottom: 1px solid rgb(62 50 40 / 12%);
  background: rgb(253 251 247 / 70%);
}

.assistant-panel-head h2 {
  margin: 8px 0 0;
  color: var(--journal-ink);
  font-size: 18px;
}

.assistant-icon-button {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid rgb(62 50 40 / 16%);
  border-radius: 10px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 72%);
  cursor: pointer;
  font-size: 22px;
  line-height: 1;
}

.assistant-message-board {
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  display: grid;
  align-content: start;
  gap: 12px;
}

.assistant-message-board::-webkit-scrollbar {
  width: 7px;
}

.assistant-message-board::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgb(62 50 40 / 20%);
}

.assistant-message {
  display: flex;
  gap: 9px;
  align-items: flex-start;
}

.assistant-user-message {
  justify-content: flex-end;
}

.assistant-message img {
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  object-fit: contain;
  filter: drop-shadow(0 6px 8px rgb(62 50 40 / 14%));
  transform-origin: 50% 88%;
}

.assistant-message div {
  max-width: min(310px, 82%);
  padding: 11px 12px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(253 251 247 / 82%);
}

.assistant-user-message div {
  background: rgb(232 195 108 / 38%);
}

.assistant-message span {
  display: block;
  margin-bottom: 5px;
  color: var(--journal-stamp);
  font-size: 11px;
  font-weight: 800;
}

.assistant-message p {
  margin: 0;
  white-space: pre-wrap;
  color: var(--journal-ink);
  font-size: 13px;
  line-height: 1.7;
}

.assistant-message audio {
  width: 100%;
  height: 34px;
  margin-top: 10px;
}

.assistant-empty {
  display: grid;
  justify-items: center;
  gap: 10px;
  margin: 24px 0;
  padding: 20px 16px;
  text-align: center;
  border: 1px dashed rgb(62 50 40 / 24%);
  background: rgb(253 251 247 / 58%);
}

.assistant-empty img {
  width: 86px;
  height: 86px;
  object-fit: contain;
  filter: drop-shadow(0 8px 12px rgb(62 50 40 / 14%));
  transform-origin: 50% 88%;
}

.assistant-empty strong {
  color: var(--journal-ink);
  font-size: 14px;
  line-height: 1.5;
}

.assistant-empty p {
  margin: 0;
  color: var(--journal-muted);
  font-size: 12px;
  line-height: 1.6;
}

.assistant-thinking {
  width: fit-content;
  padding: 8px 11px;
  color: var(--journal-muted);
  border: 1px solid rgb(62 50 40 / 12%);
  border-radius: 999px;
  background: rgb(253 251 247 / 78%);
  font-size: 12px;
}

.assistant-quick-actions {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid rgb(62 50 40 / 10%);
  background: rgb(253 251 247 / 50%);
}

.assistant-quick-actions button {
  min-height: 32px;
  padding: 0 10px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 10px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 80%);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.assistant-composer {
  display: grid;
  gap: 9px;
  padding: 12px;
  border-top: 1px solid rgb(62 50 40 / 12%);
  background: rgb(255 248 232 / 88%);
}

.assistant-composer textarea {
  width: 100%;
  min-height: 68px;
  max-height: 130px;
  resize: vertical;
  border: 1px solid rgb(62 50 40 / 18%);
  border-radius: 12px;
  padding: 10px 11px;
  outline: none;
  color: var(--journal-ink);
  background: rgb(253 251 247 / 82%);
  font-size: 13px;
  line-height: 1.6;
}

.assistant-composer-actions {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  gap: 8px;
}

.assistant-composer-actions button {
  min-height: 38px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 800;
}

.assistant-record-button {
  color: var(--journal-ink);
  background: var(--journal-kodak);
}

.assistant-record-button.recording {
  color: #fff8e8;
  background: var(--journal-stamp);
  animation: recordPulse 0.9s ease-in-out infinite;
}

.assistant-composer-actions button:last-child {
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
}

.resume-assistant-panel-enter-active,
.resume-assistant-panel-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.resume-assistant-panel-enter-from,
.resume-assistant-panel-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}

@keyframes recordPulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgb(200 90 84 / 18%);
  }
  50% {
    box-shadow: 0 0 0 6px rgb(200 90 84 / 10%);
  }
}

@keyframes xiaoxiBreathe {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-3px) scale(1.025);
  }
}

@keyframes xiaoxiThink {
  0%,
  100% {
    transform: rotate(-2deg) translateY(0);
  }
  50% {
    transform: rotate(3deg) translateY(-3px);
  }
}

@keyframes xiaoxiHappy {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  28% {
    transform: translateY(-7px) scale(1.06);
  }
  48% {
    transform: translateY(1px) scale(0.99);
  }
}

@keyframes xiaoxiComfort {
  0%,
  100% {
    transform: translateY(0) scale(1);
    filter: drop-shadow(0 5px 8px rgb(62 50 40 / 16%));
  }
  50% {
    transform: translateY(-4px) scale(1.03);
    filter: drop-shadow(0 9px 14px rgb(200 90 84 / 20%));
  }
}

@keyframes xiaoxiAngry {
  0%,
  100% {
    transform: translateX(0) rotate(0);
  }
  25% {
    transform: translateX(-2px) rotate(-2deg);
  }
  75% {
    transform: translateX(2px) rotate(2deg);
  }
}

@keyframes xiaoxiShy {
  0%,
  100% {
    transform: rotate(0) scale(1);
  }
  50% {
    transform: rotate(-4deg) scale(1.025);
  }
}

@keyframes xiaoxiNaughty {
  0%,
  100% {
    transform: rotate(0) translateY(0);
  }
  30% {
    transform: rotate(5deg) translateY(-4px);
  }
  58% {
    transform: rotate(-3deg) translateY(1px);
  }
}

@media (max-width: 1180px) {
  .resume-header {
    align-items: flex-start;
  }

  .resume-desk-props {
    flex-basis: 190px;
    transform: scale(0.88);
    transform-origin: right top;
  }

  .resume-layout {
    display: block;
  }

  .resume-preview-panel {
    position: relative;
    top: auto;
    max-height: none;
    overflow: visible;
    padding-right: 0;
    margin-top: 24px;
  }

  .preview-toolbar {
    position: static;
  }
}

@media (max-width: 720px) {
  .resume-workshop {
    padding: 16px 14px 26px;
  }

  .resume-header {
    display: block;
    padding: 20px;
  }

  .resume-actions {
    justify-content: flex-start;
    min-width: 0;
    margin-top: 16px;
  }

  .resume-desk-props {
    display: none;
  }

  .two-columns {
    grid-template-columns: 1fr;
  }

  .resume-paper {
    min-height: auto;
    padding: 30px 22px;
  }

  .paper-header {
    display: block;
  }

  .contact-list {
    margin-top: 12px;
    text-align: left;
  }

  .score-panel {
    grid-template-columns: 1fr;
  }

  .resume-xiaoxi-fab {
    right: 16px;
    bottom: 16px;
    width: 66px;
    height: 66px;
    border-radius: 20px;
  }

  .resume-xiaoxi-fab img {
    width: 56px;
    height: 56px;
  }

  .resume-xiaoxi-role-tip {
    right: 0;
    bottom: calc(100% + 10px);
    width: min(236px, calc(100vw - 32px));
    transform: translateY(8px);
  }

  .resume-xiaoxi-role-tip::after {
    right: 24px;
    bottom: -7px;
    transform: rotate(135deg);
  }

  .resume-xiaoxi-fab:hover .resume-xiaoxi-role-tip,
  .resume-xiaoxi-fab:focus-visible .resume-xiaoxi-role-tip {
    transform: translateY(0);
  }

  .resume-assistant-panel {
    right: 12px;
    bottom: 92px;
    width: calc(100vw - 24px);
    height: min(620px, calc(100vh - 110px));
  }
}

@media print {
  :global(.journal-sidebar),
  .resume-header,
  .resume-editor,
  .preview-toolbar {
    display: none !important;
  }

  :global(.journal-shell),
  :global(.journal-stage),
  .resume-workshop,
  .resume-layout,
  .resume-preview-panel {
    display: block !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  :global(.paper-texture),
  :global(body) {
    background: white !important;
  }

  :global(.paper-texture::before) {
    display: none !important;
  }

  .resume-paper {
    width: 100% !important;
    min-height: auto !important;
    margin: 0 !important;
    padding: 18mm 16mm !important;
    border: 0 !important;
    box-shadow: none !important;
  }
}
</style>
