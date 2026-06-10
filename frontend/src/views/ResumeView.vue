<template>
  <div class="resume-workshop">
    <header class="resume-header">
      <div>
        <span class="kodak-chip">Career Contact Sheet</span>
        <h1 class="script-title">简历工坊</h1>
        <p>把经历整理成清晰的一页纸。内容默认保存在本地，只有使用 AI 时才发送选中文本。</p>
      </div>
      <div class="resume-actions">
        <button class="secondary-button" @click="downloadJson">导出 JSON</button>
        <label class="secondary-button import-button">
          导入 JSON
          <input type="file" accept="application/json" @change="importJson" />
        </label>
        <button class="print-button" @click="printResume">打印 / PDF</button>
      </div>
    </header>

    <main class="resume-layout">
      <section class="resume-editor">
        <div class="editor-card">
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
            <button class="ai-button" :disabled="polishing === '个人简介'" @click="polishSummary">
              {{ polishing === '个人简介' ? '润色中...' : 'AI 润色简介' }}
            </button>
          </div>
        </div>

        <div class="editor-card">
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

        <div class="editor-card">
          <div class="section-title-row">
            <h2>项目经历</h2>
            <button class="ghost-button" @click="addProject">新增</button>
          </div>
          <article v-for="item in resume.projects" :key="item.id" class="repeat-item">
            <div class="item-toolbar">
              <strong>{{ item.name || '未命名项目' }}</strong>
              <div>
                <button class="small-ai-button" :disabled="polishing === item.id" @click="polishExperience(item, '项目经历')">
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

        <div class="editor-card">
          <div class="section-title-row">
            <h2>实习 / 工作</h2>
            <button class="ghost-button" @click="addWork">新增</button>
          </div>
          <article v-for="item in resume.work" :key="item.id" class="repeat-item">
            <div class="item-toolbar">
              <strong>{{ item.company || '未命名经历' }}</strong>
              <div>
                <button class="small-ai-button" :disabled="polishing === item.id" @click="polishExperience(item, '实习经历')">
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

        <div class="editor-card">
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

        <div class="editor-card">
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
      </section>

      <aside class="resume-preview-panel">
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
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { analyzeResumeMatch, polishResumeText } from '../api/resume'

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

const STORAGE_KEY = 'emo-agent-resume-v1'

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
    name: '陈小曦',
    headline: '前端开发实习生 / AI 应用开发方向',
    phone: '138 0000 0000',
    email: 'xiaoxi@example.com',
    location: '广州',
    website: 'github.com/xiaoxi',
    summary: '计算机相关专业本科生，关注 AI 应用与前端工程化。熟悉 Vue、TypeScript、FastAPI，能够从需求拆解、界面实现到接口联调完成完整功能闭环。',
  },
  education: [
    {
      id: crypto.randomUUID(),
      school: '广东工业大学',
      major: '计算机科学与技术',
      period: '2022.09 - 2026.06',
      detail: 'GPA 3.7/4.0，主修数据结构、数据库系统、机器学习、Web 开发',
    },
  ],
  projects: [
    {
      id: crypto.randomUUID(),
      name: 'Emo Agent 情绪陪伴系统',
      role: '核心开发',
      period: '2026.03 - 至今',
      stack: 'Vue 3, TypeScript, FastAPI, SQLAlchemy, LLM, RAG',
      description: '设计并实现聊天、生活记录、心情日历等核心模块，完成前后端接口联调。\n接入语音识别、情绪识别、TTS 与本地知识库检索，提升系统的多模态交互能力。\n基于用户场景整理校园知识库，让模型回答竞赛、推免等问题时优先引用本地资料。',
    },
  ],
  work: [],
  skills: 'Vue 3, TypeScript, Tailwind CSS, FastAPI, SQLAlchemy, Python, LLM 应用, RAG, Git',
  awards: '蓝桥杯省级一等奖\n校级优秀学生奖学金\n大学生创新创业训练计划项目负责人',
})

function newEducation(): Education {
  return {
    id: crypto.randomUUID(),
    school: '',
    major: '',
    period: '',
    detail: '',
  }
}

function newProject(): Project {
  return {
    id: crypto.randomUUID(),
    name: '',
    role: '',
    period: '',
    stack: '',
    description: '',
  }
}

function newWork(): Work {
  return {
    id: crypto.randomUUID(),
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
    education: Array.isArray(value.education) && value.education.length ? value.education.map(item => ({ ...newEducation(), ...item, id: item.id || crypto.randomUUID() })) : fallback.education,
    projects: Array.isArray(value.projects) && value.projects.length ? value.projects.map(item => ({ ...newProject(), ...item, id: item.id || crypto.randomUUID() })) : fallback.projects,
    work: Array.isArray(value.work) ? value.work.map(item => ({ ...newWork(), ...item, id: item.id || crypto.randomUUID() })) : fallback.work,
    skills: typeof value.skills === 'string' ? value.skills : fallback.skills,
    awards: typeof value.awards === 'string' ? value.awards : fallback.awards,
  }
}

const loadInitialResume = (): ResumeData => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (!saved) return emptyResume()
  try {
    return normalizeResume(JSON.parse(saved))
  } catch {
    return emptyResume()
  }
}

const resume = reactive<ResumeData>(loadInitialResume())
const jobDescription = ref('')
const analysisResult = ref('')
const polishing = ref<string | null>(null)
const analyzing = ref(false)

watch(
  resume,
  value => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
  },
  { deep: true }
)

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
  gap: 20px;
  padding: 24px 28px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 72%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
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
  align-self: center;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  min-width: 280px;
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
  color: #fff8e8;
  background: linear-gradient(145deg, #4b3525, #1a120d);
  box-shadow: 0 10px 20px rgb(62 50 40 / 16%);
}

.small-ai-button {
  margin-right: 8px;
  color: #fff8e8;
  background: var(--journal-stamp);
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

.resume-preview-panel {
  position: sticky;
  top: 24px;
}

.preview-toolbar {
  margin-bottom: 12px;
  padding: 12px 14px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(255 248 232 / 66%);
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

@media (max-width: 1180px) {
  .resume-layout {
    display: block;
  }

  .resume-preview-panel {
    position: relative;
    top: auto;
    margin-top: 24px;
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
    min-height: auto !important;
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
