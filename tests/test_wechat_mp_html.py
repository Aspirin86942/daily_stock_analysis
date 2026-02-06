# -*- coding: utf-8 -*-
"""
===================================
微信公众号 HTML 转换测试
===================================

测试 Markdown → 微信公众号 HTML 转换功能。
验证修复效果：
- 空列表项移除
- 仅含列表符号的行移除
- <li><p>...</p></li> 归一化
"""

import re
import sys
from pathlib import Path
import pytest

# 确保可以导入 src 包
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.notify.wechat_mp import WechatMPDraftClient


class TestMarkdownToWechatMPHtml:
    """测试 Markdown → 微信公众号 HTML 转换"""

    @pytest.fixture
    def client(self):
        """创建测试用客户端（不需要真实凭证）"""
        return WechatMPDraftClient(appid="test_appid", appsecret="test_secret")

    def test_empty_list_item_removed(self, client):
        """空列表项应被移除"""
        md = "- item1\n- \n- item2"
        html = client.markdown_to_wechat_mp_html(md)
        # 不应包含空 <li></li>
        assert '<li></li>' not in html
        assert re.search(r'<li>\s*</li>', html) is None

    def test_bullet_only_line_removed(self, client):
        """仅包含列表符号的行应被移除"""
        md = "- item1\n-\n- item2"
        html = client.markdown_to_wechat_mp_html(md)
        # 应该只有 2 个 <li>
        li_count = html.count('<li')
        assert li_count == 2, f"Expected 2 <li>, got {li_count}"

    def test_li_p_normalized(self, client):
        """<li><p>...</p></li> 应归一为 <li>...</li>"""
        # markdown2 在某些情况下会生成 <li><p>...</p></li>
        md = "- item1\n\n- item2"
        html = client.markdown_to_wechat_mp_html(md)
        # 不应包含 <li><p> 结构
        assert '<li><p>' not in html
        # 但应该包含列表项内容
        assert 'item1' in html
        assert 'item2' in html

    def test_consecutive_empty_lines_collapsed(self, client):
        """连续空行应被合并"""
        md = "- item1\n\n\n\n- item2"
        html = client.markdown_to_wechat_mp_html(md)
        # 应该正常渲染
        assert 'item1' in html
        assert 'item2' in html

    def test_various_bullet_symbols(self, client):
        """各种列表符号的空行都应被移除"""
        md = "- item1\n* \n• \n- item2"
        html = client.markdown_to_wechat_mp_html(md)
        # 应该只有 2 个有效列表项
        li_count = html.count('<li')
        assert li_count == 2, f"Expected 2 <li>, got {li_count}"

    def test_inline_styles_applied(self, client):
        """内联样式应被正确应用"""
        md = "# Title\n\nParagraph text"
        html = client.markdown_to_wechat_mp_html(md)
        # 标题应有样式
        assert 'style=' in html
        assert 'font-size' in html

    def test_table_styles_applied(self, client):
        """表格样式应被正确应用"""
        md = "| Col1 | Col2 |\n|------|------|\n| A | B |"
        html = client.markdown_to_wechat_mp_html(md)
        # 表格应有样式
        assert 'border-collapse' in html

    def test_blockquote_styles_applied(self, client):
        """引用块样式应被正确应用"""
        md = "> This is a quote"
        html = client.markdown_to_wechat_mp_html(md)
        # 引用块应有样式
        assert 'border-left' in html

    def test_code_styles_applied(self, client):
        """代码块样式应被正确应用"""
        md = "Some `inline code` here"
        html = client.markdown_to_wechat_mp_html(md)
        # 代码应有样式
        assert 'Consolas' in html or 'monospace' in html

    def test_complex_markdown(self, client):
        """复杂 Markdown 文档应正确转换"""
        md = """# 决策仪表盘

## 股票分析

- 贵州茅台 (600519)
  - 评分: 85
  - 建议: 买入

### 风险提示

> 市场有风险，投资需谨慎

| 指标 | 数值 |
|------|------|
| MA5 | 1800 |
| MA10 | 1750 |
"""
        html = client.markdown_to_wechat_mp_html(md)
        # 应该包含所有内容
        assert '决策仪表盘' in html
        assert '贵州茅台' in html
        assert '风险提示' in html
        # 不应有空 <li>
        assert re.search(r'<li>\s*</li>', html) is None

    def test_no_empty_paragraphs(self, client):
        """不应生成空段落"""
        md = "Line 1\n\n\n\nLine 2"
        html = client.markdown_to_wechat_mp_html(md)
        # 不应包含空 <p>
        assert re.search(r'<p>\s*</p>', html) is None


class TestMarkdownToWechatMPHtmlEdgeCases:
    """边缘情况测试"""

    @pytest.fixture
    def client(self):
        return WechatMPDraftClient(appid="test_appid", appsecret="test_secret")

    def test_empty_input(self, client):
        """空输入应返回空字符串"""
        html = client.markdown_to_wechat_mp_html("")
        assert html == "" or html.strip() == ""

    def test_only_whitespace(self, client):
        """仅空白输入应正常处理"""
        html = client.markdown_to_wechat_mp_html("   \n\n   ")
        # 不应崩溃
        assert isinstance(html, str)

    def test_unicode_content(self, client):
        """Unicode 内容应正确处理"""
        md = "# 中文标题\n\n- 项目一 🎯\n- 项目二 ✅"
        html = client.markdown_to_wechat_mp_html(md)
        assert '中文标题' in html
        assert '🎯' in html
        assert '✅' in html

    def test_nested_lists(self, client):
        """嵌套列表应正确处理"""
        md = "- Level 1\n  - Level 2\n    - Level 3"
        html = client.markdown_to_wechat_mp_html(md)
        assert 'Level 1' in html
        # 不应有空 <li>
        assert re.search(r'<li>\s*</li>', html) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
