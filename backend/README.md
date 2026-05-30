# 后端服务

FastAPI 后端服务，提供认证、课程、排课、选课、作业、附件上传、提交批改、统计和账号维护接口。

## 准备环境

项目使用根目录 `.venv`。推荐用 uv 安装依赖：

```powershell
$env:UV_CACHE_DIR="..\.uv-cache"
uv pip install -r requirements.txt --python ..\.venv\Scripts\python.exe
```

如果依赖已经装好，可以跳过安装。文件上传接口依赖 `python-multipart`，缺少时 FastAPI 会在启动或测试时报错。

## 环境变量

复制示例文件：

```powershell
Copy-Item .env.example .env
```

常用配置：

```text
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/campus_manage?charset=utf8mb4
JWT_SECRET_KEY=campus-manage-dev-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
REDIS_URL=redis://127.0.0.1:6379/0
SEED_ON_STARTUP=true
UPLOAD_DIR=backend/uploads
```

说明：

- 后端在宿主机运行时，MySQL 主机用 `127.0.0.1`。
- `UPLOAD_DIR` 用于保存作业和提交附件；默认目录会在启动时自动创建。

## MySQL 初始化

如果数据库还不存在，先创建：

```sql
CREATE DATABASE campus_manage DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

服务启动时会执行 `Base.metadata.create_all` 创建表结构；开发环境默认 `SEED_ON_STARTUP=true` 会写入演示账号和基础数据。

## 启动

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

常用地址：

- 健康检查：`http://127.0.0.1:8000/api/health`
- Swagger：`http://127.0.0.1:8000/docs`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`
- 上传文件：`http://127.0.0.1:8000/uploads/...`

## 演示账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 教师 | teacher1 | 123456 |
| 学生 | student1 | 123456 |

## 测试

```powershell
$env:PYTHONPATH='.'
..\.venv\Scripts\python.exe -m pytest tests -q
```

如果从项目根目录运行：

```powershell
$env:PYTHONPATH='backend'; .\.venv\Scripts\python.exe -m pytest backend\tests -q
```
