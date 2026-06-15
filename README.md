# QingXi V1 — 慢热型陪伴 Agent

> 初始保持礼貌距离感，通过长期真诚交流建立信任，逐步开放人格。

## 核心机制

- **慢热**：初始保持礼貌距离，不主动亲近
- **信任成长**：真诚分享推动 Trust 增长，无意义闲聊几乎不长
- **关系阶段**：陌生 → 熟悉 → 朋友 → 知己，每个阶段对话风格不同
- **人格开放**：Trust 越高，QingXi 越自然、越主动、越愿意表达自己
- **长期记忆**：自动提取和检索用户的关键信息

## 技术栈

| 层 | 技术 |
|---|---|
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL + SQLAlchemy |
| Vector DB | ChromaDB |
| LLM | OpenAI API (gpt-4o-mini) |

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repo-url>
cd qingxi

# 复制环境变量
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 2. Docker 一键启动

```bash
docker-compose up -d
```

启动后访问：
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 3. 本地开发

```bash
# 启动 PostgreSQL (或使用已有实例)
# 修改 .env 中的 DATABASE_URL

# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
qingxi/
├── backend/
│   ├── api/            # API 路由
│   ├── models/         # 数据库模型
│   ├── services/       # 业务逻辑
│   ├── memory/         # 向量存储（ChromaDB）
│   ├── trust/          # 信任计算引擎
│   ├── emotion/        # 情绪分析器
│   ├── personality/    # 人格成长引擎
│   ├── prompt/         # Prompt 构建器
│   ├── database/       # 数据库连接
│   ├── config.py       # 配置
│   ├── main.py         # 入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/        # Next.js 页面
│   │   ├── components/ # UI 组件
│   │   ├── hooks/      # React Hooks
│   │   ├── services/   # API 调用
│   │   └── types/      # 类型定义
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## 关系阶段

| 阶段 | Trust 范围 | 对话风格 |
|------|-----------|---------|
| 陌生 | 0-100 | 回复短，不多问，不谈自己 |
| 熟悉 | 100-300 | 开始记住细节，增加提问 |
| 朋友 | 300-600 | 更自然，更多互动 |
| 知己 | 600+ | 深层交流，更多情感回应 |

## Trust 增长逻辑

| 用户行为 | Trust 增长 |
|---------|-----------|
| 分享经历 | +5~15 |
| 分享烦恼 | +8~20 |
| 分享梦想 | +10~20 |
| 表达感谢 | +5~10 |
| 情绪表达 | +3~8 |
| 无意义闲聊 | +0~1 |

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/user/create | 创建用户 |
| GET | /api/user/profile | 获取用户信息 |
| POST | /api/chat | 发送消息 |
| GET | /api/chat/history | 获取聊天历史 |
| GET | /api/trust | 获取信任数据 |
| GET | /api/memory | 获取记忆列表 |
| GET | /api/emotion | 获取情绪记录 |
| GET | /api/dashboard | Dashboard 数据 |
| GET | /api/analytics | 分析数据 |

## V1 禁止开发内容

- Live2D / 语音聊天 / 多角色 / 世界观 / 剧情系统
- 恋爱系统 / 好感度礼物 / 抽卡 / 商城
- 主动消息推送 / 社交功能 / 群聊 / App 端

## License

Private — 仅供开发测试使用
