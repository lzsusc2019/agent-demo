import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m ** 2)


@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    try:
        async with httpx.AsyncClient() as client:
            # 使用模拟的天气API响应，避免实际网络调用
            return f"模拟天气数据: {city} 晴天，温度25°C"
    except Exception as e:
        return f"获取天气信息失败: {str(e)}"

if __name__ == "__main__":
    print("启动MCP服务器...")
    print("使用streamable-http传输协议")
    print("服务器将在 http://localhost:8000/mcp 上运行")
    mcp.run(transport="streamable-http")