# private 私有模块使用说明

## 1. 目录定位

`private/` 用于放置本地私有文件，不应提交敏感实现或密钥。当前目录约定如下：

- `private/modules/`：私有扩展模块（自动动态加载，Dynamic Loading）
- `private/data/`：私有数据文件
- `private/logs/`：私有日志
- `private/reports/`：私有报告
- `private/tmp/`：临时文件

`private/.gitignore` 默认忽略绝大多数文件，仅保留必要占位和本说明文档。

## 2. 动态加载机制

系统通过 `src/core/private_module_loader.py` 动态加载可选私有模块。模块目录由环境变量控制：

- 默认目录：`private/modules`
- 可覆盖：`PRIVATE_MODULES_DIR`

示例（`.env`）：

```env
PRIVATE_MODULES_DIR=private/modules
# 也支持绝对路径，例如:
# PRIVATE_MODULES_DIR=D:/secure/dsa-private-modules
```

加载顺序（以类名为目标）：

1. 先按模块名 `import` 尝试加载
2. 再按文件路径加载（`PRIVATE_MODULES_DIR/<module>.py`）
3. 最后兼容旧路径（legacy path）

模块缺失时不会导致主流程崩溃，会降级并输出日志。

## 3. 当前支持的私有扩展

### 3.1 筹码计算模块 `chip_calculator.py`

- 目标类名：`ChipCalculator`
- 触发点：`data_provider/akshare_fetcher.py` 的本地筹码计算兜底
- 模块候选名：
  - `private.modules.chip_calculator`
  - `data_provider.chip_calculator`（兼容旧路径）
- 文件候选路径：
  - `<PRIVATE_MODULES_DIR>/chip_calculator.py`
  - `data_provider/chip_calculator.py`（兼容旧路径）

最小接口契约（Interface Contract）：

```python
class ChipCalculator:
    def calculate(self, df, code: str = "", calc_days: int = 90):
        """
        返回对象需包含字段：
        date, profit_ratio, avg_cost,
        cost_90_low, cost_90_high, concentration_90,
        cost_70_low, cost_70_high, concentration_70
        """
```

建议依赖：

- `pandas`
- `py_mini_racer`（若使用 JS 版筹码算法）

### 3.2 公众号草稿发布模块 `wechat_mp_publisher.py`

- 目标类名：`WechatMPPublisher`
- 触发点：`src/notification.py` 的微信公众号推送
- 模块候选名：
  - `private.modules.wechat_mp_publisher`
  - `wechat_mp_publisher`（兼容旧路径）
- 文件候选路径：
  - `<PRIVATE_MODULES_DIR>/wechat_mp_publisher.py`
  - `wechat_mp_publisher.py`（项目根目录兼容旧路径）

最小接口契约（Interface Contract）：

```python
class WechatMPPublisher:
    def __init__(self, appid: str, appsecret: str, cover_path=None, author: str = "AI 分析助手"):
        ...

    def publish(self, content: str, title=None) -> bool:
        ...
```

建议依赖：

- `requests`
- `markdown2`

## 4. 快速验证

### 4.1 验证类是否可加载

```bash
python -c "from src.core.private_module_loader import load_optional_class,build_private_file_candidates;print(bool(load_optional_class('ChipCalculator',('private.modules.chip_calculator','data_provider.chip_calculator'),build_private_file_candidates('chip_calculator',('data_provider/chip_calculator.py',)))))"
```

### 4.2 验证公众号模块是否可加载

```bash
python -c "from src.core.private_module_loader import load_optional_class,build_private_file_candidates;print(bool(load_optional_class('WechatMPPublisher',('private.modules.wechat_mp_publisher','wechat_mp_publisher'),build_private_file_candidates('wechat_mp_publisher',('wechat_mp_publisher.py',)))))"
```

输出 `True` 表示加载成功。

## 5. 常见问题

### 5.1 模块存在但未生效

检查项：

1. 文件名是否精确匹配：`chip_calculator.py` / `wechat_mp_publisher.py`
2. 类名是否精确匹配：`ChipCalculator` / `WechatMPPublisher`
3. `PRIVATE_MODULES_DIR` 是否指向正确目录
4. 依赖库是否已安装

### 5.2 运行中静默降级

私有模块加载失败时主流程会继续执行，但会在日志中提示。请优先检查：

- `logs/` 下应用日志
- 启动时的 `ERROR` / `WARNING` 信息

## 6. 同步上游后的合并指南（给 AI 看）

当从上游仓库同步代码后，如果调用点被覆盖，需要重新嫁接动态加载逻辑。

### 6.1 检查清单

1. **检查 `src/core/private_module_loader.py` 是否存在**
   - 如果被删除，需要从备份恢复

2. **检查 `src/notification.py` 的 `send_to_wechat_mp` 方法**
   - 应使用动态加载而非硬编码 import

3. **检查 `data_provider/akshare_fetcher.py` 的 `_get_chip_distribution_local` 方法**
   - 应使用动态加载而非硬编码 import

### 6.2 修改模式：微信公众号推送

如果 `src/notification.py` 被上游覆盖，按以下模式修改：

```python
# === 修改前（硬编码 import）===
from wechat_mp_publisher import WechatMPPublisher

# ... 在 send_to_wechat_mp 方法中 ...
publisher = WechatMPPublisher(appid=..., appsecret=...)
return publisher.publish(content, title)


# === 修改后（动态加载）===
# 在文件顶部添加 import
from src.core.private_module_loader import load_optional_class, build_private_file_candidates

# ... 在 send_to_wechat_mp 方法中 ...
publisher_class = load_optional_class(
    class_name="WechatMPPublisher",
    module_candidates=("private.modules.wechat_mp_publisher", "wechat_mp_publisher"),
    file_candidates=build_private_file_candidates(
        module_stem="wechat_mp_publisher",
        legacy_relative_paths=("wechat_mp_publisher.py",),
    ),
)
if publisher_class is None:
    logger.error("微信公众号模块未安装，请确保 private/modules/wechat_mp_publisher.py 存在")
    return False

publisher = publisher_class(appid=..., appsecret=...)
return publisher.publish(content, title)
```

### 6.3 修改模式：筹码分布本地计算

如果 `data_provider/akshare_fetcher.py` 被上游覆盖，按以下模式修改：

```python
# === 修改前（硬编码 import）===
from .chip_calculator import ChipCalculator

calculator = ChipCalculator()
result = calculator.calculate(df, code=stock_code)


# === 修改后（动态加载）===
# 在文件顶部添加 import
from src.core.private_module_loader import load_optional_class, build_private_file_candidates

# ... 在 _get_chip_distribution_local 方法中 ...
calculator_class = load_optional_class(
    class_name="ChipCalculator",
    module_candidates=("private.modules.chip_calculator", "data_provider.chip_calculator"),
    file_candidates=build_private_file_candidates(
        module_stem="chip_calculator",
        legacy_relative_paths=("data_provider/chip_calculator.py",),
    ),
)
if calculator_class is None:
    logger.warning(f"[筹码分布] {stock_code} 未找到 ChipCalculator 模块，跳过本地计算")
    return None

calculator = calculator_class()
result = calculator.calculate(df, code=stock_code)
```

### 6.4 添加新私有模块

1. 将模块文件放入 `private/modules/`
2. 在调用点使用 `load_optional_class()` 动态加载
3. 处理模块不存在时的降级逻辑（返回 None/False + 日志）
4. 更新本文档的"当前支持的私有扩展"章节

## 7. 安全建议

1. 不要把密钥硬编码到私有模块文件。
2. 私有模块中涉及网络调用时，建议设置超时与重试。
3. 若需团队共享私有模块，建议单独私有仓库存放，并通过 `PRIVATE_MODULES_DIR` 引用。
