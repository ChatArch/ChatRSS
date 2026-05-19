"""chatenv 配置。"""
from chatenv import BaseEnvConfig, EnvField


class ChatRssConfig(BaseEnvConfig):
    _title = "ChatRSS Configuration"
    _aliases = ["chatrss", "rss"]
    _storage_dir = "ChatRss"

    CHATRSS_DEFAULT_REPO = EnvField("CHATRSS_DEFAULT_REPO", desc="默认监听仓库（owner/name）")
    CHATRSS_RSSHUB_URL = EnvField("CHATRSS_RSSHUB_URL", desc="RSSHub 实例地址，默认 http://localhost:1200")
    CHATRSS_LARK_USER_ID = EnvField("CHATRSS_LARK_USER_ID", desc="飞书消息接收用户 open_id")
    CHATRSS_LARK_DOC_TOKEN = EnvField("CHATRSS_LARK_DOC_TOKEN", desc="飞书文档 token（状态追踪文档）")


__all__ = ["ChatRssConfig"]
