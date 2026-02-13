# -*- coding: utf-8 -*-
"""
===================================
ChipCalculator - 筹码分布本地计算模块
===================================

独立模块，可作为插件复用。

原理：
    筹码分布是根据历史 K 线数据（OHLC + 换手率）通过三角形分布算法计算的。
    本模块复用 akshare 的 JS 算法，支持任意 K 线数据源。

使用方法：
    from private.modules.chip_calculator import ChipCalculator, ChipResult

    # 方式1：传入 DataFrame
    calculator = ChipCalculator()
    result = calculator.calculate(df)  # df 需包含 date,open,close,high,low,volume,turnover_rate

    # 方式2：传入股票代码（自动获取数据）
    result = calculator.calculate_by_code('600519')

数据要求：
    DataFrame 必须包含以下列：
    - date: 日期
    - open: 开盘价
    - close: 收盘价
    - high: 最高价
    - low: 最低价
    - volume: 成交量（可选，用于计算换手率）
    - turnover_rate 或 hsl: 换手率（%），如 5.2 表示 5.2%

输出：
    ChipResult 对象，包含：
    - profit_ratio: 获利比例（0-1）
    - avg_cost: 平均成本
    - cost_90_low/high: 90% 筹码成本区间
    - cost_70_low/high: 70% 筹码成本区间
    - concentration_90/70: 筹码集中度

算法来源：
    东方财富网筹码分布算法（通过 akshare 逆向）
    https://quote.eastmoney.com/concept/sz000001.html
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ChipResult:
    """筹码分布计算结果"""
    code: str = ""
    date: str = ""
    profit_ratio: float = 0.0      # 获利比例 (0-1)
    avg_cost: float = 0.0          # 平均成本
    cost_90_low: float = 0.0       # 90% 筹码成本下限
    cost_90_high: float = 0.0      # 90% 筹码成本上限
    concentration_90: float = 0.0  # 90% 筹码集中度
    cost_70_low: float = 0.0       # 70% 筹码成本下限
    cost_70_high: float = 0.0      # 70% 筹码成本上限
    concentration_70: float = 0.0  # 70% 筹码集中度

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'date': self.date,
            'profit_ratio': self.profit_ratio,
            'avg_cost': self.avg_cost,
            'cost_90_low': self.cost_90_low,
            'cost_90_high': self.cost_90_high,
            'concentration_90': self.concentration_90,
            'cost_70_low': self.cost_70_low,
            'cost_70_high': self.cost_70_high,
            'concentration_70': self.concentration_70,
        }


# 筹码分布计算 JS 代码（来自东方财富，通过 akshare 逆向）
_CYQ_JS_CODE = """
// 筹码分布计算器
// @param {number} index 当前 K 线索引
// @param {Array} klinedata K 线数据数组
// @return {Object} 筹码分布结果

function CYQCalculator(index, klinedata) {
    var maxprice = 0;
    var minprice = 0;
    var factor = 150;  // 价格精度因子
    var start = this.range ? Math.max(0, index - this.range + 1) : 0;

    var kdata = klinedata.slice(start, Math.max(1, index + 1));
    if (kdata.length === 0) throw 'invalid index';

    // 计算价格区间
    for (var i = 0; i < kdata.length; i++) {
        var elements = kdata[i];
        maxprice = !maxprice ? elements.high : Math.max(maxprice, elements.high);
        minprice = !minprice ? elements.low : Math.min(minprice, elements.low);
    }

    // 精度不小于 0.01
    var accuracy = Math.max(0.01, (maxprice - minprice) / (factor - 1));

    // 价格值域
    var yrange = [];
    for (var i = 0; i < factor; i++) {
        yrange.push((minprice + accuracy * i).toFixed(2) / 1);
    }

    // 筹码分布数组
    var xdata = createNumberArray(factor);

    // 遍历 K 线计算筹码分布
    for (var i = 0; i < kdata.length; i++) {
        var eles = kdata[i];
        var open = eles.open,
            close = eles.close,
            high = eles.high,
            low = eles.low,
            avg = (open + close + high + low) / 4,
            turnoverRate = Math.min(1, eles.hsl / 100 || 0);

        var H = Math.floor((high - minprice) / accuracy),
            L = Math.ceil((low - minprice) / accuracy),
            GPoint = [high == low ? factor - 1 : 2 / (high - low), Math.floor((avg - minprice) / accuracy)];

        // 筹码衰减（换手导致旧筹码减少）
        for (var n = 0; n < xdata.length; n++) {
            xdata[n] *= (1 - turnoverRate);
        }

        // 三角形分布算法
        if (high == low) {
            // 一字板
            xdata[GPoint[1]] += GPoint[0] * turnoverRate / 2;
        } else {
            for (var j = L; j <= H; j++) {
                var curprice = minprice + accuracy * j;
                if (curprice <= avg) {
                    if (Math.abs(avg - low) < 1e-8) {
                        xdata[j] += GPoint[0] * turnoverRate;
                    } else {
                        xdata[j] += (curprice - low) / (avg - low) * GPoint[0] * turnoverRate;
                    }
                } else {
                    if (Math.abs(high - avg) < 1e-8) {
                        xdata[j] += GPoint[0] * turnoverRate;
                    } else {
                        xdata[j] += (high - curprice) / (high - avg) * GPoint[0] * turnoverRate;
                    }
                }
            }
        }
    }

    // 计算统计指标
    var currentprice = klinedata[index].close;
    var totalChips = 0;
    for (var i = 0; i < factor; i++) {
        var x = xdata[i].toPrecision(12) / 1;
        totalChips += x;
    }

    var result = new CYQData();
    result.x = xdata;
    result.y = yrange;
    result.benefitPart = result.getBenefitPart(currentprice);
    result.avgCost = getCostByChip(totalChips * 0.5).toFixed(2);
    result.percentChips = {
        '90': result.computePercentChips(0.9),
        '70': result.computePercentChips(0.7)
    };
    return result;

    // 获取指定筹码处的成本
    function getCostByChip(chip) {
        var result = 0, sum = 0;
        for (var i = 0; i < factor; i++) {
            var x = xdata[i].toPrecision(12) / 1;
            if (sum + x > chip) {
                result = minprice + i * accuracy;
                break;
            }
            sum += x;
        }
        return result;
    }

    // 筹码分布数据对象
    function CYQData() {
        this.x = arguments[0];
        this.y = arguments[1];
        this.benefitPart = arguments[2];
        this.avgCost = arguments[3];
        this.percentChips = arguments[4];

        this.computePercentChips = function(percent) {
            if (percent > 1 || percent < 0) throw 'argument "percent" out of range';
            var ps = [(1 - percent) / 2, (1 + percent) / 2];
            var pr = [getCostByChip(totalChips * ps[0]), getCostByChip(totalChips * ps[1])];
            return {
                priceRange: [pr[0].toFixed(2), pr[1].toFixed(2)],
                concentration: pr[0] + pr[1] === 0 ? 0 : (pr[1] - pr[0]) / (pr[0] + pr[1])
            };
        };

        this.getBenefitPart = function(price) {
            var below = 0;
            for (var i = 0; i < factor; i++) {
                var x = xdata[i].toPrecision(12) / 1;
                if (price >= minprice + i * accuracy) {
                    below += x;
                }
            }
            return totalChips == 0 ? 0 : below / totalChips;
        };
    }
}

function createNumberArray(count) {
    var array = [];
    for (var i = 0; i < count; i++) {
        array.push(0);
    }
    return array;
}
"""


class ChipCalculator:
    """
    筹码分布计算器

    支持两种使用方式：
    1. 传入 DataFrame 直接计算
    2. 传入股票代码自动获取数据后计算
    """

    def __init__(self, data_fetcher=None):
        """
        初始化计算器

        Args:
            data_fetcher: 数据获取器，需实现 get_daily_data(code, days) 方法
                         如果不传，calculate_by_code 将尝试自动创建
        """
        self._js_context = None
        self._data_fetcher = data_fetcher

    def _get_js_context(self):
        """延迟加载 JS 执行环境"""
        if self._js_context is None:
            try:
                import py_mini_racer
                self._js_context = py_mini_racer.MiniRacer()
                self._js_context.eval(_CYQ_JS_CODE)
                logger.debug("[ChipCalculator] JS 执行环境初始化成功")
            except ImportError:
                raise ImportError(
                    "筹码分布计算需要 py_mini_racer 库，请安装: pip install py_mini_racer"
                )
        return self._js_context

    def _get_data_fetcher(self):
        """延迟加载数据获取器"""
        if self._data_fetcher is None:
            try:
                from data_provider.base import DataFetcherManager
                self._data_fetcher = DataFetcherManager()
                logger.debug("[ChipCalculator] 数据获取器初始化成功")
            except ImportError:
                raise ImportError(
                    "自动获取数据需要 DataFetcherManager，请手动传入 DataFrame"
                )
        return self._data_fetcher

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        准备 DataFrame，标准化列名并添加换手率

        Args:
            df: 原始 DataFrame

        Returns:
            标准化后的 DataFrame
        """
        df = df.copy()

        # 标准化列名映射
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '换手率': 'hsl',
            'turnover_rate': 'hsl',
            'pct_chg': 'zdf',
            '涨跌幅': 'zdf',
        }

        df.rename(columns=column_mapping, inplace=True)

        # 确保必要列存在
        required_cols = ['date', 'open', 'close', 'high', 'low']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"DataFrame 缺少必要列: {missing}")

        # 确保换手率列存在
        if 'hsl' not in df.columns:
            # 尝试从成交量估算换手率（假设流通股本，这里用默认值）
            logger.warning("[ChipCalculator] 未找到换手率列，使用默认值 1%")
            df['hsl'] = 1.0

        # 转换数值类型
        for col in ['open', 'close', 'high', 'low', 'hsl']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 转换日期为字符串（避免 JSON 序列化问题）
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)

        # 填充缺失的换手率
        df['hsl'] = df['hsl'].fillna(1.0)

        # 添加索引列
        df = df.reset_index(drop=True)
        df['index'] = range(len(df))

        return df

    def calculate(
        self,
        df: pd.DataFrame,
        code: str = "",
        calc_days: int = 90
    ) -> Optional[ChipResult]:
        """
        根据 K 线数据计算筹码分布

        Args:
            df: K 线数据 DataFrame
            code: 股票代码（可选，用于结果标识）
            calc_days: 计算最近 N 天的筹码（默认 90 天）

        Returns:
            ChipResult 对象，计算失败返回 None
        """
        try:
            # 准备数据
            df = self._prepare_dataframe(df)

            if len(df) < 10:
                logger.warning(f"[ChipCalculator] 数据不足 10 条，无法计算筹码分布")
                return None

            # 只取最近 calc_days 天
            if len(df) > calc_days:
                df = df.tail(calc_days).reset_index(drop=True)
                df['index'] = range(len(df))

            # 转换为 JS 需要的格式
            records = df.to_dict(orient='records')

            # 获取 JS 执行环境
            js_ctx = self._get_js_context()

            # 计算最后一天的筹码分布
            last_index = len(records) - 1
            result = js_ctx.call("CYQCalculator", last_index, records)

            # 解析结果
            chip = ChipResult(
                code=code,
                date=str(records[last_index].get('date', '')),
                profit_ratio=float(result.get('benefitPart', 0)),
                avg_cost=float(result.get('avgCost', 0)),
                cost_90_low=float(result['percentChips']['90']['priceRange'][0]),
                cost_90_high=float(result['percentChips']['90']['priceRange'][1]),
                concentration_90=float(result['percentChips']['90']['concentration']),
                cost_70_low=float(result['percentChips']['70']['priceRange'][0]),
                cost_70_high=float(result['percentChips']['70']['priceRange'][1]),
                concentration_70=float(result['percentChips']['70']['concentration']),
            )

            logger.info(
                f"[ChipCalculator] {code} 日期={chip.date}: "
                f"获利比例={chip.profit_ratio:.1%}, 平均成本={chip.avg_cost}, "
                f"90%集中度={chip.concentration_90:.2%}"
            )

            return chip

        except Exception as e:
            logger.error(f"[ChipCalculator] 计算筹码分布失败: {e}")
            return None

    def calculate_by_code(
        self,
        stock_code: str,
        days: int = 210,
        calc_days: int = 90
    ) -> Optional[ChipResult]:
        """
        根据股票代码获取数据并计算筹码分布

        Args:
            stock_code: 股票代码
            days: 获取历史数据天数（默认 210 天，约 1 年交易日）
            calc_days: 计算最近 N 天的筹码（默认 90 天）

        Returns:
            ChipResult 对象，计算失败返回 None
        """
        try:
            fetcher = self._get_data_fetcher()

            logger.info(f"[ChipCalculator] 获取 {stock_code} 历史数据...")
            df, source = fetcher.get_daily_data(stock_code, days=days)

            if df is None or df.empty:
                logger.warning(f"[ChipCalculator] {stock_code} 获取数据失败")
                return None

            logger.info(f"[ChipCalculator] {stock_code} 获取到 {len(df)} 条数据 (来源: {source})")

            return self.calculate(df, code=stock_code, calc_days=calc_days)

        except Exception as e:
            logger.error(f"[ChipCalculator] {stock_code} 计算失败: {e}")
            return None

    def calculate_batch(
        self,
        stock_codes: List[str],
        days: int = 210,
        calc_days: int = 90
    ) -> Dict[str, Optional[ChipResult]]:
        """
        批量计算多只股票的筹码分布

        Args:
            stock_codes: 股票代码列表
            days: 获取历史数据天数
            calc_days: 计算最近 N 天的筹码

        Returns:
            {股票代码: ChipResult} 字典
        """
        results = {}
        for code in stock_codes:
            results[code] = self.calculate_by_code(code, days=days, calc_days=calc_days)
        return results


# 便捷函数
def calculate_chip_distribution(
    stock_code: str = None,
    df: pd.DataFrame = None,
    days: int = 210
) -> Optional[ChipResult]:
    """
    计算筹码分布的便捷函数

    Args:
        stock_code: 股票代码（与 df 二选一）
        df: K 线数据 DataFrame（与 stock_code 二选一）
        days: 获取历史数据天数（仅 stock_code 模式有效）

    Returns:
        ChipResult 对象

    Examples:
        # 方式1：传入股票代码
        result = calculate_chip_distribution(stock_code='600519')

        # 方式2：传入 DataFrame
        result = calculate_chip_distribution(df=my_dataframe)
    """
    calculator = ChipCalculator()

    if stock_code:
        return calculator.calculate_by_code(stock_code, days=days)
    elif df is not None:
        return calculator.calculate(df)
    else:
        raise ValueError("必须提供 stock_code 或 df 参数")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 测试计算
    result = calculate_chip_distribution(stock_code='600519')
    if result:
        print(f"\n筹码分布结果:")
        print(f"  股票代码: {result.code}")
        print(f"  日期: {result.date}")
        print(f"  获利比例: {result.profit_ratio:.1%}")
        print(f"  平均成本: {result.avg_cost}")
        print(f"  90%筹码区间: {result.cost_90_low} - {result.cost_90_high}")
        print(f"  90%集中度: {result.concentration_90:.2%}")
        print(f"  70%筹码区间: {result.cost_70_low} - {result.cost_70_high}")
        print(f"  70%集中度: {result.concentration_70:.2%}")
