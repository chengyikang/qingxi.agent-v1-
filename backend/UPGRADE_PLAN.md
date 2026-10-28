# QingXi V0 → V1 后端升级方案

**完成日期**: 2026-07-11
**版本**: V1.0.0
**总代码量**: 5392 行 Python

---

## 一、现有架构分析 (V0)

### V0 模块结构
```
backend/
├── api/          # API 路由层 (7个: user, chat, trust, memory, emotion, dashboard, analytics)
├── models/       # 数据模型层 (6个: User, ChatHistory, EmotionLog, Memory, PersonalityState, TrustProfile)
├── services/     # 服务层 (6个: chat, emotion, llm, memory, personality, trust)
├── emotion/      # 情绪分析器
├── memory/       # 向量存储 (ChromaDB)
├── personality/  # 人格引擎
├── trust/        # 信任引擎
├── prompt/       # Prompt 构建器
├── database/     # 数据库连接
└── config.py     # 配置
```

### V0 核心流程
```
用户消息 → 情绪分析 → 信任更新 → 人格更新 → 记忆检索 → Prompt 构建 → LLM → 回复
```

### V0 局限性
1. **Memory 是聊天记录**：只有 7 个简单 category，没有层级、来源、可信度
2. **Persona 是标签**：PersonalityState 只有 openness/initiative/vulnerability 三个整数
3. **Timeline 不存在**：没有时间轴、没有共同经历记录
4. **Insight/Reflection 不存在**：没有自我认知和成长回顾
5. **Life Import 不存在**：无法导入用户人生资料
6. **Relationship 只有 Trust**：没有关系上下文、没有里程碑记录
7. **Dashboard 简陋**：只有信任、记忆数、聊天数、情绪
8. **Prompt 构建简单**：只包含角色+信任+人格+记忆+情绪+历史

---

## 二、V1 目标架构设计

### V1 设计哲学
| 原则 | 含义 |
|------|------|
| 聊天不是核心，理解用户才是核心 | Companion Engine 协调所有模块，理解优先于回复 |
| Memory 不是聊天记录，Memory 是人生 | 6 层记忆系统，支持来源/可信度/关联 |
| Persona 不是标签，Persona 是持续成长的人格 | 多维度人格模型，LLM 深度更新 |
| Timeline 不是历史，Timeline 是共同经历 | 记录人生事件和共同经历 |
| Insight 不是建议，Insight 是观察 | 温暖观察，不给建议 |
| Reflection 不是总结，Reflection 是陪伴成长 | 陪伴式回顾，记录成长 |

### V1 模块结构
```
backend_v1/
├── api/              # API 路由层 (14个)
│   ├── _helpers.py   # 公共辅助
│   ├── user.py       # ✅ 保留
│   ├── chat.py       # ⬆ 升级 (使用 CompanionEngine)
│   ├── trust.py      # ✅ 保留
│   ├── memory.py     # ⬆ 升级 (支持层级过滤)
│   ├── emotion.py    # ⬆ 升级 (新增 trend/summary)
│   ├── dashboard.py  # ⬆ 大幅升级 (V1 面板)
│   ├── analytics.py  # ⬆ 升级
│   ├── persona.py    # 🆕 新增
│   ├── life_import.py# 🆕 新增
│   ├── timeline.py   # 🆕 新增
│   ├── relationship.py# 🆕 新增
│   ├── insight.py    # 🆕 新增
│   ├── reflection.py # 🆕 新增
│   └── life_profile.py# 🆕 新增
├── models/           # 数据模型层 (14个)
│   ├── user.py       # ⬆ 升级 (新增 V1 关系)
│   ├── chat.py       # ⬆ 升级 (新增 emotion/intent/memory_ids)
│   ├── emotion.py    # ⬆ 升级 (新增 intensity/trigger/context)
│   ├── memory.py     # ⬆ 大幅升级 (6层/来源/可信度/关联)
│   ├── personality.py# ✅ 保留兼容
│   ├── trust.py      # ✅ 保留兼容
│   ├── persona.py    # 🆕 新增
│   ├── life_event.py # 🆕 新增
│   ├── timeline.py   # 🆕 新增
│   ├── relationship_context.py # 🆕 新增
│   ├── insight.py    # 🆕 新增
│   ├── reflection.py # 🆕 新增
│   ├── life_profile.py# 🆕 新增
│   └── life_import.py# 🆕 新增
├── engines/          # 🆕 引擎层 (8个核心引擎)
│   ├── companion/    # Module 06: 产品大脑
│   ├── persona/      # Module 03: 数字人格引擎
│   ├── life_memory/  # Module 04: 人生记忆引擎
│   ├── relationship/ # Module 05: 关系引擎
│   ├── insight/      # Module 07: 洞察引擎
│   ├── reflection/   # Module 08: 反思引擎
│   ├── life_import/  # Module 01: 人生导入引擎
│   └── life_parser/  # Module 02: 人生解析引擎
├── services/         # 服务层
│   ├── chat.py       # ⬆ 委托给 CompanionEngine
│   ├── emotion.py    # ⬆ 增加情绪强度
│   ├── llm.py        # ✅ 保留
│   ├── memory.py     # ⬆ 委托给 LifeMemoryEngine
│   ├── personality.py# ✅ 保留兼容
│   └── trust.py      # ✅ 保留
├── emotion/          # ✅ 保留
├── memory/           # ✅ 保留
├── personality/      # ✅ 保留兼容
├── trust/            # ✅ 保留
├── prompt/           # ⬆ 大幅升级
│   └── builder.py    # V1 统一构建
├── database/         # ✅ 保留
└── config.py         # ⬆ 升级 (新增 V1 配置项)
```

### V1 核心流程 (CompanionEngine)
```
用户消息
  ↓
Step 1: 保存用户消息
  ↓
Step 2: Emotion Analysis → 情绪分析
  ↓
Step 3: Persona Retrieval → 获取用户人格
  ↓
Step 4: Memory Retrieval → 6层记忆检索
  ↓
Step 5: Relationship Retrieval → 关系上下文 + 里程碑
  ↓
Step 6: Timeline Retrieval → 时间轴条目
  ↓
Step 7: Insight Retrieval → 近期洞察
  ↓
Step 8: Recent History → 最近对话
  ↓
Step 9: Prompt Builder → 统一构建完整 Prompt
  ↓
Step 10: LLM → 生成回复
  ↓
Step 11: 保存回复
  ↓
Step 12: 更新信任值
  ↓
Step 13: 更新人格 (规则 + 定期 LLM 深度)
  ↓
Step 14: 检查关系里程碑
  ↓
Step 15: 提取记忆 (定期)
  ↓
Step 16: 更新时间轴
```

---

## 三、数据库 Schema 升级方案

### 新增表 (7个)

#### 1. personas (数字人格)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK → users, UNIQUE |
| identity_summary | TEXT | 一句话身份概括 |
| identity_traits | JSON | 性格特质列表 |
| identity_roles | JSON | 社会角色 |
| comm_formality | FLOAT | 正式度 0-1 |
| comm_expressiveness | FLOAT | 表达丰富度 |
| comm_directness | FLOAT | 直接程度 |
| comm_humor | FLOAT | 幽默倾向 |
| thinking_analytical | FLOAT | 分析型 |
| thinking_creative | FLOAT | 创造型 |
| thinking_practical | FLOAT | 实践型 |
| thinking_reflective | FLOAT | 反思型 |
| emotion_stability | FLOAT | 情绪稳定性 |
| emotion_expressiveness | FLOAT | 情绪表达度 |
| emotion_sensitivity | FLOAT | 情绪敏感度 |
| emotion_optimism | FLOAT | 乐观倾向 |
| emotion_patterns | JSON | 情绪模式 |
| values_core | JSON | 核心价值观 |
| preferences_topics | JSON | 喜欢的话题 |
| current_goals | JSON | 当前目标 |
| maturity_score | FLOAT | 人格成熟度 0-1 |
| growth_history | JSON | 成长记录 |
| update_count | INT | 更新次数 |
| ... | | 时间戳等 |

#### 2. life_events (人生事件)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK |
| title | VARCHAR(200) | 事件标题 |
| description | TEXT | 描述 |
| event_type | VARCHAR(50) | milestone/challenge/achievement/transition/relationship/daily |
| event_date | DATETIME | 事件发生时间 |
| impact_level | INT | 影响程度 1-10 |
| emotion_at_event | VARCHAR(20) | 当时情绪 |
| growth_significance | FLOAT | 成长意义 0-1 |
| people_involved | JSON | 相关人物 |
| source | VARCHAR(30) | chat/import/parser/manual |
| confidence | FLOAT | 可信度 |
| ... | | |

#### 3. timelines (时间轴)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK |
| entry_type | VARCHAR(50) | life_event/shared_experience/growth_node/trust_milestone/conversation_milestone |
| title | VARCHAR(200) | 标题 |
| occurred_at | DATETIME | 发生时间 |
| importance | INT | 重要性 |
| is_shared_with_companion | BOOL | 是否共同经历 |
| companion_first | VARCHAR(100) | "第一次XXX" |
| emotion_marker | VARCHAR(20) | 情绪标记 |
| ... | | |

#### 4. relationship_contexts (关系上下文)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK |
| context_type | VARCHAR(50) | first_chat/first_dream/first_trouble/... |
| title | VARCHAR(200) | "第一次聊梦想" |
| occurred_at | DATETIME | 时间 |
| significance | FLOAT | 意义度 0-1 |
| is_milestone | BOOL | 是否里程碑 |
| milestone_type | VARCHAR(50) | stranger_to_familiar/... |
| ... | | |

#### 5. insights (洞察)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK |
| insight_type | VARCHAR(30) | weekly/monthly/on_demand |
| title | VARCHAR(200) | 标题 |
| content | TEXT | 内容 |
| category | VARCHAR(50) | emotion_pattern/behavior_pattern/growth_observation/... |
| period_start/end | DATETIME | 时间范围 |
| observations | JSON | 观察列表 |
| confidence | FLOAT | 可信度 |
| ... | | |

#### 6. reflections (反思)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK |
| reflection_type | VARCHAR(30) | weekly/monthly/yearly/on_demand |
| title | VARCHAR(200) | 标题 |
| content | TEXT | 内容 |
| highlights/challenges/growth_points/gratitude/learnings | JSON | 结构化内容 |
| growth_score | FLOAT | 成长评分 0-1 |
| ... | | |

#### 7. life_profiles (人生画像)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK, UNIQUE |
| name/age_range/occupation/location/education | | 基本身份 |
| interests/goals_short_term/goals_long_term/dreams | JSON | 兴趣和目标 |
| important_people | JSON | 重要人物 |
| growth_trajectory/life_chapters | JSON | 成长轨迹 |
| values/beliefs | JSON | 价值观 |
| thinking_style/communication_style/social_style | | 思维/沟通 |
| emotion_patterns/stress_triggers/coping_mechanisms | JSON | 情绪特点 |
| completeness_score | FLOAT | 完整度 0-1 |
| ... | | |

#### 8. life_imports (导入记录)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK |
| source_type | VARCHAR(30) | qq_chat/wechat_chat/txt/markdown/pdf/docx/diary/note |
| status | VARCHAR(20) | pending/processing/parsed/completed/failed |
| parsed_data | JSON | 解析数据 |
| extracted_*_count | INT | 各类提取数量 |
| ... | | |

### 升级表

#### memories (6层升级)
| 新增字段 | 类型 | 说明 |
|----------|------|------|
| layer | VARCHAR(30) | identity/preference/relationship/life_event/emotion/growth |
| source | VARCHAR(30) | chat/import/persona/insight/reflection/system |
| confidence | FLOAT | 可信度 0-1 |
| event_time | DATETIME | 事件发生时间 |
| updated_at | DATETIME | 更新时间 |
| related_entity_type | VARCHAR(50) | 关联实体类型 |
| related_entity_id | VARCHAR(36) | 关联实体ID |
| metadata_json | JSON | 元数据 |
| is_active | BOOL | 软删除 |
| version | INT | 版本号 |

#### chat_histories (V1 增强)
| 新增字段 | 类型 | 说明 |
|----------|------|------|
| emotion_type | VARCHAR(20) | 消息情绪 |
| emotion_confidence | FLOAT | 情绪置信度 |
| intent | VARCHAR(50) | 消息意图 |
| memory_ids | JSON | 提取的记忆ID |
| persona_snapshot | JSON | 人格快照 |
| trust_score_at | INT | 当时信任值 |

#### emotion_logs (V1 增强)
| 新增字段 | 类型 | 说明 |
|----------|------|------|
| intensity | INT | 情绪强度 1-5 |
| trigger | VARCHAR(200) | 触发原因 |
| context_tags | JSON | 上下文标签 |
| is_negative | BOOL | 是否负面 |

---

## 四、API 设计

### V0 兼容 API (保持不变)
| 路由 | 方法 | 说明 |
|------|------|------|
| /api/user/create | POST | 创建用户 |
| /api/user/profile | GET | 获取用户信息 |
| /api/chat | POST | 发送消息 (V1 内部使用 CompanionEngine) |
| /api/chat/history | GET | 获取历史 |
| /api/trust | GET | 获取信任 |
| /api/emotion | GET | 获取情绪 |
| /api/memory | GET | 获取记忆 |

### V1 新增 API
| 路由 | 方法 | 说明 |
|------|------|------|
| /api/persona | GET | 获取数字人格 |
| /api/persona/prompt-dict | GET | 获取人格 Prompt 数据 |
| /api/life-import/text | POST | 从文本导入人生资料 |
| /api/life-import/file | POST | 从文件导入人生资料 |
| /api/life-import/history | GET | 获取导入历史 |
| /api/timeline | GET | 获取时间轴 |
| /api/relationship/context | GET | 获取关系上下文 |
| /api/relationship/milestones | GET | 获取关系里程碑 |
| /api/insight | GET | 获取洞察列表 |
| /api/insight/generate/weekly | POST | 生成周洞察 |
| /api/insight/generate/monthly | POST | 生成月洞察 |
| /api/reflection | GET | 获取反思列表 |
| /api/reflection/generate/weekly | POST | 生成周反思 |
| /api/reflection/generate/monthly | POST | 生成月反思 |
| /api/reflection/generate/yearly | POST | 生成年反思 |
| /api/life-profile | GET | 获取人生画像 |
| /api/memory/statistics | GET | 记忆统计 (按层/按源) |
| /api/emotion/trend | GET | 情绪趋势 |
| /api/emotion/summary | GET | 情绪摘要 |

### V1 升级 Dashboard
Dashboard 返回新增字段:
- persona: 人格摘要
- timeline: 最近时间轴
- milestones: 关系里程碑
- insights: 近期洞察
- reflections: 近期反思
- life_profile: 人生画像摘要
- memory_statistics: 按层记忆统计
- emotion_statistics: 情绪统计
- trust_curve: 信任曲线

---

## 五、完整文件清单

### 新增文件 (22个)
```
api/_helpers.py                    # API 公共辅助
api/persona.py                     # Persona API
api/life_import.py                 # Life Import API
api/timeline.py                    # Timeline API
api/relationship.py                # Relationship API
api/insight.py                     # Insight API
api/reflection.py                  # Reflection API
api/life_profile.py                # Life Profile API
models/persona.py                  # Persona 模型
models/life_event.py               # LifeEvent 模型
models/timeline.py                 # Timeline 模型
models/relationship_context.py     # RelationshipContext 模型
models/insight.py                  # Insight 模型
models/reflection.py               # Reflection 模型
models/life_profile.py             # LifeProfile 模型
models/life_import.py              # LifeImport 模型
engines/__init__.py                # Engines 入口
engines/companion/engine.py        # Module 06: 产品大脑
engines/persona/engine.py          # Module 03: 数字人格引擎
engines/life_memory/engine.py      # Module 04: 人生记忆引擎
engines/relationship/engine.py     # Module 05: 关系引擎
engines/insight/engine.py          # Module 07: 洞察引擎
engines/reflection/engine.py       # Module 08: 反思引擎
engines/life_import/engine.py      # Module 01: 人生导入引擎
engines/life_parser/engine.py      # Module 02: 人生解析引擎
```

### 升级文件 (7个)
```
config.py                          # 新增 V1 配置项
models/user.py                     # 新增 V1 关系
models/chat.py                     # 新增 emotion/intent/memory_ids
models/memory.py                   # 6层/来源/可信度/关联
models/emotion.py                  # 新增 intensity/trigger/context
api/dashboard.py                   # V1 完整面板
prompt/builder.py                  # V1 统一 Prompt 构建
```

### 委托升级文件 (3个)
```
services/chat.py                   # 委托给 CompanionEngine
services/memory.py                 # 委托给 LifeMemoryEngine
services/emotion.py                # 增加情绪强度
```

---

## 六、兼容性设计

1. **V0 API 完全兼容**：所有 V0 的 API 路由保持不变，返回格式保持 `ok/data` 结构
2. **V0 模型保留**：PersonalityState、TrustProfile 保持原表，V1 新增独立表
3. **V0 服务保留**：personality_service、trust_service 保持原有接口
4. **渐进式升级**：
   - Phase 1: 部署 V1，所有 V0 API 正常工作，V1 新 API 可用
   - Phase 2: 切换 chat_service 使用 CompanionEngine
   - Phase 3: 启用 Life Import 和 Persona 更新
   - Phase 4: 启用 Insight 和 Reflection 定期生成

---

## 七、V1 开发原则映射

| 原则 | 实现方式 |
|------|----------|
| 聊天不是核心，理解用户才是核心 | CompanionEngine 15步流程，理解优先 |
| Memory 不是聊天记录，Memory 是人生 | LifeMemoryEngine 6层系统 |
| Persona 不是标签，Persona 是持续成长的人格 | Persona 多维度 + LLM 深度更新 |
| Timeline 不是历史，Timeline 是共同经历 | Timeline + RelationshipContext |
| Insight 不是建议，Insight 是观察 | InsightEngine 观察式语气 |
| Reflection 不是总结，Reflection 是陪伴成长 | ReflectionEngine 陪伴式回顾 |

