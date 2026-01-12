import logging
from typing import Dict, Optional, List, Any
from src.providers.project.api import WorkItemAPI
from src.core.cache import SimpleCache
from src.schemas.project import FieldDefinition

logger = logging.getLogger(__name__)


class FieldMetadataProvider:
    def __init__(self, api_client: Optional[WorkItemAPI] = None):
        self.api = api_client or WorkItemAPI()
        self._cache = SimpleCache(ttl=3600)  # 1 hour TTL

    async def get_field_mappings(self, project_key: str) -> Dict[str, str]:
        """
        Returns a mapping of field_key -> field_name for a project.
        Uses cache if available.
        """
        cache_key = f"fields:{project_key}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        resp = await self.api.get_project_fields(project_key)
        if not resp.is_success or resp.data is None:
            logger.error(
                f"Failed to fetch fields for project {project_key}: {resp.msg}"
            )
            return {}

        # Create mapping: key -> name
        mapping = {f.field_key: f.field_name for f in resp.data}

        # Also store the reverse mapping if needed later, but for now just name
        self._cache.set(cache_key, mapping)
        return mapping

    async def translate_keys(
        self, project_key: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Translates field_xxx keys in a dictionary to human-readable names.
        """
        mappings = await self.get_field_mappings(project_key)
        if not mappings:
            return data

        translated = {}
        for k, v in data.items():
            new_key = mappings.get(k, k)
            translated[new_key] = v
        return translated

    async def get_reverse_mappings(self, project_key: str) -> Dict[str, str]:
        """
        Returns a mapping of field_name -> field_key.
        """
        mappings = await self.get_field_mappings(project_key)
        return {v: k for k, v in mappings.items()}
