# 在线选课与作业管理系统

一个前后端分离的课程管理、作业提交与成绩统计平台，面向学生、教师和管理员三类角色。系统提供课程管理、选课排课、作业发布、附件提交、批改评分、数据仪表盘和操作日志等能力。

前端采用 Vue 3 + Element Plus + ECharts，界面使用 iOS 液态玻璃风格；后端采用 FastAPI + SQLAlchemy，数据存储使用 MySQL。

## 功能特性

### 学生端

- 查看课程列表和课程安排
- 在开放时间内完成选课
- 查看本周课表
- 查看作业详情
- 提交作业文本、附件和图片
- 查看提交状态、成绩和教师评语

### 教师端

- 查看本人授课课程
- 发布和维护课程作业
- 上传作业附件
- 查看学生提交记录
- 下载提交附件
- 批改作业并发布成绩
- 通过通知入口快速处理待批改提交

### 管理端

- 查看系统数据仪表盘
- 查看用户角色分布、课程状态统计和最近操作日志
- 维护课程、上课时间、教室、容量等基础信息
- 维护学生和教师账号基础资料，支持新增、编辑和停用账号
- 设置选课开放时间
- 管理员侧边栏保留“数据仪表盘”“课程管理”“账号维护”，不进入教师/学生作业操作页

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端框架 | Vue 3, Vite, TypeScript |
| 前端状态与路由 | Pinia, Vue Router |
| UI 与图表 | Element Plus, ECharts |
| HTTP 客户端 | Axios |
| 后端框架 | FastAPI, Uvicorn |
| ORM 与校验 | SQLAlchemy 2, Pydantic |
| 数据库 | MySQL 8.0 |
| 文件上传 | python-multipart, 本地静态文件服务 |
| 测试 | pytest, FastAPI TestClient |

## 项目结构

```text
CompusmanageSys/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/              # 路由入口
│   │   ├── core/             # 配置、异常、响应、安全
│   │   ├── db/               # 数据库会话和演示数据
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── repositories/     # 数据访问层
│   │   ├── schemas/          # Pydantic Schema
│   │   └── services/         # 业务逻辑
│   ├── tests/                # 后端测试
│   ├── uploads/              # 本地上传文件目录
│   ├── .env.example          # 后端环境变量示例
│   └── requirements.txt
├── frontend/                 # Vue 前端
│   ├── src/
│   │   ├── api/              # 前端接口封装
│   │   ├── assets/           # 全局样式
│   │   ├── components/       # 通用组件
│   │   ├── layouts/          # 主布局
│   │   ├── router/           # 路由
│   │   ├── stores/           # Pinia 状态
│   │   └── views/            # 页面
│   ├── .env.example          # 前端环境变量示例
│   └── package.json
├── docker-compose.example.yml
└── README.md
```

## 环境要求

- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- Redis 7+，当前仅预留配置，业务运行不强依赖
- Windows PowerShell 或其他终端

## 快速启动

### 1. 启动 MySQL 和 Redis

如果本地没有 MySQL，可以使用示例 Compose 文件启动依赖服务：

```powershell
docker compose -f docker-compose.example.yml up -d
```

默认数据库连接为：

```text
mysql+pymysql://root:123456@127.0.0.1:3306/campus_manage?charset=utf8mb4
```

如果你使用自己的 MySQL，请同步修改 `backend/.env` 中的 `DATABASE_URL`。

### 2. 配置后端环境变量

```powershell
Copy-Item backend\.env.example backend\.env
```

常用配置：

```text
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/campus_manage?charset=utf8mb4
JWT_SECRET_KEY=campus-manage-dev-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SEED_ON_STARTUP=true
UPLOAD_DIR=backend/uploads
```

`SEED_ON_STARTUP=true` 时，后端启动会自动创建表并写入演示数据。

### 3. 安装并启动后端

项目根目录下创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

启动后端：

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

常用地址：

- 后端服务：`http://127.0.0.1:8000`
- 健康检查：`http://127.0.0.1:8000/api/health`
- Swagger 文档：`http://127.0.0.1:8000/docs`
- 上传文件访问：`http://127.0.0.1:8000/uploads/...`

### 4. 配置并启动前端

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

默认前端地址：

```text
http://127.0.0.1:5173
```

前端环境变量：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 演示账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 教师 | teacher1 | 123456 |
| 学生 | student1 | 123456 |

## 主要业务规则

- 学生只能在管理员设置的开放时间内选课。
- 选课会校验课程容量和课表冲突。
- 学生不能自行退课，退课由管理员在课程学生列表中处理。
- 教师可以发布作业、查看提交并批改成绩。
- 学生可以提交文本、附件和图片。
- 通知入口会根据角色展示新作业、成绩发布或待批改提交。
- 管理员不进入作业管理和提交批改页面，保留数据仪表盘、课程管理和账号维护入口。

## 常用命令

前端构建：

```powershell
npm --prefix frontend run build
```

后端测试：

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest backend\tests -q
```

检查 8000 端口占用：

```powershell
netstat -ano | findstr LISTENING | findstr ":8000"
```

## GitHub 上传注意事项

- `backend/.env`、`frontend/.env`、上传文件、虚拟环境、构建产物和日志文件已在 `.gitignore` 中排除。
- 不要提交真实数据库密码、生产 JWT 密钥或用户上传文件。
- `docs/` 是本地开发资料目录，当前在 `.gitignore` 中被忽略，不随 GitHub 仓库发布。

## 可选扩展

- 将后端和前端都纳入 Docker Compose
- 为管理端补充只读审计报表
- 将上传文件切换为对象存储
- 为前端增加 Vitest 或 Playwright 自动化测试
- 对 ECharts 和 Element Plus 做进一步分包优化，降低生产构建 chunk 体积
