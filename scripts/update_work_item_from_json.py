"""
从 JSON 输入更新工作项字段的脚本

用法:
    python scripts/update_work_item_from_json.py

JSON 格式:
{
  "project_name": "Project Management",
  "work_type": "项目管理",
  "work_item": "SR6D2VA-7552-Lark",
  "modify": {
    "Wi-Fi Module": "MTK/MT7668BSN"
  }
}
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.providers.project.work_item_provider import WorkItemProvider


async def update_from_json(json_data: dict) -> None:
    """从 JSON 数据更新工作项"""
    # 解析 JSON 数据
    project_name = json_data.get("project_name")
    work_type = json_data.get("work_type")
    work_item_name = json_data.get("work_item")
    modify_fields = json_data.get("modify", {})

    # 预处理字段值，移除常见的厂商前缀
    processed_fields = {}
    for field_name, field_value in modify_fields.items():
        processed_value = field_value
        if isinstance(field_value, str):
            # 移除常见的厂商前缀，如 "MTK/", "Qualcomm/", "Broadcom/" 等
            prefixes_to_remove = ["MTK/", "Qualcomm/", "Broadcom/", "Realtek/", "Amlogic/"]
            for prefix in prefixes_to_remove:
                if field_value.startswith(prefix):
                    processed_value = field_value[len(prefix):]
                    print(f"⚠️  预处理字段值: '{field_value}' -> '{processed_value}'")
                    break
        processed_fields[field_name] = processed_value

    modify_fields = processed_fields

    if not all([project_name, work_type, work_item_name, modify_fields]):
        raise ValueError("JSON 数据不完整，缺少必要的字段")

    print("📋 解析的更新请求:")
    print(f"   项目: {project_name}")
    print(f"   工作项类型: {work_type}")
    print(f"   工作项名称: {work_item_name}")
    print(f"   更新字段: {modify_fields}")
    print("-" * 60)

    # 创建 Provider
    provider = WorkItemProvider(
        project_name=project_name,
        work_item_type_name=work_type
    )

    # 1. 先搜索工作项，找到ID
    print(f"\n🔍 正在搜索工作项: {work_item_name}...")
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
    print(f"\n🔄 正在更新字段...")
    try:
        await provider.update_issue(
            issue_id=issue_id,
            extra_fields=modify_fields
        )
        print("✅ 更新成功！")
        print(f"   工作项ID: {issue_id}")
        print(f"   更新字段: {modify_fields}")
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("🚀 飞书工作项字段更新工具")
    print("=" * 60)

    # 读取用户输入的 JSON
    print("请输入 JSON 数据（格式参考脚本顶部注释）:")
    print("注意：输入完成后按 Ctrl+D (Linux/Mac) 或 Ctrl+Z+Enter (Windows) 结束输入")
    print("-" * 60)

    try:
        # 从标准输入读取 JSON
        json_lines = []
        for line in sys.stdin:
            json_lines.append(line.strip())
        json_text = '\n'.join(json_lines)

        if not json_text.strip():
            raise ValueError("未接收到输入")

        # 解析 JSON
        json_data = json.loads(json_text)
        print("✅ JSON 解析成功")

        # 执行更新
        await update_from_json(json_data)

    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        print("请检查 JSON 格式是否正确")
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())