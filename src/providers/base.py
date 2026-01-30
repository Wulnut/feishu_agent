"""
Provider 基类定义

所有业务层 Provider 的抽象基类，定义通用接口和能力。
"""

from abc import ABC  # Abstract Base Class - 抽象基类，子类必须继承但不能直接实例化


class Provider(ABC):  # noqa: B024 - 暂无抽象方法，预留扩展
    """
    Provider 抽象基类

    定义所有业务层 Provider 需要遵循的接口契约。

    设计说明：
    - Provider 是业务逻辑层的核心抽象
    - 封装外部 API 调用，提供人性化的接口
    - 子类需要实现具体的业务方法
    """

    @property
    def provider_name(self) -> str:
        """
        Provider 名称，用于日志和调试

        Returns:
            Provider 类名
        """
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.provider_name}>"
