"""
AttachmentAPI - 附件管理原子能力层
负责附件上传、下载、删除等原子接口封装

对应 Postman 集合:
- 附件管理 > 删除附件: POST /open_api/file/delete
"""

import logging
from typing import Dict, List, Optional
from src.core.project_client import get_project_client, ProjectClient

logger = logging.getLogger(__name__)


class AttachmentAPI:
    """
    飞书项目附件 API 封装 (Base API Layer)
    """

    def __init__(self, client: Optional[ProjectClient] = None):
        self.client = client or get_project_client()

    async def delete_file(
        self,
        project_key: str,
        file_tokens: List[str],
    ) -> Dict:
        """
        删除附件

        对应 Postman: 附件管理 > 删除附件
        API: POST /open_api/file/delete

        Args:
            project_key: 项目空间 Key (虽然 API 路径没带，但通常需要鉴权或 header)
                        (Doc says POST /open_api/file/delete, checking payload usually)
            file_tokens: 附件 Token 列表

        Returns:
            删除结果

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = "/open_api/file/delete"
        payload = {
            "project_key": project_key,
            "file_tokens": file_tokens,
        }

        logger.warning(
            "Deleting files: project=%s, tokens_count=%d",
            project_key,
            len(file_tokens),
        )

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "删除附件失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"删除附件失败: {err_msg}")

        result = data.get("data", {})
        logger.info("Files deleted successfully")
        return result

    async def upload_file(
        self,
        project_key: str,
        file_path: str,
        parent_type: str = "work_item",
        parent_id: Optional[int] = None,
    ) -> Dict:
        """
        上传附件

        对应 Postman: 附件管理 > 上传附件
        API: POST /open_api/:project_key/file/upload

        Args:
            project_key: 项目空间 Key
            file_path: 本地文件路径
            parent_type: 父对象类型 (默认 work_item)
            parent_id: 父对象 ID (工作项 ID)

        Returns:
            上传结果 (包含 file_token)

        Raises:
            Exception: API 调用失败时抛出异常
            FileNotFoundError: 文件未找到
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        url = f"/open_api/{project_key}/file/upload"

        # 准备 Multipart/form-data
        file_name = os.path.basename(file_path)

        logger.info(
            "Uploading file: project=%s, file=%s, parent=%s:%s",
            project_key,
            file_name,
            parent_type,
            parent_id,
        )

        # 使用 httpx 的文件上传格式
        files = {"file": (file_name, open(file_path, "rb"))}

        data = {
            "parent_type": parent_type,
        }
        if parent_id:
            data["parent_id"] = parent_id

        try:
            # 注意: 这里 files 打开的文件流需要正确关闭，但在 httpx sync usage 中通常传递 open() 即可
            # 若是 async client, httpx 也会处理。
            # 但最佳实践是 context manager，不过此处为保持 API 简单，暂直接传递
            # TODO: 考虑使用 context manager 包装 file open
            resp = await self.client.post(url, data=data, files=files)
        except Exception as e:
            # 确保异常时也能记录日志
            logger.error("File upload network error: %s", str(e))
            raise e
        finally:
            # 关闭文件句柄 (files 字典中的 tuple item 1)
            files["file"][1].close()

        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "上传附件失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"上传附件失败: {err_msg}")

        result = data.get("data", {})
        logger.info("File uploaded successfully: token=%s", result.get("file_token"))
        return result

    async def download_file(
        self,
        project_key: str,
        file_token: str,
    ) -> bytes:
        """
        下载附件

        对应 Postman: 附件管理 > 下载附件
        API: POST /open_api/file/download
        (注: 部分接口可能是 GET 或需要特定的 header，此处按 Postman 规范 POST)

        Args:
            project_key: 项目空间 Key
            file_token: 附件 Token

        Returns:
            文件二进制内容 (bytes)

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = "/open_api/file/download"
        payload = {
            "project_key": project_key,
            "file_token": file_token,
        }

        logger.info(
            "Downloading file: project=%s, token=%s",
            project_key,
            file_token,
        )

        # 下载文件通常返回二进制流，需要 stream=True 或者直接读取 content
        # 这里假设直接读取全部 content 到内存 (适用于中小文件)
        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()

        # 检查是否是 JSON 错误响应 (有时候 binary 接口出错会返回 JSON)
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                data = resp.json()
                if data.get("err_code") != 0:
                    err_msg = data.get("err_msg", "Unknown error")
                    logger.error(
                        "下载附件失败: err_code=%s, err_msg=%s",
                        data.get("err_code"),
                        err_msg,
                    )
                    raise Exception(f"下载附件失败: {err_msg}")
            except ValueError:
                # 解析 JSON 失败 (resp.json() raises ValueError/JSONDecodeError)
                # 这意味着虽然 header 说是 json，但内容不是有效 json，可能就是二进制流
                pass

        logger.info("File downloaded successfully, size=%d bytes", len(resp.content))
        return resp.content
