
import asyncio, sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Environment Variable Loading
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# LangGraph 
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool




from src.agent.RAG.rag_tool import rag_tool


from src.mcp.mcp_client_initialization import client




# State
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage


# LLM
llm = ChatOpenAI()



@tool
async def get_stock_price_tool(symbol: str) -> dict:
    """
    Fetch latest stock price for a given sumbol (e.g 'AAPL', 'TSLA')
    using the Alpha Vantage URL with API Key.
    """
    try:
      # async with client: # NOTE by using lifespan asynccontextmanager in fastAPI we don't need this continious connection & Disconnection
      stock_price = await client.call_tool("get_stock_price_tool", {"symbol": symbol})
      
      return stock_price

    except Exception as e:
      print(f"error in graph.py purchase stock--{e}")

@tool
async def calculator_tool(first_num: float, second_num: float, operation: str, tool_name: str = "") -> dict:
    """
    Perform a Basic Arithamatic Operation on two numbers.
    Supported Oprations: addition(add), subtraction(sub), multiplication(mul) and division(div).
    """
    
    try:
      # async with client: # NOTE by using lifespan asynccontextmanager in fastAPI we don't need this continious connection & Disconnection
          return await client.call_tool("calculator_tool", {"first_num": first_num, "second_num": second_num, "operation": operation, "tool_name": tool_name})

    except Exception as e:
      print(f"error in graph.py Calculator--{e}")
        

@tool
async def purchase_stack_tool(symbol: str, quantity: int) -> dict:
    """
    Simulate purchasing a given quantity of a stock symbol.

    NOTE:- This is stock mock implementation:
    - No real brokerage API is called
    - It simply returns a confirmation payload.
    """
    
    try:
      # async with client: # NOTE by using lifespan asynccontextmanager in fastAPI we don't need this continious connection & Disconnection
          return await client.call_tool("purchase_stack_tool", {"symbol": symbol, "quantity": quantity})

    except Exception as e:
      print(f"error in graph.py purchase stock--{e}")


# Binding tools
tools = [rag_tool, get_stock_price_tool, calculator_tool, purchase_stack_tool]

llm_with_tools = llm.bind_tools(tools)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# chat_node function
async def chat_node(state: ChatState):
    """
        You are a helpful, friendly, and clear conversational assistant, 
        Please Remember your name is 'Lexi'. DO NOT FORGOT!!

        Your goal is to give the user the right answer, in the right length, in the right tone — every single time.

        RULE 1 — RESPONSE LENGTH:

        Before writing your answer, classify the user's query:

        - SHORT query: a single fact, yes/no, definition, or quick clarification.

          → Respond in 1–3 sentences maximum.

        - LONG query: a how-to, explanation, comparison, or multi-part question.

          → Respond with short paragraphs or a simple numbered list.

        Never pad a short answer. Never cut short a long one.

        RULE 2 — TONE AND EMOTION DETECTION:

        Detect the user's emotional tone before replying:

        - Frustrated or upset     → Be calm, patient, and reassuring. Acknowledge their feeling first.

        - Confused                → Be extra clear, use simple steps, check in at the end.

        - Curious or excited      → Match their energy, be warm and engaged.

        - Urgent                  → Be direct and get to the answer fast.

        - Neutral                 → Be friendly and professional.

        RULE 3 — PLAIN LANGUAGE:

        Always use simple, everyday words.

        - Avoid jargon or complex vocabulary.

        - If a technical word is necessary, explain it in plain words right after.

        - Write as if talking to a smart person who is not an expert on this topic.

        RULE 4 — POLITENESS:

        Be warm, polite, and respectful at all times.

        - Do not use hollow filler phrases like "Great question!" or "Certainly!".

        - If the user is wrong about something, correct them gently.

        - Never be dismissive, rude, or impatient.

        RULE 5 — ACCURACY AND FOCUS:

        Answer only what the user asked — nothing more, nothing less.

        - If the query is unclear, ask one short clarifying question.

        - Do not guess or make things up. If you do not know, say so honestly.

        OUTPUT FORMAT:

        - Short answers: plain text, 1–3 sentences.

        - Long answers: short paragraphs or a simple numbered list.

        - No markdown headers or bold text for short answers.

        - Keep formatting clean and minimal.

    """

    #Accesing messages from state
    messages = state["messages"]

    # Send  that Message to LLM
    # response = llm.invoke(messages) # NOTE this line Needs to use WithOut Tools existed
    response = await llm_with_tools.ainvoke(messages)

    # Store the response in the State
    return { "messages": [response]}

# tool_node function
tool_node = ToolNode(tools) 

async def set_up_memory():
    # intialising the Graph
    graph = StateGraph(ChatState)
    # nodes
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)#NOTE:- Here node name Must be 'tools' Only B/c by default 'tools_condition' Will search for the graph node named 'tools'
    
    # edges
    graph.add_edge(START, "chat_node")
    
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
    
    graph.add_edge("chat_node", END)
    
    # Compile Graph
    compiled_graph  = graph.compile()

    return compiled_graph
    






