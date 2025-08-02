#!/usr/bin/env python3
"""
测试MCP服务器和客户端连接
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_connection():
    """测试MCP连接"""
    print("=== 测试MCP连接 ===\n")
    
    try:
        from src.mcp.mcp_client import MCPAgentClient
        
        # 创建MCP客户端
        client = MCPAgentClient()
        
        # 测试连接
        print("1. 测试MCP服务器启动...")
        success = await client.start_server()
        if success:
            print("✓ MCP服务器启动成功")
        else:
            print("❌ MCP服务器启动失败")
            return False
        
        # 等待服务器启动
        await asyncio.sleep(3)
        
        print("\n2. 测试MCP客户端连接...")
        success = await client.connect()
        if success:
            print("✓ MCP客户端连接成功")
        else:
            print("❌ MCP客户端连接失败")
            return False
        
        # 测试工具获取
        print("\n3. 测试工具获取...")
        tools = client.get_tool_functions()
        print(f"✓ 获取到 {len(tools)} 个工具")
        for tool in tools:
            print(f"  - {tool.__name__}: {tool.__doc__}")
        
        # 测试工具调用
        print("\n4. 测试工具调用...")
        bmi_tool = client.get_tool_by_name("calculate_bmi")
        if bmi_tool:
            result = bmi_tool(weight_kg=70, height_m=1.75)
            print(f"✓ BMI计算: {result}")
        else:
            print("❌ 未找到BMI计算工具")
        
        # 关闭连接
        await client.close()
        
        print("\n=== MCP连接测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1) 