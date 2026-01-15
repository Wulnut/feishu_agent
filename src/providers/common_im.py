"""
IM Provider - 飞书 IM 消息发送提供者

负责封装飞书 IM 相关的 API 调用。
"""

import logging
from typing import Optional

from src.providers.base import Provider
from src.core.client import get_lark_client

logger = logging.getLogger(__name__)


class IMProvider(Provider):
    """
    飞书 IM 消息发送提供者

    封装飞书 IM SDK 的调用，提供发送文本消息等功能。

    注意：需要配置 LARK_APP_ID 和 LARK_APP_SECRET 环境变量。
    """

    def __init__(self):
        """
        初始化 IM Provider

        延迟获取 Lark 客户端，避免在对象实例化时抛出异常。
        """
        self._client = None

    @property
    def client(self):
        """延迟获取 Lark 客户端"""
        if self._client is None:
            self._client = get_lark_client()
        return self._client

    async def send_text(
        self,
        receive_id_type: str,
        receive_id: str,
        content: str,
    ) -> Optional[str]:
        """
        发送文本消息

        Args:
            receive_id_type: 接收者 ID 类型，可选值: open_id, user_id, union_id, email, chat_id
            receive_id: 接收者 ID
            content: 消息内容（纯文本）

        Returns:
            消息 ID，发送失败时返回 None

        Raises:
            NotImplementedError: 此方法尚未实现
            ValueError: 参数校验失败
        """
        # 参数校验
        if not receive_id_type:
            raise ValueError("receive_id_type 不能为空")
        if not receive_id:
            raise ValueError("receive_id 不能为空")
        if not content:
            raise ValueError("content 不能为空")

        valid_id_types = {"open_id", "user_id", "union_id", "email", "chat_id"}
        if receive_id_type not in valid_id_types:
            raise ValueError(
                f"receive_id_type 无效，可选值: {', '.join(valid_id_types)}"
            )

        # TODO: 实现消息发送逻辑
        raise NotImplementedError(
            "send_text 方法尚未实现。请参考飞书 SDK 文档实现消息发送功能。"
        )
