# 在线选课和作业管理系统

前后端分离的课程作业管理系统，面向学生、教师、管理员三类角色。

- 学生：查看课程、按开放时间选课、查看课表、查看作业、提交文本说明和附件、查看成绩。
- 教师：查看授课课程、发布带附件的作业、查看学生提交、下载附件、批改作业、查看统计。
- 管理员：维护课程、上课时间和教室、设置选课开放时间、维护学生/教师账号、处理学生退课。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router、Pinia、Element Plus、Axios、ECharts
- 后端：FastAPI、SQLAlchemy、Pydantic、PyMySQL、python-multipart
- 数据库：MySQL 8.0
- 中间件：Redis 预留配置，当前业务不强依赖
- 文件存储：本地 `backend/uploads`，通过 `/uploads/...` 静态访问

## 目录结构

```text
backend/                 FastAPI 后端
frontend/                Vue3 前端
docs/api-contract.md     接口文档
docs/database-design.md  数据库设计
docker-compose.example.yml
```

## MySQL / Redis

如果只需要启动 MySQL 和 Redis：

```powershell
docker compose -f docker-compose.example.yml up -d
```

你当前本地 MySQL 配置按下面连接：

```text
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/campus_manage?charset=utf8mb4
```

如果使用 `docker-compose.example.yml`，请确保 Compose 里的 `MYSQL_ROOT_PASSWORD` 与 `backend/.env` 中的密码一致。

## 后端启动

项目使用根目录 `.venv`，由 uv 创建时可这样安装依赖：

```powershell
$env:UV_CACHE_DIR=".uv-cache"
uv pip install -r backend\requirements.txt --python .\.venv\Scripts\python.exe
```

复制环境变量文件：

```powershell
Copy-Item backend\.env.example backend\.env
```

确认 `backend\.env` 中数据库连接、JWT 密钥和上传目录配置：

```text
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/campus_manage?charset=utf8mb4
JWT_SECRET_KEY=campus-manage-dev-secret
UPLOAD_DIR=backend/uploads
```

启动后端：

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

常用地址：

- 健康检查：`http://127.0.0.1:8000/api/health`
- Swagger 文档：`http://127.0.0.1:8000/docs`
- 上传文件访问：`http://127.0.0.1:8000/uploads/...`

后端启动时会自动创建数据表；开发环境默认会写入演示数据。

## 前端启动

```powershell
cd frontend
npm install
npm run dev
```

默认前端地址：`http://127.0.0.1:5173`

开发代理已包含：

- `/api/v1` -> `http://127.0.0.1:8000`
- `/uploads` -> `http://127.0.0.1:8000`

如需指定后端地址，复制并修改：

```powershell
Copy-Item frontend\.env.example frontend\.env
```

## 演示账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 教师 | teacher1 | 123456 |
| 学生 | student1 | 123456 |

## 核心功能说明

- 课程排课按固定课段：`1-2`、`3-4`、`5-6`、`7-8`、`9-10`，对应时间自动生成。
- 学生选课受管理员设置的开放时间控制，并校验容量和课表冲突。
- 学生不能单方面退课，退课由管理员在课程学生列表中处理。
- 教师发布作业支持附件和图片；学生提交作业支持说明文本、附件和图片。
- 数据仪表盘使用 ECharts，包含提交状态、课程作业统计、成绩分布、按课程成绩统计和本周课表。

## 文档

- 接口文档：[docs/api-contract.md](docs/api-contract.md)
- 数据库设计：[docs/database-design.md](docs/database-design.md)
- 开发计划：[docs/development/project-plan.md](docs/development/project-plan.md)

## 验证命令

```powershell
npm --prefix frontend run build
$env:PYTHONPATH='backend'; .\.venv\Scripts\python.exe -m pytest backend\tests -q
```
