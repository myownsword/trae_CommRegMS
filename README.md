# 社区活动报名管理系统

一个基于 Vue 3 + FastAPI + SQLite 的全栈 Web 应用，用于社区活动的发布、报名和管理。

---

## 目录结构

```
CommRegMS/
├── backend/                 # 后端 (Python 3 + FastAPI)
│   ├── database.py          # 数据库连接配置
│   ├── models.py            # SQLAlchemy ORM 模型
│   ├── schemas.py           # Pydantic 数据校验模型
│   ├── crud.py              # 数据库 CRUD 操作
│   ├── main.py              # FastAPI 主应用 & API 路由
│   └── requirements.txt     # Python 依赖
├── frontend/                # 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   │   ├── Home.vue            # 首页（活动列表 + 统计 + 筛选）
│   │   │   ├── ActivityForm.vue    # 活动创建 / 编辑页
│   │   │   └── ActivityDetail.vue  # 活动详情 + 报名 / 取消报名
│   │   ├── api/index.js     # REST API 封装 (axios)
│   │   ├── router/index.js  # Vue Router 路由配置
│   │   ├── App.vue          # 根组件
│   │   ├── main.js          # 入口文件
│   │   └── style.css        # 全局样式
│   ├── index.html
│   ├── vite.config.js       # Vite 配置（含 /api 代理）
│   └── package.json         # Node 依赖
└── README.md
```

---

## 一、依赖安装

### 1.1 后端依赖（需要 Python 3.9+）

```bash
cd backend
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 1.2 前端依赖（需要 Node.js 16+）

```bash
cd frontend
npm install
```

---

## 二、数据库初始化

后端启动时会**自动完成**以下工作：

1. 自动创建 SQLite 数据库文件 `backend/commregms.db`
2. 自动创建 `activities` 和 `registrations` 两张表
3. 首次启动自动插入演示数据（5 个活动 + 7 条报名记录）

如需重置数据库，只需删除 `backend/commregms.db` 文件，再次启动后端即可重新初始化。

---

## 三、启动服务

### 3.1 启动后端（默认端口 8000）

```bash
cd backend

# 如果已激活虚拟环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端启动成功后：
- API 根地址：<http://localhost:8000/>
- Swagger 交互式文档：<http://localhost:8000/docs>

### 3.2 启动前端（默认端口 5173）

```bash
cd frontend
npm run dev
```

前端启动后，在浏览器打开：<http://localhost:5173/>

> 前端已配置 Vite 代理，`/api` 请求会自动转发到 `http://localhost:8000/api`，无需配置 CORS。

---

## 四、核心功能

| 模块 | 功能说明 |
|------|----------|
| 活动管理 | 创建、查看、编辑、取消活动；字段包含标题、地点、开始时间、人数上限、活动说明、状态 |
| 报名管理 | 输入姓名 + 手机号 + 备注报名；同一手机号不能重复报名同一活动 |
| 名额控制 | 达到人数上限后拒绝后续报名，前端展示明确错误提示 |
| 取消报名 | 用报名手机号取消报名，剩余名额和统计数据自动同步恢复 |
| 活动详情页 | 展示活动信息、当前报名人数、剩余名额、完整报名名单和状态 |
| 首页筛选统计 | 顶部展示总活动数 / 可报名活动数 / 总报名人数；支持按状态筛选活动列表 |
| 数据持久化 | 全部数据存入 SQLite，后端启动自动建表并插入演示数据 |
| 表单校验 | 前端：必填、手机号格式、人数上限正整数；后端：同名校验、重复报名、状态校验 |

### 活动状态说明

| 状态值 | 显示 | 说明 |
|--------|------|------|
| `open` | 报名中（绿色） | 用户可正常报名 |
| `draft` | 草稿（蓝色） | 暂不开放报名 |
| `closed` | 已结束（灰色） | 活动已完成，不可报名 |
| `cancelled` | 已取消（红色） | 活动被取消，不可报名 |

---

## 五、REST API 一览

所有接口前缀均为 `/api`。

### 5.1 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/statistics` | 获取总活动数、可报名活动数、总报名人数 |

### 5.2 活动接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/activities` | 获取活动列表，支持 `?status=open` 查询参数筛选 |
| GET | `/api/activities/{id}` | 获取单个活动详情（含报名名单、当前人数、剩余名额） |
| POST | `/api/activities` | 创建活动（201 响应） |
| PUT | `/api/activities/{id}` | 编辑活动 |
| POST | `/api/activities/{id}/cancel` | 取消活动 |

### 5.3 报名接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/activities/{id}/registrations` | 报名活动（201 响应） |
| POST | `/api/activities/{id}/registrations/cancel` | 用手机号取消报名 |

### 5.4 常见错误状态码

| 状态码 | 场景 |
|--------|------|
| 400 | 活动已取消 / 已结束 / 已满员 / 人数上限低于已报名人数 |
| 404 | 活动或报名记录不存在 |
| 409 | 该手机号已报名（重复报名拦截） |
| 422 | Pydantic 参数校验失败（如手机号格式、必填项缺失等） |

---

## 六、核心功能验证场景

以下场景可通过前端页面或 Swagger 文档 (<http://localhost:8000/docs>) 逐一验证。

---

### ✅ 场景 1：创建活动成功

**操作步骤：**

1. 前端首页点击右上角 **「+ 发布活动」**
2. 填写：
   - 活动标题：`社区端午包粽子活动`
   - 活动地点：`社区食堂二楼`
   - 人数上限：`20`
   - 开始时间：选择未来任意时间
   - 活动说明：`请自带粽叶，糯米免费提供`
   - 状态：`报名中`
3. 点击 **「发布活动」**

**预期结果：**
- 成功跳转到新活动详情页
- 页面顶部显示活动信息和 `报名中` 绿色徽章
- 返回首页，`总活动数` 统计 +1，`可报名活动数` +1

**curl 验证：**
```bash
curl -X POST http://localhost:8000/api/activities \
  -H "Content-Type: application/json" \
  -d '{
    "title": "社区端午包粽子活动",
    "location": "社区食堂二楼",
    "start_time": "2026-06-22T09:00:00",
    "max_participants": 20,
    "description": "请自带粽叶，糯米免费提供",
    "status": "open"
  }'
```
预期 HTTP 201，返回创建好的活动对象。

---

### ✅ 场景 2：报名成功

**前置条件：** 存在一个状态为「报名中」且剩余名额 > 0 的活动。

**操作步骤：**

1. 从首页点击任意「报名中」的活动卡片进入详情页
2. 点击绿色 **「📝 我要报名」** 按钮
3. 填写：
   - 姓名：`李明`
   - 手机号：`13912345678`
   - 备注：`带爱人一起`
4. 点击 **「确认报名」**

**预期结果：**
- 弹窗关闭，页面顶部显示绿色提示 `🎉 报名成功！`
- 活动详情页：
  - `当前报名人数` +1
  - `剩余名额` -1
  - 报名名单表格新增一行记录（姓名：李明、手机号：139****5678）
- 返回首页，对应活动卡片的进度条和「X/Y 人已报名」数字同步更新，`总报名人数` 统计 +1

**curl 验证（以活动 id=1 为例）：**
```bash
curl -X POST http://localhost:8000/api/activities/1/registrations \
  -H "Content-Type: application/json" \
  -d '{"name": "李明", "phone": "13912345678", "remark": "带爱人一起"}'
```
预期 HTTP 201，返回报名记录。

---

### ✅ 场景 3：重复报名失败（同手机号 + 同活动）

**前置条件：** 已用手机号 `13912345678` 报名了某个活动。

**操作步骤：**

1. 进入同一个活动详情页
2. 再次点击 **「我要报名」**
3. 填写相同的手机号 `13912345678`（姓名可以不同）
4. 点击提交

**预期结果：**
- 报名弹窗内出现红色错误提示：`该手机号已报名此活动，不能重复报名`
- 报名人数和剩余名额保持不变
- 后端返回 HTTP 409 Conflict

**curl 验证：** 连续执行两次场景 2 中的相同 curl 命令，第二次返回 409。

---

### ✅ 场景 4：满员拦截（名额全部占用后拒绝报名）

**操作步骤：**

1. 先创建一个人数上限很小（例如 `max_participants = 2`）的活动，状态为「报名中」
2. 使用两个不同手机号分别报名成功（此时 2/2，剩余名额 = 0）
3. 使用第三个新手机号尝试报名

**预期结果：**
- 第三步提交后，弹窗内出现红色错误提示：`活动名额已满，报名失败`
- 活动详情页顶部显示黄色 `活动名额已满` 横幅
- 首页该活动卡片显示「已满员」且按钮消失
- 后端返回 HTTP 400

**简化版验证（创建人数上限为 1 的活动）：**
```bash
# 1. 创建上限 1 的活动
curl -X POST http://localhost:8000/api/activities \
  -H "Content-Type: application/json" \
  -d '{"title":"测试满员","location":"测试地点","start_time":"2026-06-30T10:00:00","max_participants":1,"status":"open"}'

# 假设返回 id=6

# 2. 第一个人报名（成功）
curl -X POST http://localhost:8000/api/activities/6/registrations \
  -H "Content-Type: application/json" \
  -d '{"name":"甲","phone":"13800000001"}'

# 3. 第二个人报名（失败）
curl -X POST http://localhost:8000/api/activities/6/registrations \
  -H "Content-Type: application/json" \
  -d '{"name":"乙","phone":"13800000002"}'
```
第 3 步预期返回 HTTP 400，body: `{"detail":"活动名额已满，报名失败"}`。

---

### ✅ 场景 5：取消报名后名额和统计同步恢复

**操作步骤：**

1. 选一个「报名中」且已有报名记录的活动（比如演示数据中的「亲子烘焙工作坊」）
2. 进入详情页，记录当前：
   - 当前报名人数（X）
   - 剩余名额（Y）
   - 首页的「总报名人数」数值
3. 点击 **「❌ 取消报名」** 按钮
4. 输入一条已报名记录对应的真实手机号（演示数据可尝试 `13800138004`）
5. 点击 **「确认取消报名」**

**预期结果：**
- 弹窗关闭，页面顶部显示绿色提示：`✅ 已取消报名，名额已释放`
- 详情页数据同步更新：
  - 当前报名人数：X - 1
  - 剩余名额：Y + 1
  - 报名名单表格中该条记录状态从「已报名」变为「已取消」
- 返回首页：
  - 该活动卡片进度条和 X/Y 数值同步更新
  - 顶部「总报名人数」统计 -1
- 同一个手机号之后可以再次重新报名该活动

**curl 验证：**
```bash
# 取消报名（以上面 13800000001 为例）
curl -X POST http://localhost:8000/api/activities/6/registrations/cancel \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800000001"}'

# 查看详情确认人数
curl http://localhost:8000/api/activities/6
```
预期 `current_participants` 从 1 变为 0，`remaining_slots` 从 0 变为 1。

---

## 七、附加验证场景（可选）

### 取消活动后无法再报名
- 进入任意「报名中」的活动详情页 → 点击右上角「取消活动」→ 确认
- 活动状态变为红色「已取消」，「我要报名」按钮消失，显示红色横幅「此活动已取消，无法报名」
- 直接用 curl 报名同样返回 HTTP 400：`活动已取消，无法报名`

### 手机号格式校验
- 前端报名时输入 `123456` → 立即提示「手机号格式不正确」
- 后端直接调接口传非法手机号 → 返回 HTTP 422

### 编辑活动时人数上限不能低于当前已报名人数
- 找一个已有 3 人报名的活动 → 编辑 → 将人数上限改为 2
- 提交返回错误：`人数上限不能低于当前已报名人数(3)`
