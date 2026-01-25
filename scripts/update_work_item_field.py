"""
更新工作项字段的脚本

用法:
    python scripts/update_work_item_field.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.providers.project.work_item_provider import WorkItemProvider


async def main():
    """更新工作项字段"""
    # 从用户输入解析参数
    project_name = "Project Management"
    work_item_type = "项目管理"
    work_item_name = "SR6D2VA-7552-Lark"
    field_name = "Wi-Fi Module"
    field_value = "MTK/MT7668BSN"
    
    print(f"项目: {project_name}")
    print(f"工作项类型: {work_item_type}")
    print(f"工作项名称: {work_item_name}")
    print(f"字段名称: {field_name}")
    print(f"字段值: {field_value}")
    print("-" * 60)
    
    # 创建 Provider
    provider = WorkItemProvider(
        project_name=project_name,
        work_item_type_name=work_item_type
    )
    
    # 1. 先搜索工作项，找到ID
    print(f"\n正在搜索工作项: {work_item_name}...")
    search_result = await provider.get_tasks(
        name_keyword=work_item_name,
        page_num=1,
        page_size=10
    )
    
    items = search_result.get("items", [])
    if not items:
        print(f"❌ 未找到名称为 '{work_item_name}' 的工作项")
        return
    
    # 查找精确匹配的工作项
    target_item = None
    for item in items:
        if item.get("name") == work_item_name:
            target_item = item
            break
    
    # 如果没有精确匹配，使用第一个结果
    if not target_item:
        target_item = items[0]
        print(f"⚠️  未找到精确匹配，使用第一个结果: {target_item.get('name')}")
    
    issue_id = target_item.get("id")
    if not issue_id:
        print("❌ 工作项没有ID")
        return
    
    print(f"✅ 找到工作项: {target_item.get('name')} (ID: {issue_id})")
    
    # 2. 更新字段
    print(f"\n正在更新字段 '{field_name}' 为 '{field_value}'...")
    try:
        await provider.update_issue(
            issue_id=issue_id,
            extra_fields={field_name: field_value}
        )
        print(f"✅ 更新成功！")
        print(f"   工作项ID: {issue_id}")
        print(f"   字段: {field_name} = {field_value}")
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
