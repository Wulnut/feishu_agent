"""
Author: liangyz liangyz@seirobotics.net
Date: 2026-01-12 15:48:38
LastEditors: liangyz liangyz@seirobotics.net
LastEditTime: 2026-01-14 12:42:57
FilePath: /feishu_agent/main.py
Description:
    Feishu Agent MCP Server 入口点

    支持两种运行方式：
    1. 直接运行: python main.py
    2. 通过 uv tool install 安装后: lark-agent
"""

from src.mcp_server import main, mcp

if __name__ == "__main__":
    main()
