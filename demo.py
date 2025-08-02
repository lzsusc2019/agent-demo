from src.core import Agent
from src.tools import add, count_letter_in_string, compare, get_current_datetime, search_wikipedia, get_current_temperature
from src.mcp import get_mcp_tools_for_agent, calculate_bmi, fetch_weather, get_mcp_tools_info

from openai import OpenAI


if __name__ == "__main__":
    client = OpenAI(
        api_key="sk-btdctqegducmsoqbdcchdevgrjotlyoxryqghbhtmkjefgdw",
        base_url="https://api.siliconflow.cn/v1",
    )

    # 获取MCP工具列表
    mcp_tools = get_mcp_tools_for_agent()
    
    # 合并所有工具
    all_tools = [
        get_current_datetime, 
        search_wikipedia, 
        get_current_temperature,
    ] + mcp_tools  # 添加MCP工具

    agent = Agent(
        client=client,
        model="Qwen/Qwen2.5-32B-Instruct",
        tools=all_tools,
    )

    print("\033[93m=== MCP工具已集成到Agent ===\033[0m")
    print("MCP工具列表:")
    for tool in mcp_tools:
        print(f"- {tool.__name__}: {tool.__doc__}")
    print("\033[93m==================\033[0m\n")

    while True:
        # 使用彩色输出区分用户输入和AI回答
        prompt = input("\033[94mUser: \033[0m")  # 蓝色显示用户输入提示
        if prompt == "exit":
            break
        response = agent.get_completion(prompt)
        print("\033[92mAssistant: \033[0m", response)  # 绿色显示AI助手回答
