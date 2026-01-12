import logging
from typing import Dict, List, Optional
from src.core.project_client import get_project_client, ProjectClient
from src.core.config import settings

logger = logging.getLogger(__name__)

class MetadataService:
    """
    元数据服务 (Service Layer)
    负责动态获取和缓存 Project Key, Work Item Type Key, Field Key, Option Value
    """
    _instance = None

    def __init__(self, client: Optional[ProjectClient] = None):
        self.client = client or get_project_client()
        self._project_cache: Dict[str, str] = {}  # name -> project_key
        self._type_cache: Dict[str, Dict[str, str]] = {}  # project_key -> {name -> type_key}
        self._field_cache: Dict[str, Dict[str, Dict[str, str]]] = {} # project_key -> type_key -> {name -> field_key}
        self._option_cache: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = {} # project_key -> type_key -> field_key -> {label -> value}
        self._user_cache: Dict[str, str] = {} # identifier(name/email) -> user_key

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    async def get_project_key(self, project_name: str) -> str:
        """根据项目名称获取 Project Key"""
        if project_name in self._project_cache:
            return self._project_cache[project_name]

        # 1. 获取项目列表
        # 注意：这里需要遍历所有项目，或者使用搜索（如果支持）
        # 目前 Open API 获取项目列表 /open_api/projects 仅返回 key list，需要再调详情
        
        # Step 1: Get keys
        url_list = "/open_api/projects"
        payload_list = {
            "user_key": settings.FEISHU_PROJECT_USER_KEY,
            "tenant_group_id": 0 # 默认
        }
        try:
            resp_list = await self.client.post(url_list, json=payload_list)
            resp_list.raise_for_status()
            data_list = resp_list.json()
            if data_list.get("err_code") != 0:
                raise Exception(f"Failed to get project keys: {data_list.get('err_msg')}")
            
            project_keys = data_list.get("data", [])
            if not project_keys:
                raise Exception("No projects found")

            # Step 2: Get details
            url_detail = "/open_api/projects/detail"
            payload_detail = {
                "project_keys": project_keys,
                "user_key": settings.FEISHU_PROJECT_USER_KEY
            }
            resp_detail = await self.client.post(url_detail, json=payload_detail)
            resp_detail.raise_for_status()
            data_detail = resp_detail.json()
            if data_detail.get("err_code") != 0:
                raise Exception(f"Failed to get project details: {data_detail.get('err_msg')}")
            
            projects_map = data_detail.get("data", {})
            for key, info in projects_map.items():
                if isinstance(info, dict):
                    name = info.get("name")
                    if name:
                        self._project_cache[name] = key
                        
            if project_name in self._project_cache:
                return self._project_cache[project_name]
            
            raise Exception(f"Project '{project_name}' not found")

        except Exception as e:
            logger.error(f"Error resolving project key for '{project_name}': {e}")
            raise

    async def get_type_key(self, project_key: str, type_name: str) -> str:
        """根据类型名称获取 Type Key"""
        if project_key not in self._type_cache:
            self._type_cache[project_key] = {}
            
        if type_name in self._type_cache[project_key]:
            return self._type_cache[project_key][type_name]

        # Fetch all types
        url = f"/open_api/{project_key}/work_item/all-types"
        try:
            resp = await self.client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if data.get("err_code") != 0:
                raise Exception(f"Failed to get work item types: {data.get('err_msg')}")
            
            types = data.get("data", [])
            for t in types:
                t_name = t.get("name")
                t_key = t.get("type_key")
                if t_name and t_key:
                    self._type_cache[project_key][t_name] = t_key
            
            if type_name in self._type_cache[project_key]:
                return self._type_cache[project_key][type_name]
            
            raise Exception(f"Work Item Type '{type_name}' not found in project '{project_key}'")

        except Exception as e:
            logger.error(f"Error resolving type key for '{type_name}': {e}")
            raise

    async def _ensure_field_cache(self, project_key: str, type_key: str):
        """加载字段和选项缓存"""
        if project_key not in self._field_cache:
            self._field_cache[project_key] = {}
            self._option_cache[project_key] = {}
            
        if type_key in self._field_cache[project_key]:
            return

        self._field_cache[project_key][type_key] = {}
        self._option_cache[project_key][type_key] = {}

        url = f"/open_api/{project_key}/field/all"
        payload = {"work_item_type_key": type_key}
        try:
            resp = await self.client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if data.get("err_code") != 0:
                raise Exception(f"Failed to get fields: {data.get('err_msg')}")
            
            fields = data.get("data", [])
            for f in fields:
                f_name = f.get("field_name")
                f_key = f.get("field_key")
                f_alias = f.get("field_alias")
                
                if f_name and f_key:
                    # 优先存储 field_name -> field_key
                    self._field_cache[project_key][type_key][f_name] = f_key
                    # 也可以存储 alias
                    if f_alias:
                        self._field_cache[project_key][type_key][f_alias] = f_key
                
                # Cache options
                options = f.get("options", [])
                if options:
                    self._option_cache[project_key][type_key][f_key] = {}
                    for opt in options:
                        label = opt.get("label")
                        value = opt.get("value")
                        if label and value:
                            self._option_cache[project_key][type_key][f_key][label] = value

        except Exception as e:
            logger.error(f"Error loading fields for type '{type_key}': {e}")
            raise

    async def get_field_key(self, project_key: str, type_key: str, field_name: str) -> str:
        """根据字段名称获取 Field Key"""
        await self._ensure_field_cache(project_key, type_key)
        
        field_map = self._field_cache[project_key].get(type_key, {})
        
        # 1. 精确匹配名称
        if field_name in field_map:
            return field_map[field_name]
            
        # 2. 检查是否本身就是 Key (反向查找)
        # 这是一个 O(N) 操作，但在字段数量不多时可以接受
        if field_name in field_map.values():
            return field_name
            
        # 3. 尝试匹配 Alias (已经在缓存里了，如果 alias 存在)
        
        # Log available fields for debugging
        available_fields = list(field_map.keys())
        logger.warning(f"Field '{field_name}' not found. Available fields: {available_fields[:10]}...")
        
        raise Exception(f"Field '{field_name}' not found for type '{type_key}'")

    async def get_option_value(self, project_key: str, type_key: str, field_key: str, option_label: str) -> str:
        """根据选项标签获取 Option Value"""
        await self._ensure_field_cache(project_key, type_key)
        
        option_map = self._option_cache[project_key].get(type_key, {}).get(field_key, {})
        if option_label in option_map:
            return option_map[option_label]
            
        # 也许 option_label 本身就是 value?
        if option_label in option_map.values():
            return option_label
            
        raise Exception(f"Option '{option_label}' not found for field '{field_key}'")

    async def get_user_key(self, identifier: str) -> str:
        """
        获取 User Key (暂时未实现完全，需要调用 User API)
        目前简单返回 identifier，如果它是 user_key 的话
        未来应实现：Identifier(email/name) -> Search -> UserKey
        """
        # TODO: Implement user search API
        return identifier
