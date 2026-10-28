# QingXi V1 - 慢热型陪伴 Agent

> 通过长期真诚交流建立信任，逐步开放人格的 AI 陪伴者

## 🌙 项目简介

QingXi 是一个"慢热型" AI 陪伴 Agent。不同于普通的聊天机器人，QingXi 会通过长期、真诚的交流逐步建立与用户之间的信任关系。信任值越高，QingXi 越会展现更丰富的人格层面。

## ✨ V1 核心特性

### 🧠 六层人生记忆系统
- **身份层** - 关于"我是谁"的记忆
- **偏好层** - 喜欢什么、不喜欢什么
- **关系层** - 与重要的人的关系
- **事件层** - 人生中的重要事件
- **情绪层** - 情绪相关的记忆
- **成长层** - 成长与变化的轨迹

每条记忆包含来源追踪、可信度评估、事件时间关联等元数据。

### 🕐 人生时间轴
记录用户人生中的重要时刻，以可视化时间轴形式展示。

### 💡 洞察系统
基于长期交流数据，QingXi 会尝试发现用户的行为模式和规律。

### 📖 反思回顾
定期为用户生成周/月/年度回顾，回望一起走过的时光。

### 📥 人生资料导入
支持导入 QQ/微信聊天记录、TXT、Markdown、PDF、DOCX 等格式的人生资料。
系统会自动解析并提取：人物关系、兴趣爱好、人生目标、梦想、情绪模式、人生事件、成长轨迹、价值观。
提取结果自动存入六层记忆系统，并用于构建和更新用户的人格画像。

### 🪪 人格画像
基于交流逐步构建用户的完整人格画像，包括性格特质、价值观、沟通风格等。支持通过导入人生资料快速初始化画像。

### 😊 颜文字表情系统
根据情绪和关系阶段自动匹配颜文字，风格定位"慢热、温柔、内敛"：
- **陌生阶段** - 极少使用，偶尔 neutral/greeting
- **熟悉阶段** - 适度 neutral/thinking
- **朋友阶段** - 较多 happy/comfort/thinking
- **知己阶段** - 丰富使用所有类型

## 🏗️ 项目结构

```
qingxi-v1-full/
├── backend/          # FastAPI 后端（V1）
│   ├── api/          # API 路由（16个模块）
│   ├── models/       # 数据库模型（14个模型）
│   ├── engines/      # 核心引擎
│   ├── services/     # 业务服务
│   ├── prompt/       # Prompt 构建
│   ├── memory/       # 记忆管理
│   ├── emotion/      # 情绪引擎
│   ├── trust/        # 信任系统
│   ├── personality/  # 人格系统
│   └── database/     # 数据库连接
├── frontend/         # Next.js 前端（V1 优化版）
│   ├── src/
│   │   ├── app/      # 页面（聊天/数据/时间轴/洞察/反思）
│   │   ├── components/ # 组件（含颜文字高亮）
│   │   ├── hooks/    # React Hooks
│   │   ├── services/ # API 服务
│   │   ├── types/    # TypeScript 类型
│   │   └── utils/    # 工具库（含颜文字系统）
│   └── ...
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 快速开始

### 前置条件
- Docker & Docker Compose
- OpenAI API Key

### 启动

```bash
# 1. 复制环境变量并填入你的 API Key
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 2. 启动所有服务
docker-compose up -d

# 3. 访问
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# 后端文档: http://localhost:8000/docs
```

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### Mock 模式
前端支持 Mock 模式，无需后端即可体验 UI：
```bash
cd frontend
NEXT_PUBLIC_USE_MOCK=true npm run dev
```

## 📡 API 模块

| 模块 | 路径 | 说明 |
|------|------|------|
| User | `/api/user` | 用户管理 |
| Chat | `/api/chat` | 聊天对话 |
| Trust | `/api/trust` | 信任系统 |
| Memory | `/api/memory` | 六层记忆 |
| Emotion | `/api/emotion` | 情绪引擎 |
| Persona | `/api/persona` | 人格画像 |
| Timeline | `/api/timeline` | 人生时间轴 |
| Insight | `/api/insight` | 洞察系统 |
| Reflection | `/api/reflection` | 反思回顾 |
| Life Profile | `/api/life-profile` | 人生画像 |
| Life Import | `/api/life-import` | 资料导入 |
| Relationship | `/api/relationship` | 关系上下文 |
| Dashboard | `/api/dashboard` | 数据面板 |
| Analytics | `/api/analytics` | 分析统计 |

## 🎨 技术栈

**后端**: Python 3.11 / FastAPI / SQLAlchemy / PostgreSQL / ChromaDB / OpenAI

**前端**: Next.js 14 / TypeScript / Tailwind CSS / React 18

## 📝 License

MIT
