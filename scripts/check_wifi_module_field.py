"""
检查 Wi-Fi Module 字段的详细信息
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.project_client import get_project_client
from src.providers.project.api.field import FieldAPI
from scripts.project_utils import get_project_key_by_name


async def get_work_item_types(client, project_key: str):
    """获取工作项类型"""
    url = f"/open_api/{project_key}/work_item/all-types"
    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
    if data.get("err_code") != 0:
        raise Exception(f"获取工作项类型失败: {data.get('err_msg')}")
    return data.get("data", [])


async def main():
    client = get_project_client()
    field_api = FieldAPI()
    
    project_name = "Project Management"
    work_item_type_name = "项目管理"
    
    print(f"正在查找项目: {project_name}...")
    project_key = await get_project_key_by_name(client, project_name)
    print(f"项目 Key: {project_key}\n")
    
    # 获取工作项类型
    print(f"正在查找工作项类型: {work_item_type_name}...")
    types = await get_work_item_types(client, project_key)
    type_key = None
    for t in types:
        if t.get("name") == work_item_type_name:
            type_key = t.get("type_key")
            break
    
    if not type_key:
        print(f"未找到工作项类型: {work_item_type_name}")
        return
    
    print(f"工作项类型 Key: {type_key}\n")
    
    # 获取所有字段
    print("正在获取字段定义...")
    fields = await field_api.get_all_fields(project_key, type_key)
    
    # 查找 Wi-Fi Module 字段
    wifi_field = None
    for field in fields:
        field_name = field.get("field_name", "")
        field_alias = field.get("field_alias", "")
        if "Wi-Fi Module" in field_name or "Wi-Fi Module" in field_alias or "WiFi" in field_name or "WiFi" in field_alias:
            wifi_field = field
            break
    
    if not wifi_field:
        print("未找到 Wi-Fi Module 字段")
        print("\n所有字段名称:")
        for field in fields:
            print(f"  - {field.get('field_name')} (alias: {field.get('field_alias', '')})")
        return
    
    print("=" * 80)
    print("Wi-Fi Module 字段详细信息:")
    print("=" * 80)
    print(json.dumps(wifi_field, indent=2, ensure_ascii=False))
    
    # 特别关注字段类型和选项结构
    print("\n" + "=" * 80)
    print("关键信息摘要:")
    print("=" * 80)
    print(f"字段名称: {wifi_field.get('field_name')}")
    print(f"字段别名: {wifi_field.get('field_alias', '无')}")
    print(f"字段 Key: {wifi_field.get('field_key')}")
    print(f"字段类型: {wifi_field.get('field_type_key')}")
    
    options = wifi_field.get("options", [])
    print(f"\n选项数量: {len(options)}")
    
    if options:
        print("\n选项列表:")
        for i, opt in enumerate(options[:20], 1):  # 只显示前20个
            label = opt.get("label", "")
            value = opt.get("value", "")
            parent = opt.get("parent", None)
            children = opt.get("children", [])
            
            print(f"  {i}. Label: {label}")
            print(f"     Value: {value}")
            if parent:
                print(f"     Parent: {parent}")
            if children:
                print(f"     Children: {len(children)} 个子选项")
            print()
        
        if len(options) > 20:
            print(f"  ... 还有 {len(options) - 20} 个选项未显示")
    
    # 检查是否有层级结构
    has_hierarchy = any(opt.get("parent") or opt.get("children") for opt in options)
    print(f"\n是否有层级结构: {has_hierarchy}")
    
    # 保存完整字段定义到文件
    output_file = "wifi_module_field.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(wifi_field, f, indent=2, ensure_ascii=False)
    print(f"\n完整字段定义已保存到: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
