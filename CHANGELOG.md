# QingXi.agent V1 - 修复版本

## 修复内容

### 1. Frontend Dockerfile - npm镜像加速
- npm install 和 npm run build 前添加淘宝镜像源
- 解决国内环境 npm install 超时问题（1131s -> 预计60s内）

### 2. 完整项目文件（107个源文件）
- 后端 engines 模块：companion / insight / life_import / life_memory / life_parser / persona / reflection / relationship
- 后端 API 路由：含 insight / life_import / life_profile / persona / reflection / relationship / timeline
- 前端页面：import / insight / reflection / timeline
- 前端组件：InsightCard / PersonaPanel / ReflectionView / TimelineView
- 工具：kaomoji 颜文字系统

## 部署
```powershell
cd Qingxi.agent_v1
docker compose up -d --build
```
