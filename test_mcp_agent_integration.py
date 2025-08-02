#!/usr/bin/env python3
"""
测试MCP工具集成到Agent中的功能
"""

import sys
import os
import asyncio
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MCPAgentIntegrationTest:
    """
    MCP Agent集成测试类
    """
    
    def __init__(self):
        self.test_results = []
    
    def test_mcp_client_connection(self) -> bool:
        """测试MCP客户端连接"""
        print("\n1. 测试MCP客户端连接...")
        try:
            from src.mcp.mcp_client import MCPAgentClient
            import asyncio
            
            async def _test_connection():
                client = MCPAgentClient()
                
                # 启动服务器
                if not await client.start_server():
                    return False
                
                # 等待服务器启动
                await asyncio.sleep(3)
                
                # 连接客户端
                if not await client.connect():
                    return False
                
                # 获取工具
                tools = client.get_tool_functions()
                if not tools:
                    print("  ⚠ 未获取到MCP工具")
                    return False
                
                print(f"  ✓ 获取到 {len(tools)} 个MCP工具")
                for tool in tools:
                    print(f"    - {tool.__name__}: {tool.__doc__}")
                
                # 关闭连接
                await client.close()
                return True
            
            # 运行异步测试
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(_test_connection())
                return success
            except Exception as e:
                print(f"  ❌ 异步测试失败: {e}")
                return False
            finally:
                try:
                    loop.close()
                except:
                    pass
                
        except Exception as e:
            print(f"❌ MCP客户端连接测试失败: {e}")
            return False
    
    def test_individual_mcp_tools(self) -> bool:
        """测试单个MCP工具功能"""
        print("\n2. 测试单个MCP工具功能...")
        try:
            from src.mcp import calculate_bmi, fetch_weather, get_mcp_tools_info
            
            # 测试BMI计算
            bmi_result = calculate_bmi(70, 1.75)
            print(f"  ✓ BMI计算: {bmi_result}")
            
            # 测试天气查询
            weather_result = fetch_weather("Beijing")
            print(f"  ✓ 天气查询: {weather_result}")
            
            # 测试工具信息
            tools_info = get_mcp_tools_info()
            print(f"  ✓ 工具信息: {tools_info}")
            
            return True
            
        except Exception as e:
            print(f"❌ 单个MCP工具测试失败: {e}")
            return False
    
    def test_agent_integration(self) -> bool:
        """测试Agent集成"""
        print("\n3. 测试Agent集成...")
        try:
            from src.core import Agent
            from src.tools import get_current_datetime
            from src.mcp import get_mcp_tools_for_agent
            from openai import OpenAI
            
            # 创建OpenAI客户端（使用测试API密钥）
            client = OpenAI(
                api_key="test-key",  # 测试用
                base_url="https://api.siliconflow.cn/v1",
            )
            
            # 获取MCP工具
            mcp_tools = get_mcp_tools_for_agent()
            
            # 创建Agent
            agent = Agent(
                client=client,
                model="Qwen/Qwen2.5-32B-Instruct",
                tools=[get_current_datetime] + mcp_tools,
            )
            
            # 检查工具schema
            tool_schema = agent.get_tool_schema()
            mcp_tool_names = [tool.__name__ for tool in mcp_tools]
            
            print(f"  ✓ Agent创建成功")
            print(f"  ✓ 工具schema包含 {len(tool_schema)} 个工具")
            print(f"  ✓ MCP工具: {mcp_tool_names}")
            
            return True
            
        except Exception as e:
            print(f"❌ Agent集成测试失败: {e}")
            return False
    
    def test_mcp_server_functionality(self) -> bool:
        """测试MCP服务器功能"""
        print("\n4. 测试MCP服务器功能...")
        try:
            import subprocess
            import json
            import time
            
            # 启动MCP服务器
            process = subprocess.Popen(
                [sys.executable, "src/mcp/mcp_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            time.sleep(3)
            
            if process.poll() is None:
                print("  ✓ MCP服务器启动成功")
                
                # 测试HTTP连接
                import httpx
                try:
                    with httpx.Client() as client:
                        response = client.get("http://localhost:8000/mcp")
                        if response.status_code == 200:
                            print("  ✓ MCP服务器HTTP连接正常")
                        else:
                            print(f"  ⚠ MCP服务器HTTP状态码: {response.status_code}")
                except Exception as e:
                    print(f"  ⚠ MCP服务器HTTP连接测试失败: {e}")
                
                # 关闭服务器
                process.terminate()
                process.wait()
                print("  ✓ MCP服务器已关闭")
                return True
            else:
                print("  ❌ MCP服务器启动失败")
                return False
                
        except Exception as e:
            print(f"❌ MCP服务器功能测试失败: {e}")
            return False
    
    def test_tool_schema_generation(self) -> bool:
        """测试工具schema生成"""
        print("\n5. 测试工具schema生成...")
        try:
            from src.utils import function_to_json
            from src.mcp import calculate_bmi, fetch_weather
            
            # 测试BMI工具schema
            bmi_schema = function_to_json(calculate_bmi)
            print(f"  ✓ BMI工具schema: {bmi_schema['function']['name']}")
            
            # 测试天气工具schema
            weather_schema = function_to_json(fetch_weather)
            print(f"  ✓ 天气工具schema: {weather_schema['function']['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 工具schema生成测试失败: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("=== MCP Agent集成测试 ===\n")
        
        tests = [
            ("MCP客户端连接", self.test_mcp_client_connection),
            ("单个MCP工具功能", self.test_individual_mcp_tools),
            ("Agent集成", self.test_agent_integration),
            ("MCP服务器功能", self.test_mcp_server_functionality),
            ("工具schema生成", self.test_tool_schema_generation),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                self.test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name}测试异常: {e}")
                results[test_name] = False
                self.test_results.append((test_name, False))
        
        return results
    
    def print_summary(self):
        """打印测试总结"""
        print("\n=== 测试总结 ===")
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {total - passed}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in self.test_results:
            status = "✓ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
        
        if passed == total:
            print("\n🎉 所有测试通过！MCP工具已成功集成到Agent中。")
        else:
            print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查相关配置。")

def main():
    """主函数"""
    test = MCPAgentIntegrationTest()
    results = test.run_all_tests()
    test.print_summary()
    
    # 返回测试结果
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 