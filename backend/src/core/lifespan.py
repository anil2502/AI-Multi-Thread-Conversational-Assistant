
import asyncio
import sys
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from src.db.session import init_models

# 1. Windows Fix (Must be at the very top)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()


from src.mcp.mcp_client_initialization import client


from src.agent.graph import set_up_memory

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Starting Application Startup ---")
    await init_models()

    async with client: 
        await client.__aenter__()
        
        compiled_graph = await set_up_memory()
        
        app.state.compiled_graph = compiled_graph

        yield 
        
        await client.__aexit__()
            
