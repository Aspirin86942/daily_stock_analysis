# -*- coding: utf-8 -*-
"""
===================================
股票实体定义
===================================

包含：
- StockCode: 股票代码值对象（含市场识别逻辑）
- StockInfo: 股票基本信息数据类
- STANDARD_COLUMNS: 标准化列名定义
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# === 标准化列名定义（从 data_provider/base.py 提取）===
STANDARD_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']


class Market(Enum):
    """市场类型枚举"""
    A_SHARE_SH = "sh"      # A股上海
    A_SHARE_SZ = "sz"      # A股深圳
    A_SHARE_BJ = "bj"      # A股北交所
    HK = "hk"              # 港股
    US = "us"              # 美股
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StockCode:
    """
    股票代码值对象

    设计原则：
    - 不可变（frozen=True）
    - 封装市场识别逻辑
    - 提供标准化格式转换

    使用示例：
        code = StockCode("600519")
        print(code.market)  # Market.A_SHARE_SH
        print(code.with_prefix)  # "sh600519"
    """
    raw: str  # 原始代码

    @property
    def normalized(self) -> str:
        """标准化代码（去除前缀、空格）"""
        code = self.raw.strip().upper()
        # 移除常见前缀
        for prefix in ['SH', 'SZ', 'BJ', 'HK', 'US', '.SS', '.SZ', '.HK']:
            if code.startswith(prefix):
                code = code[len(prefix):]
            if code.endswith(prefix):
                code = code[:-len(prefix)]
        return code

    @property
    def market(self) -> Market:
        """识别市场类型"""
        code = self.normalized

        # A股：6位数字
        if re.match(r'^\d{6}$', code):
            if code.startswith('6'):
                return Market.A_SHARE_SH
            elif code.startswith(('0', '3')):
                return Market.A_SHARE_SZ
            elif code.startswith(('4', '8')):
                return Market.A_SHARE_BJ

        # 港股：5位数字
        if re.match(r'^\d{5}$', code):
            return Market.HK

        # 美股：纯字母
        if re.match(r'^[A-Z]+$', code):
            return Market.US

        return Market.UNKNOWN

    @property
    def with_prefix(self) -> str:
        """带市场前缀的代码"""
        market = self.market
        code = self.normalized

        if market == Market.A_SHARE_SH:
            return f"sh{code}"
        elif market == Market.A_SHARE_SZ:
            return f"sz{code}"
        elif market == Market.A_SHARE_BJ:
            return f"bj{code}"
        elif market == Market.HK:
            return f"hk{code}"
        elif market == Market.US:
            return code  # 美股不加前缀
        return code

    @property
    def is_a_share(self) -> bool:
        """是否为 A 股"""
        return self.market in (Market.A_SHARE_SH, Market.A_SHARE_SZ, Market.A_SHARE_BJ)

    @property
    def is_hk(self) -> bool:
        """是否为港股"""
        return self.market == Market.HK

    @property
    def is_us(self) -> bool:
        """是否为美股"""
        return self.market == Market.US

    def __str__(self) -> str:
        return self.normalized

    def __eq__(self, other) -> bool:
        if isinstance(other, StockCode):
            return self.normalized == other.normalized
        if isinstance(other, str):
            return self.normalized == StockCode(other).normalized
        return False

    def __hash__(self) -> int:
        return hash(self.normalized)


@dataclass
class StockInfo:
    """
    股票基本信息

    用于存储股票的静态信息（代码、名称、行业等）
    """
    code: str
    name: str = ""
    industry: str = ""           # 所属行业
    sector: str = ""             # 所属板块
    list_date: Optional[str] = None  # 上市日期

    @property
    def stock_code(self) -> StockCode:
        """获取 StockCode 值对象"""
        return StockCode(self.code)

    @property
    def market(self) -> Market:
        """获取市场类型"""
        return self.stock_code.market

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'code': self.code,
            'name': self.name,
            'industry': self.industry,
            'sector': self.sector,
            'list_date': self.list_date,
            'market': self.market.value,
        }


# 股票名称映射（常见股票，从 analyzer.py 提取）
STOCK_NAME_MAP = {
    # === A股 ===
    '600519': '贵州茅台',
    '000001': '平安银行',
    '300750': '宁德时代',
    '002594': '比亚迪',
    '600036': '招商银行',
    '601318': '中国平安',
    '000858': '五粮液',
    '600276': '恒瑞医药',
    '601012': '隆基绿能',
    '002475': '立讯精密',
    '300059': '东方财富',
    '002415': '海康威视',
    '600900': '长江电力',
    '601166': '兴业银行',
    '600028': '中国石化',

    # === 美股 ===
    'AAPL': '苹果',
    'TSLA': '特斯拉',
    'MSFT': '微软',
    'GOOGL': '谷歌A',
    'GOOG': '谷歌C',
    'AMZN': '亚马逊',
    'NVDA': '英伟达',
    'META': 'Meta',
    'AMD': 'AMD',
    'INTC': '英特尔',
    'BABA': '阿里巴巴',
    'PDD': '拼多多',
    'JD': '京东',
    'BIDU': '百度',
    'NIO': '蔚来',
    'XPEV': '小鹏汽车',
    'LI': '理想汽车',
    'COIN': 'Coinbase',
    'MSTR': 'MicroStrategy',

    # === 港股 (5位数字) ===
    '00700': '腾讯控股',
    '03690': '美团',
    '01810': '小米集团',
    '09988': '阿里巴巴',
    '09618': '京东集团',
    '09888': '百度集团',
    '01024': '快手',
    '00981': '中芯国际',
    '02015': '理想汽车',
    '09868': '小鹏汽车',
    '00005': '汇丰控股',
    '01299': '友邦保险',
    '00941': '中国移动',
    '00883': '中国海洋石油',
}


def get_stock_name(code: str) -> str:
    """
    获取股票名称

    Args:
        code: 股票代码

    Returns:
        股票名称，未找到则返回代码本身
    """
    normalized = StockCode(code).normalized
    return STOCK_NAME_MAP.get(normalized, normalized)
