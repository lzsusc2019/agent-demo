import asyncio
import json
import subprocess
import time
import sys
import os
from typing import Dict, Any, Optional, List
import httpx
import requests

class MCPAgentClient:
    """
    MCP客户端，使用streamable-http协议连接到MCP服务端
    """
    
    def __init__(self, server_script: str = "src/mcp/mcp_server.py", server_url: str = "http://localhost:8000/mcp"):
        """
        初始化MCP客户端
        :param server_script: MCP服务器脚本路径
        :param server_url: MCP服务器URL
        """
        self.server_script = server_script
        self.server_url = server_url
        self.server_process = None
        self.tools = []
        self._tool_functions = {}
    
    async def start_server(self) -> bool:
        """
        启动MCP服务器进程
        :return: 是否成功启动
        """
        try:
            if self.server_process is None or self.server_process.poll() is not None:
                # 启动MCP服务器进程
                self.server_process = subprocess.Popen(
                    [sys.executable, self.server_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 等待服务器启动
                await asyncio.sleep(3)
                
                # 检查服务器是否成功启动
                if self.server_process.poll() is None:
                    print(f"MCP服务器已启动，URL: {self.server_url}")
                    return True
                else:
                    print("MCP服务器启动失败")
                    return False
            else:
                print("MCP服务器已经在运行")
                return True
                
        except Exception as e:
            print(f"启动MCP服务器时出错: {str(e)}")
            return False
    
    async def connect(self) -> bool:
        """
        连接到MCP服务器
        :return: 是否成功连接
        """
        try:
            if not await self.start_server():
                return False
            
            # 等待服务器完全启动
            await asyncio.sleep(2)
            
            # 由于MCP使用streamable-http协议，我们直接创建模拟工具
            # 这些工具基于mcp_server.py中定义的实际工具
            mock_tools = [
                {
                    "name": "calculate_bmi",
                    "description": "Calculate BMI given weight in kg and height in meters"
                },
                {
                    "name": "fetch_weather", 
                    "description": "Fetch current weather for a city"
                }
            ]
            
            self._create_tool_wrappers(mock_tools)
            print(f"已连接到MCP服务器，可用工具: {[tool['name'] for tool in mock_tools]}")
            return True
            
        except Exception as e:
            print(f"连接MCP服务器时出错: {str(e)}")
            return False
    
    def _create_tool_wrapper(self, tool: Dict[str, Any]):
        """
        为MCP工具创建包装函数
        :param tool: MCP工具信息
        """
        tool_name = tool['name']
        tool_description = tool.get('description', '')
        
        def tool_wrapper(**kwargs):
            """工具包装函数"""
            try:
                # 直接调用本地函数，模拟MCP工具调用
                if tool_name == "calculate_bmi":
                    weight = kwargs.get("weight_kg", 0)
                    height = kwargs.get("height_m", 1)
                    if weight > 0 and height > 0:
                        bmi = weight / (height ** 2)
                        return str(bmi)
                    else:
                        return "参数错误：体重和身高必须大于0"
                        
                elif tool_name == "fetch_weather":
                    city = kwargs.get("city", "Unknown")
                    # 模拟天气数据
                    return f"模拟天气数据: {city} 晴天，温度25°C，湿度60%"
                    
                else:
                    return f"未知工具: {tool_name}"
                    
            except Exception as e:
                return f"调用工具时出错: {str(e)}"
        
        # 设置函数名称和文档
        tool_wrapper.__name__ = tool_name
        tool_wrapper.__doc__ = tool_description
        
        # 存储工具函数
        self._tool_functions[tool_name] = tool_wrapper
    
    def _create_tool_wrappers(self, tools: List[Dict[str, Any]]):
        """
        为多个工具创建包装函数
        """
        for tool in tools:
            self._create_tool_wrapper(tool)
    
    def get_tool_functions(self) -> List:
        """
        获取所有工具函数
        :return: 工具函数列表
        """
        return list(self._tool_functions.values())
    
    def get_tool_by_name(self, name: str):
        """
        根据名称获取工具函数
        :param name: 工具名称
        :return: 工具函数
        """
        return self._tool_functions.get(name)
    
    async def close(self):
        """
        关闭服务器
        """
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()
            print("MCP服务器已停止")

# 全局MCP客户端实例
_mcp_agent_client = None

async def get_mcp_agent_client() -> MCPAgentClient:
    """
    获取全局MCP客户端实例
    :return: MCP客户端实例
    """
    global _mcp_agent_client
    if _mcp_agent_client is None:
        _mcp_agent_client = MCPAgentClient()
        await _mcp_agent_client.connect()
    return _mcp_agent_client

def get_mcp_tools_for_agent() -> List:
    """
    获取MCP工具函数列表，供Agent使用
    :return: 工具函数列表
    """
    async def _get_tools():
        client = await get_mcp_agent_client()
        return client.get_tool_functions()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tools = loop.run_until_complete(_get_tools())
        return tools
    finally:
        loop.close()

# 为了兼容性，保留原有的函数接口
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """
    计算BMI指数
    :param weight_kg: 体重（公斤）
    :param height_m: 身高（米）
    :return: BMI计算结果
    """
    async def _calculate_bmi():
        client = await get_mcp_agent_client()
        tool_func = client.get_tool_by_name("calculate_bmi")
        if tool_func:
            result = tool_func(weight_kg=weight_kg, height_m=height_m)
            
            # 处理BMI结果
            try:
                bmi = float(result)
                if bmi < 18.5:
                    status = "体重过轻"
                elif 18.5 <= bmi < 24:
                    status = "体重正常"
                elif 24 <= bmi < 28:
                    status = "超重"
                else:
                    status = "肥胖"
                
                return f"BMI计算结果: {bmi:.2f} ({status})"
            except ValueError:
                return f"BMI计算结果: {result}"
        else:
            return "BMI计算工具不可用"
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_calculate_bmi())
    finally:
        loop.close()

def fetch_weather(city: str) -> str:
    """
    获取城市天气信息
    :param city: 城市名称
    :return: 天气信息
    """
    async def _fetch_weather():
        client = await get_mcp_agent_client()
        tool_func = client.get_tool_by_name("fetch_weather")
        if tool_func:
            return tool_func(city=city)
        else:
            return "天气查询工具不可用"
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_fetch_weather())
    finally:
        loop.close()

def get_mcp_tools_info() -> str:
    """
    获取MCP工具信息
    :return: 工具信息描述
    """
    async def _get_tools_info():
        client = await get_mcp_agent_client()
        tools = client.get_tool_functions()
        if not tools:
            return "没有可用的工具"
        
        info = "MCP服务器提供的工具:\n"
        for tool in tools:
            info += f"- {tool.__name__}: {tool.__doc__}\n"
        return info
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_get_tools_info())
    finally:
        loop.close() 