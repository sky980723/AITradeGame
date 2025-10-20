# Repository Guidelines

## 项目结构与模块组织
`app.py` 是 Flask 入口与路由分发中心，交易循环委托给 `trading_engine.py`，市场数据逻辑在 `market_data.py`，AI 调用由 `ai_trader.py` 负责，持久化交给 `database.py`。前端静态资源位于 `static/`，模板位于 `templates/`。本地配置可复制 `config.example.py` 为 `config.py` 或以环境变量提供。`Dockerfile` 与 `docker-compose.yml` 支持容器部署，并将 `data/` 目录挂载为 SQLite 数据持久层。

## 构建、测试与开发命令
- `python -m venv .venv` 与 `.venv\Scripts\activate`（PowerShell）隔离依赖。
- `pip install -r requirements.txt` 安装 Flask、CORS、requests 与 OpenAI 客户端。
- `python app.py` 在 `http://localhost:5000` 启动开发服务器；Windows 可直接运行 `run.bat`。
- `docker compose up --build` 在容器中启动应用，交易数据库保存在 `data/trading_bot.db`。

## 代码风格与命名规范
默认遵循 PEP 8：四空格缩进、为非 trivial 函数编写 docstring、模块与函数使用 snake_case，类名保持 PascalCase（如 `TradingEngine`）。日志请延续现有方括号标签（`[INFO]`、`[ERROR]`），便于命令行与容器日志检索。

## 测试指引
仓库尚未内置自动化测试，新增功能时优先补充 `tests/test_<module>.py` 并使用 `pytest`。对外部 API（OpenAI、CoinGecko）进行 mock，确保测试可重复。若仍需手动验证，请在 PR 描述记录执行步骤（例如 `curl http://localhost:5000/api/market/prices`）以及所需的数据库迁移或初始化数据。

## 提交与拉取请求规范
提交信息参考历史惯例，使用简洁的现在时（如 `Update README.md`），并控制主题行不超过 72 个字符。每个 PR 需按需更新 `CHANGELOG.md` 与 `README.md`，说明核心改动、关联 Issue，并提供测试证据或界面截图。若涉及配置变更（新增环境变量、数据库结构调整），请在描述中明确提醒。

## 配置与安全提示
禁止提交真实 API Key 或 SQLite 数据文件，可通过 `.env` 或未跟踪的 `config.py` 管理敏感信息。使用 Docker 时，在推送前检查 `data/` 目录内容。若演示暴露了密钥，应立即更换，并在脚本中优先使用环境变量（如 `OPENAI_API_KEY`、`OPENAI_BASE_URL`）进行覆盖。
