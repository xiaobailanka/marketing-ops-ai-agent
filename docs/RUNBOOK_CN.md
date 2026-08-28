# 运行与部署手册

## 1. 安装 Python

建议 Python 3.11 或 3.12。

1. 打开 <https://www.python.org/downloads/>。
2. 下载 Windows 64-bit 安装程序。
3. 安装时勾选 `Add Python to PATH`。
4. 打开 PowerShell 验证：

```powershell
py --version
```

## 2. 创建虚拟环境

在项目目录运行：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止激活：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. 安装依赖

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. 初始化匿名化样例数据

```powershell
python -m scripts.initialize_sample_data
```

该命令可以重复运行；固定 Seed 会生成一致的 GTM、FIFA、Media Plan 和 Google Ads 样例数据。文件不包含客户记录。

## 5. 启动 Web App

```powershell
streamlit run app.py
```

浏览器打开：

```text
http://localhost:8501
```

首次使用建议顺序：

1. Overview 查看 Runtime KPI、QC posture 和 Attention queue。
2. Data Cleaning 选择 UG 和 2026-08-26，点击 Run cleaning。
3. Daily Report 点击 Generate report 生成同日期日报。
4. FIFA Sync 先 Preview cleaning，再 Run sync；第二次运行可验证 Skip。
5. Google Ads QC 依次点击 Detect schema、Confirm mapping、Run quality control。
6. Agent Copilot 选择一个 Common command 或输入运营请求。
7. Activity & Audit 查看任务状态和缓存的审计证据。

## 6. 运行测试

```powershell
pytest -q
```

只测试某个模块：

```powershell
pytest tests/etl -q
pytest tests/reporting -q
pytest tests/fifa -q
pytest tests/qc -q
pytest tests/ui -q
```

## 7. 命令行任务

日报：

```powershell
python -m scripts.run_daily_report --demo --country UG --date 2026-08-26
```

FIFA：

```powershell
python -m scripts.run_fifa_sync --demo --date 2026-08-26
```

日报 Excel 输出到 `data/outputs/`。

## 8. 配置环境变量

复制示例：

```powershell
Copy-Item .env.example .env
```

Public Sandbox 不需要填写任何密钥。取得合法授权后可配置 External Integration：

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_BITABLE_APP_TOKEN`
- `FEISHU_TABLE_ID`
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

不要把 `.env`、Service Account JSON 或 Token 提交到 Git。

## 9. 发布到 GitHub

先在 GitHub 创建一个空仓库，然后在项目目录运行：

```powershell
git status
git add .
git commit -m "feat: publish marketing ops workspace"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/marketing-ops-ai-agent.git
git push -u origin main
```

提交前确认：

```powershell
git status
git ls-files | Select-String -Pattern "\.env|credentials|service-account|app\.db"
```

第二条命令不应该列出任何密钥或本地数据库。

## 10. 部署 Streamlit Community Cloud

1. 登录 Streamlit Community Cloud。
2. 点击 Create app。
3. 连接公开 GitHub 仓库。
4. 选择 `main` 分支。
5. Main file path 填写 `app.py`。
6. Public Sandbox 不需要添加环境变量。
7. 部署完成后打开公开域名并检查全部页面。

如需持久化环境，可以在支持持久卷的 Docker 平台部署，并设置：

```text
DATABASE_PATH=/data/app.db
```

## 11. 查看日志

本地日志显示在运行 Streamlit 的 PowerShell 窗口。

Streamlit Community Cloud：打开应用 → Manage app → Logs。

排查时重点寻找：

- `ModuleNotFoundError`：依赖未安装或不在项目根目录。
- `External ... credentials are not configured`：外部密钥缺失；Public Sandbox 会继续使用隔离 Connector。
- `缺少日报平台 Sheet`：上传 Excel 没有 FB、TT、GG。
- `未识别到有效表头`：表头不在前 25 行或缺少关键字段。
- `Schema Mapping 必须人工确认`：尚未点击 Confirm Mapping。

## 12. 常见问题

### `python` 命令不存在

使用：

```powershell
py -3.11 --version
```

如果 `py` 也不存在，重新安装 Python 并勾选 Add Python to PATH。

### 8501 端口被占用

```powershell
streamlit run app.py --server.port 8502
```

### 上传大 Excel 很慢

系统会只选择 FB、TT 和第一个 GG，并按行尽早过滤项目/日期。首次解析 50MB 文件仍需要时间。先用内置样例文件验证环境。

### 页面显示旧结果

Public Sandbox 状态按浏览器 Session 隔离。刷新页面会保留当前 Session；关闭该会话后重新打开，或使用新的无痕窗口，可获得全新 Session。

### Google Ads 为什么不能修改

这是安全设计。Real Connector 只读，V1 只负责上线前核查，不负责启用、暂停或调预算。

### Docker 构建

```powershell
docker build -t marketing-ops-ai-agent .
docker run --rm -p 8501:8501 marketing-ops-ai-agent
```
