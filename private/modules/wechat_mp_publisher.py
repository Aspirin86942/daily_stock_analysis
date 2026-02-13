"""
微信公众号草稿箱发布模块（独立版）

功能：
- 将 Markdown 内容转换为微信公众号兼容的 HTML
- 上传封面图（永久素材，带缓存）
- 创建草稿到公众号后台

使用方式：
    from private.modules.wechat_mp_publisher import publish_to_wechat_mp

    success = publish_to_wechat_mp(
        content="# 标题\n\n正文内容",
        appid="your_appid",
        appsecret="your_appsecret",
        title="文章标题"
    )

依赖：
    pip install requests markdown2

注意事项：
    1. 需要在微信公众号后台配置 IP 白名单
    2. 封面图建议尺寸 900x500 像素
    3. 永久素材有数量限制（图片 5000 个），模块内置缓存避免重复上传
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Dict, Optional

import markdown2
import requests

logger = logging.getLogger(__name__)


class WechatMPDraftClient:
    """
    微信公众号草稿箱客户端

    功能：
    1. 获取 access_token（带缓存，2小时有效期）
    2. 上传封面图（永久素材）
    3. 创建草稿

    使用流程：
    1. 在公众号后台获取 AppID 和 AppSecret
    2. 将运行脚本的 IP 添加到公众号后台的 IP 白名单
    3. 准备封面图（建议 900x500 像素）
    """

    # 微信 API 基础 URL
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, appid: str, appsecret: str):
        """
        初始化客户端

        Args:
            appid: 公众号 AppID
            appsecret: 公众号 AppSecret
        """
        self.appid = appid
        self.appsecret = appsecret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        # 缓存封面图 media_id，避免重复上传
        self._cover_media_id_cache: Dict[str, str] = {}

    def get_access_token(self) -> Optional[str]:
        """
        获取 access_token（带缓存，2小时有效期）

        微信 access_token 有效期为 7200 秒（2小时），
        这里提前 5 分钟刷新以避免边界问题。

        Returns:
            access_token 或 None（如果获取失败）
        """
        # 检查缓存是否有效（提前 5 分钟刷新）
        if self._access_token and time.time() < self._token_expires_at - 300:
            return self._access_token

        try:
            url = f"{self.BASE_URL}/token"
            params = {
                "grant_type": "client_credential",
                "appid": self.appid,
                "secret": self.appsecret,
            }

            response = requests.get(url, params=params, timeout=10)
            result = response.json()

            if "access_token" in result:
                self._access_token = result["access_token"]
                expires_in = result.get("expires_in", 7200)
                self._token_expires_at = time.time() + expires_in
                logger.info(f"微信公众号 access_token 获取成功，有效期 {expires_in} 秒")
                return self._access_token
            else:
                errcode = result.get("errcode", "unknown")
                errmsg = result.get("errmsg", "未知错误")
                logger.error(f"获取 access_token 失败: [{errcode}] {errmsg}")
                return None

        except Exception as e:
            logger.error(f"获取 access_token 异常: {e}")
            return None

    def upload_cover_image(self, image_path: str) -> Optional[str]:
        """
        上传封面图（永久素材）

        微信公众号图文消息需要封面图，封面图需要先上传到微信服务器获取 media_id。
        永久素材不会过期，但有数量限制（图片 5000 个）。

        Args:
            image_path: 图片文件路径

        Returns:
            media_id 或 None（如果上传失败）
        """
        # 检查缓存
        abs_path = os.path.abspath(image_path)
        if abs_path in self._cover_media_id_cache:
            logger.info(f"使用缓存的封面图 media_id: {self._cover_media_id_cache[abs_path][:20]}...")
            return self._cover_media_id_cache[abs_path]

        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"封面图文件不存在: {image_path}")
            return None

        access_token = self.get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.BASE_URL}/material/add_material"
            params = {"access_token": access_token, "type": "image"}

            # 读取图片文件
            with open(image_path, "rb") as f:
                files = {"media": (os.path.basename(image_path), f, "image/jpeg")}
                response = requests.post(url, params=params, files=files, timeout=30)

            result = response.json()

            if "media_id" in result:
                media_id = result["media_id"]
                # 缓存 media_id
                self._cover_media_id_cache[abs_path] = media_id
                logger.info(f"封面图上传成功，media_id: {media_id[:20]}...")
                return media_id
            else:
                errcode = result.get("errcode", "unknown")
                errmsg = result.get("errmsg", "未知错误")
                logger.error(f"上传封面图失败: [{errcode}] {errmsg}")
                return None

        except Exception as e:
            logger.error(f"上传封面图异常: {e}")
            return None

    def add_draft(
        self,
        title: str,
        content: str,
        thumb_media_id: str,
        author: str = "",
        digest: str = "",
    ) -> Optional[str]:
        """
        创建草稿

        Args:
            title: 文章标题
            content: 文章内容（HTML 格式）
            thumb_media_id: 封面图 media_id
            author: 作者（可选）
            digest: 摘要（可选，不填则自动截取正文前 54 字）

        Returns:
            草稿 media_id 或 None（如果创建失败）
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.BASE_URL}/draft/add"
            params = {"access_token": access_token}

            # 构建文章数据
            article = {
                "title": title,
                "author": author,
                "digest": digest[:120] if digest else "",  # 摘要最多 120 字
                "content": content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,  # 不开启评论
                "only_fans_can_comment": 0,
            }

            payload = {"articles": [article]}

            # 调试：记录内容长度
            content_length = len(content)
            logger.debug(f"草稿内容长度: {content_length} 字符")
            if content_length > 20000:
                logger.warning(f"内容过长 ({content_length} 字符)，可能导致创建失败")

            response = requests.post(
                url,
                params=params,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30,
            )

            result = response.json()

            if "media_id" in result:
                media_id = result["media_id"]
                logger.info(f"草稿创建成功，media_id: {media_id}")
                return media_id
            else:
                errcode = result.get("errcode", "unknown")
                errmsg = result.get("errmsg", "未知错误")
                logger.error(f"创建草稿失败: [{errcode}] {errmsg}")
                return None

        except Exception as e:
            logger.error(f"创建草稿异常: {e}")
            return None


class WechatMPPublisher:
    """
    微信公众号发布器

    封装完整的发布流程：Markdown 转 HTML、封面图轮换、创建草稿
    """

    def __init__(
        self,
        appid: str,
        appsecret: str,
        cover_path: Optional[str] = None,
        assets_dir: str = "assets",
        author: str = "AI 分析助手",
    ):
        """
        初始化发布器

        Args:
            appid: 公众号 AppID
            appsecret: 公众号 AppSecret
            cover_path: 指定封面图路径（可选，优先级最高）
            assets_dir: 封面图目录（用于周几轮换）
            author: 文章作者
        """
        self._client = WechatMPDraftClient(appid, appsecret)
        self._cover_path = cover_path
        self._assets_dir = assets_dir
        self._author = author

    def publish(self, content: str, title: Optional[str] = None) -> bool:
        """
        发布 Markdown 内容到微信公众号草稿箱

        Args:
            content: Markdown 格式内容
            title: 文章标题（默认自动生成带日期的标题）

        Returns:
            是否创建成功
        """
        # 生成标题
        if title is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            title = f"股票分析报告 - {date_str}"

        try:
            # 获取封面图 media_id
            thumb_media_id = self._get_cover_media_id()
            if not thumb_media_id:
                logger.error("无法获取封面图 media_id，请配置封面图路径或放置默认封面图")
                return False

            # 转换 Markdown 为微信公众号兼容的 HTML
            html_content = self._markdown_to_wechat_mp_html(content)

            # 生成摘要（取正文前 100 字）
            plain_text = self._markdown_to_plain_text(content)
            digest = plain_text[:100].replace("\n", " ").strip()

            # 创建草稿
            media_id = self._client.add_draft(
                title=title,
                content=html_content,
                thumb_media_id=thumb_media_id,
                author=self._author,
                digest=digest,
            )

            if media_id:
                logger.info("微信公众号草稿创建成功，请登录公众号后台手动发布")
                return True
            else:
                logger.error("微信公众号草稿创建失败")
                return False

        except Exception as e:
            logger.error(f"发送微信公众号草稿失败: {e}")
            return False

    def _get_cover_media_id(self) -> Optional[str]:
        """获取封面图 media_id，支持指定路径和周几轮换"""
        # 优先使用指定的封面图
        if self._cover_path:
            media_id = self._client.upload_cover_image(self._cover_path)
            if media_id:
                return media_id
            logger.warning("指定封面图上传失败，尝试使用轮换封面")

        # 根据星期几选择封面图（周一=cover.jpg，周二~周五=cover01~04.jpg）
        weekday = datetime.now().weekday()
        weekday_cover_map = {
            0: "cover.jpg",      # 周一
            1: "cover01.jpg",    # 周二
            2: "cover02.jpg",    # 周三
            3: "cover03.jpg",    # 周四
            4: "cover04.jpg",    # 周五
        }
        weekday_cover = weekday_cover_map.get(weekday, "cover.jpg")

        # 候选封面图列表
        cover_candidates = [
            os.path.join(self._assets_dir, weekday_cover),
            os.path.join(self._assets_dir, "cover.jpg"),
            os.path.join(self._assets_dir, "default_cover.jpg"),
        ]

        for cover_path in cover_candidates:
            if os.path.exists(cover_path):
                media_id = self._client.upload_cover_image(cover_path)
                if media_id:
                    logger.info(f"使用封面图: {cover_path}")
                    return media_id

        return None

    def _markdown_to_wechat_mp_html(self, markdown_text: str) -> str:
        """
        将 Markdown 转换为微信公众号兼容的 HTML

        微信公众号对 HTML 有严格限制：
        1. 不支持外部 CSS 文件，只能使用内联样式
        2. 不支持 JavaScript
        3. 图片必须使用微信服务器 URL
        4. 部分 CSS 属性不支持
        """
        # 使用 markdown2 转换
        html_content = markdown2.markdown(
            markdown_text,
            extras=["tables", "fenced-code-blocks", "break-on-newline", "cuddled-lists"],
        )

        # 微信公众号兼容的内联样式
        styled_html = html_content

        # 替换标题样式
        styled_html = re.sub(
            r"<h1>(.*?)</h1>",
            r'<h1 style="font-size: 22px; color: #333; border-bottom: 2px solid #07c160; padding-bottom: 8px; margin: 20px 0 15px 0;">\1</h1>',
            styled_html,
        )
        styled_html = re.sub(
            r"<h2>(.*?)</h2>",
            r'<h2 style="font-size: 18px; color: #333; border-bottom: 1px solid #eee; padding-bottom: 6px; margin: 18px 0 12px 0;">\1</h2>',
            styled_html,
        )
        styled_html = re.sub(
            r"<h3>(.*?)</h3>",
            r'<h3 style="font-size: 16px; color: #333; margin: 15px 0 10px 0;">\1</h3>',
            styled_html,
        )

        # 替换段落样式
        styled_html = re.sub(
            r"<p>(.*?)</p>",
            r'<p style="font-size: 15px; color: #333; line-height: 1.8; margin: 10px 0;">\1</p>',
            styled_html,
            flags=re.DOTALL,
        )

        # 替换表格样式
        styled_html = re.sub(
            r"<table>",
            r'<table style="width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px;">',
            styled_html,
        )
        styled_html = re.sub(
            r"<th>(.*?)</th>",
            r'<th style="background-color: #f6f8fa; border: 1px solid #ddd; padding: 8px 12px; text-align: left; font-weight: bold;">\1</th>',
            styled_html,
        )
        styled_html = re.sub(
            r"<td>(.*?)</td>",
            r'<td style="border: 1px solid #ddd; padding: 8px 12px;">\1</td>',
            styled_html,
        )

        # 替换引用块样式
        styled_html = re.sub(
            r"<blockquote>(.*?)</blockquote>",
            r'<blockquote style="border-left: 4px solid #07c160; padding: 10px 15px; margin: 15px 0; background-color: #f9f9f9; color: #666;">\1</blockquote>',
            styled_html,
            flags=re.DOTALL,
        )

        # 替换代码块样式
        styled_html = re.sub(
            r"<code>(.*?)</code>",
            r'<code style="background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; font-size: 14px;">\1</code>',
            styled_html,
        )

        # 替换列表样式
        styled_html = re.sub(
            r"<ul>",
            r'<ul style="padding-left: 20px; margin: 10px 0;">',
            styled_html,
        )
        styled_html = re.sub(
            r"<ol>",
            r'<ol style="padding-left: 20px; margin: 10px 0;">',
            styled_html,
        )
        styled_html = re.sub(
            r"<li>(.*?)</li>",
            r'<li style="margin: 5px 0; line-height: 1.6;">\1</li>',
            styled_html,
        )

        # 替换分隔线样式
        styled_html = re.sub(
            r"<hr\s*/?>",
            r'<hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">',
            styled_html,
        )

        # 替换加粗样式
        styled_html = re.sub(
            r"<strong>(.*?)</strong>",
            r'<strong style="color: #333;">\1</strong>',
            styled_html,
        )

        return styled_html

    def _markdown_to_plain_text(self, markdown_text: str) -> str:
        """将 Markdown 转换为纯文本，用于生成摘要"""
        text = markdown_text

        # 移除标题标记 # ## ###
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

        # 移除加粗 **text** -> text
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)

        # 移除斜体 *text* -> text
        text = re.sub(r"\*(.+?)\*", r"\1", text)

        # 移除引用 > text -> text
        text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)

        # 移除列表标记 - item -> item
        text = re.sub(r"^[-*]\s+", "• ", text, flags=re.MULTILINE)

        # 移除分隔线 ---
        text = re.sub(r"^---+$", "────────", text, flags=re.MULTILINE)

        # 移除表格语法 |---|---|
        text = re.sub(r"\|[-:]+\|[-:|\s]+\|", "", text)
        text = re.sub(r"^\|(.+)\|$", r"\1", text, flags=re.MULTILINE)

        # 清理多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()


def publish_to_wechat_mp(
    content: str,
    appid: str,
    appsecret: str,
    title: Optional[str] = None,
    cover_path: Optional[str] = None,
    assets_dir: str = "assets",
    author: str = "AI 分析助手",
) -> bool:
    """
    一行调用发布到微信公众号草稿箱

    Args:
        content: Markdown 格式内容
        appid: 公众号 AppID
        appsecret: 公众号 AppSecret
        title: 文章标题（默认自动生成带日期的标题）
        cover_path: 指定封面图路径（可选）
        assets_dir: 封面图目录（用于周几轮换，默认 "assets"）
        author: 文章作者（默认 "AI 分析助手"）

    Returns:
        是否创建成功

    Example:
        >>> from private.modules.wechat_mp_publisher import publish_to_wechat_mp
        >>> success = publish_to_wechat_mp(
        ...     content="# 标题\\n\\n正文内容",
        ...     appid="your_appid",
        ...     appsecret="your_appsecret"
        ... )
    """
    publisher = WechatMPPublisher(
        appid=appid,
        appsecret=appsecret,
        cover_path=cover_path,
        assets_dir=assets_dir,
        author=author,
    )
    return publisher.publish(content, title)


# 模块自测试
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # 从环境变量读取配置
    appid = os.getenv("WECHAT_MP_APPID")
    appsecret = os.getenv("WECHAT_MP_APPSECRET")

    if not appid or not appsecret:
        print("请设置环境变量 WECHAT_MP_APPID 和 WECHAT_MP_APPSECRET")
        sys.exit(1)

    test_content = """# 测试标题

这是一段测试内容。

## 功能特性

- 支持 Markdown 转换
- 支持封面图轮换
- 支持 access_token 缓存

> 这是一段引用

| 列1 | 列2 |
|-----|-----|
| A   | B   |
"""

    success = publish_to_wechat_mp(
        content=test_content,
        appid=appid,
        appsecret=appsecret,
        title="测试文章",
    )

    print("发布成功" if success else "发布失败")
    sys.exit(0 if success else 1)
