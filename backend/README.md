# QingXi V1 Backend

**理解用户人生的陪伴 Agent**

## V1 核心模块

| Module | 引擎 | 说明 |
|--------|------|------|
| Module 01 | LifeImportEngine | 用户人生资料导入 |
| Module 02 | LifeParserEngine | 理解导入内容，提取结构化人生数据 |
| Module 03 | PersonaEngine | 数字人格（持续成长） |
| Module 04 | LifeMemoryEngine | 6层人生记忆 |
| Module 05 | RelationshipEngine | 关系引擎（Trust + 共同经历） |
| Module 06 | CompanionEngine | 产品大脑，协调所有模块 |
| Module 07 | InsightEngine | 洞察引擎（观察用户） |
| Module 08 | ReflectionEngine | 反思引擎（陪伴成长） |

## 6层记忆系统

1. **Identity 身份层**: 核心身份信息
2. **Preference 偏好层**: 喜好和习惯
3. **Relationship 关系层**: 与他人的关系
4. **Life Event 事件层**: 重要人生事件
5. **Emotion 情绪层**: 情绪模式和特点
6. **Growth 成长层**: 成长经历和感悟

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 设置 LLM_API_KEY

# 启动
uvicorn main:app --reload --port 8000
```

## API 文档

启动后访问: http://localhost:8000/docs

## V0 兼容

所有 V0 API 完全兼容，可渐进式升级。
