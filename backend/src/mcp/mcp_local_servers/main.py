
import requests
from fastmcp import FastMCP




# NOTE:- Creating MCP Server Instance
mcp = FastMCP("Local MCP Server for first_lexi_ai_agent")


@mcp.tool
async def get_stock_price_tool(symbol: str) -> dict:
    """
    Fetch Latest Stock price for a given symbol (e.g 'AAPL', 'TSLA')
    using the Alpha Vantage URL With API Key.
    """

    stock_price = requests.get(F"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM")
    converted_to_json = stock_price.json()
    converted_to_json["tool_name"] = "get_stock_price_tool"
    
    return converted_to_json

@mcp.tool
async def calculator_tool(first_num: float, second_num: float, operation: str, tool_name: str = "") -> dict:
    """
    Perform a Basic Arithamatic Operation on two numbers.
    Supported Oprations: addition(add), subtraction(sub), multiplication(mul) and division(div).
    """

    if operation in ["add", "addition"]:
        result = first_num + second_num
    elif operation in ["sub", "subtraction"]:
        result = first_num - second_num
    elif operation in ["mul", "division"]:
        result = first_num * second_num
    elif operation in ["div", "division"]:
        if second_num == 0:
            return {"error": "division by zero is not allowed."}
        result = first_num / second_num
    
    return {
        "first_num": first_num,
        "second_num": second_num,
        "operation": operation,
        "result" : result,
        "tool_name": "calculator_tool"
    }


@mcp.tool
async def purchase_stack_tool(symbol: str, quantity: int) -> dict:
    """
    Simulate purchasing a given quantity of a stock symbol.

    NOTE:- This is stock mock implementation:
    - No real brokerage API is called
    - It simply returns a confirmation payload.
    """

    return {
        "status": "success",
        "message": f"Purchase order placed for {quantity} Shares of {symbol}.",
        "symbol": symbol,
        "quantity": quantity,
        "tool_name": "purchase_stack_tool"
    }


if __name__ == "__main__":
    mcp.run()


