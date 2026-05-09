# Emo Agent

一个基于 `FastAPI + Vue 3` 的情感对话 Agent 项目。

用户可以输入文本或语音，系统会先做语音转文本与情感分析，再结合设定好的情绪提示词生成回复，并支持语音播报与聊天记录保存。

## 功能简介

- 文本输入对话
- 语音输入对话
- 语音自动转文本
- 用户情绪识别
- 根据情绪调整回复风格
- Agent 回复语音播放
- 聊天记录保存
- 消息时间展示

## 项目结构

```text
Emo_Agent/
├─ ai/                    # ASR、情感分析、LLM、TTS 等能力封装
├─ backend/               # FastAPI 后端
│  ├─ app/
│  │  ├─ api/             # 接口
│  │  ├─ core/            # 配置、数据库
│  │  ├─ models/          # 数据模型
│  │  ├─ schemas/         # Pydantic schema
│  │  └─ services/        # 对话处理主流程
│  ├─ data/               # 运行时数据（已忽略，不上传）
│  ├─ .env                # 本地环境变量（已忽略，不上传）
│  └─ requirements.txt
├─ frontend/              # Vue 3 前端
│  ├─ src/
│  └─ package.json
├─ models/                # 本地模型目录（已忽略，不上传）
├─ .gitignore
└─ README.md
```

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite
- 前端：Vue 3、Vite、TypeScript、Tailwind CSS
- 语音识别：SenseVoice / Whisper 回退
- 情感分析：Transformers 本地模型
- 大模型回复：OpenAI 兼容接口
- 语音合成：在线 TTS + Windows 本地中文语音回退

## 运行前说明

这个仓库默认**不上传**以下内容：

- `backend/data/` 运行数据
- 数据库文件
- 语音文件
- 本地模型文件 `models/`
- 环境变量文件 `.env`
- 前端构建产物 `dist/`
- `node_modules/`

所以你把项目拉下来时需要自己准备：

- Python 环境
- Node.js 环境
- 后端 `.env`
- 本地模型目录（如果你的部署方式依赖这些模型）

## 后端启动

先进入后端目录并安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

然后启动服务：

```bash
python main.py
```

默认后端地址：

```text
http://localhost:8000
```

## 前端启动

先进入前端目录并安装依赖：

```bash
cd frontend
npm install
```

启动开发服务器：

```bash
npm run dev
```

默认前端地址：

```text
http://localhost:5173
```

## 环境变量

你当前项目主要会用到后端的这些配置项，写在 `backend/.env`：

```env
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=deepseek-chat
```

如果你后面有更多配置，也建议继续放在 `backend/.env`，不要直接写死到代码里。

## 聊天记录

聊天记录默认保存在：

```text
backend/data/chat.db
```

语音上传和 TTS 文件也会保存在：

```text
backend/data/
```

这些目录已经加入 `.gitignore`，不会被上传到 GitHub。

## 上传到 GitHub 前建议检查

在提交前，先确认以下内容没有被加入版本控制：

- `backend/data/`
- `models/`
- `.env`
- `frontend/node_modules/`
- `frontend/dist/`
- 各类 `.wav`、`.mp3`、`.webm` 文件

可以用下面命令检查：

```bash
git status
```

如果某些不该上传的文件以前已经被 Git 跟踪过，需要先取消跟踪：

```bash
git rm -r --cached backend/data
git rm -r --cached models
git rm -r --cached frontend/node_modules
git rm -r --cached frontend/dist
```

## 后续可改进方向

- 换成更稳定的中文本地 TTS
- 增加多轮上下文管理
- 提供会话管理页面
- 增加 Docker 部署方案
- 增加模型下载脚本和 `.env.example`

## 说明

这个项目更适合学习和演示“语音 + 情绪 + 对话 Agent”的完整流程。

如果你准备公开发布，建议你再补充：

- `LICENSE`
- `.env.example`
- 模型下载说明
- 部署文档
