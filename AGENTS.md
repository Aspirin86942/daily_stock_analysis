# Repository Guidelines

## 项目结构与模块组织
- `main.py` 为 CLI 入口，`webui.py` 为 WebUI 入口。
- `src/` 采用分层结构：
  - `src/domain/` 核心实体与枚举
  - `src/interfaces/` 接口协议 (Protocol)
  - `src/services/` 业务服务层
  - `src/infrastructure/` 外部集成与兼容层
  - `src/common/` 公共错误与工具
- 兼容层仍保留旧路径：`src/core/`、`src/notification.py`、`src/analyzer.py`。
- `data_provider/` 为行情数据源与标准化适配层。
- `bot/` 为机器人指令与平台适配器；`web/` 为 WebUI 服务端与页面资源。
- `docker/` 存放容器与编排配置；`docs/` 为用户与贡献文档。
- 运行产物：`data/`、`logs/`、`reports/`；本地素材 `assets/` 默认忽略提交。

## 构建、测试与开发命令
- `pip install -r requirements.txt`：安装依赖（Python 3.10+）。
- `cp .env.example .env`：创建本地配置并填入 API Key 与推送渠道。
- `python main.py`：运行完整分析流程。
- `python main.py --webui` / `--webui-only`：启动 WebUI（可选是否执行分析）。
- `python main.py --market-review`：仅大盘复盘。
- `python main.py --schedule`：定时模式。
- `docker-compose -f docker/docker-compose.yml up -d analyzer`：容器运行分析任务。

## 代码风格与命名规范
- 遵循 PEP 8，使用类型标注与 Google 风格 docstring。
- 格式化：`black .`、`isort .`（`setup.cfg` 中 line length=120）。
- 静态检查：`flake8 .`，规则见 `setup.cfg`。
- 日志统一用 `logging`，禁止裸 `except:`，异常需记录。
- 数据处理优先 pandas 矢量化，避免对大数据集使用 Python 循环。

## 测试指南
- `pytest -v`：执行测试，命名规范为 `test_*.py` 与 `test_*`。
- `./test.sh quick`：快速冒烟；`./test.sh all`：语法、lint 与场景测试。
- 需要网络或 API Key 的测试可单独运行并在 PR 中说明。

## 提交与 PR 规范
- 提交信息沿用 `feat:`、`chore:` 等前缀（参见 Git 历史）。
- 提交需聚焦单一目的，描述对行为的影响。
- PR 需包含：摘要、运行的测试命令（或未运行原因）、配置变更说明。
- 新增环境变量需同步更新 `.env.example` 与相关 `docs/`。

## 配置与安全提示
- 禁止提交密钥；本地配置仅写入 `.env`。
- 新增推送渠道或数据源时，补充文档与示例配置项。
